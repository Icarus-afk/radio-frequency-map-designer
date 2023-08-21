import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsRectItem, \
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QAction, QFileDialog, QColorDialog, QToolTip, QScrollBar, QComboBox
from PyQt5.QtGui import QColor, QPen, QBrush, QFont, QPainter, QPixmap, QPalette
from PyQt5.QtCore import Qt, QRectF, QPoint, QPointF
from PyQt5 import QtPrintSupport


class RFService:
    def __init__(self, name, start, end, color):
        self.name = name
        self.start = start
        self.end = end
        self.color = color


class RFAllocationTable(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set the application palette
        palette = QPalette()
        palette.setColor(QPalette.Window, Qt.white)
        palette.setColor(QPalette.WindowText, Qt.black)
        self.setPalette(palette)

        self.setWindowTitle("National Radio Frequency Allocation Table")
        self.setGeometry(100, 100, 1000, 6000)

        self.rf_map_scene = QGraphicsScene(self)
        self.rf_map_view = CustomGraphicsView(self.rf_map_scene)
        self.setCentralWidget(self.rf_map_view)

        self.rf_spectrum_rect = QRectF(3, 0, 300000000, 300)        
        self.rf_map_scene.setSceneRect(0, 0, 100, self.rf_spectrum_rect.height() +10 )

        self.rf_map_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.rf_map_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.rf_map_view.setScene(self.rf_map_scene)
        self.rf_map_view.setSceneRect(self.rf_map_scene.sceneRect())

        self.rf_services = []

        self.input_widget = QWidget()
        self.input_layout = QVBoxLayout()
        self.input_widget.setLayout(self.input_layout)

        self.service_name_label = QLabel("Service Name:")
        self.service_name_edit = QLineEdit()
        self.frequency_units = ["KHz", "MHz", "GHz"]
        self.start_frequency_label = QLabel("Start Frequency:")
        self.start_frequency_edit = QLineEdit()
        self.start_frequency_unit_combo = QComboBox()
        self.start_frequency_unit_combo.addItems(self.frequency_units)

        self.end_frequency_label = QLabel("End Frequency:")
        self.end_frequency_edit = QLineEdit()
        self.end_frequency_unit_combo = QComboBox()
        self.end_frequency_unit_combo.addItems(self.frequency_units)
        
        self.add_service_button = QPushButton("Add Service")
        self.add_service_button.clicked.connect(self.add_service)

        self.input_layout.addWidget(self.service_name_label)
        self.input_layout.addWidget(self.service_name_edit)
        self.input_layout.addWidget(self.start_frequency_label)
        self.input_layout.addWidget(self.start_frequency_edit)
        self.input_layout.addWidget(self.start_frequency_unit_combo)
        self.input_layout.addWidget(self.end_frequency_label)
        self.input_layout.addWidget(self.end_frequency_edit)
        self.input_layout.addWidget(self.end_frequency_unit_combo)
        self.input_layout.addWidget(self.add_service_button)

        self.input_widget.setMaximumWidth(200)
        toolbar = self.addToolBar("Input Fields")
        toolbar.setFixedWidth(200)
        toolbar.setMovable(True)
        toolbar.addWidget(self.input_widget)

        self.edit_service_action = QAction("Edit Service", self)
        self.edit_service_action.triggered.connect(self.edit_service)
        self.delete_service_action = QAction("Delete Service", self)
        self.delete_service_action.triggered.connect(self.delete_service)
        self.save_action = QAction("Save", self)
        self.save_action.triggered.connect(self.save_file)
        self.load_action = QAction("Load", self)
        self.load_action.triggered.connect(self.load_file)
        self.export_image_action = QAction("Export Image", self)
        self.export_image_action.triggered.connect(self.export_image)
        self.print_action = QAction("Print", self)
        self.print_action.triggered.connect(self.print_table)

        self.create_menus()

        # Enable tool tips
        QToolTip.setFont(QFont("Arial", 10))
        self.rf_map_view.setMouseTracking(True)
        self.rf_map_view.viewport().setMouseTracking(True)

        self.selected_service_index = -1

    def create_menus(self):
        # Set the stylesheet for the menu bar
        self.menuBar().setStyleSheet(
            """
            QMenuBar {
                background-color: #f2f2f2;
                color: #000000;
                font-weight: bold;
            }
            QMenuBar::item {
                background-color: transparent;
            }
            QMenuBar::item:selected {
                background-color: #dddddd;
            }
            """
        )

        file_menu = self.menuBar().addMenu("File")
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.load_action)
        file_menu.addAction(self.export_image_action)
        file_menu.addAction(self.print_action)

        edit_menu = self.menuBar().addMenu("Edit")
        edit_menu.addAction(self.edit_service_action)
        edit_menu.addAction(self.delete_service_action)


    def add_service(self):
        service_name = self.service_name_edit.text()
        start_frequency = float(self.start_frequency_edit.text())
        end_frequency = float(self.end_frequency_edit.text())

        start_frequency_unit = self.start_frequency_unit_combo.currentText()
        end_frequency_unit = self.end_frequency_unit_combo.currentText()

        if start_frequency_unit == "KHz":
            start_frequency *= 1  # Convert KHz to Hz
        elif start_frequency_unit == "MHz":
            start_frequency *= 1000  # Convert MHz to Hz
        elif start_frequency_unit == "GHz":
            start_frequency *= 1000000  # Convert GHz to Hz

        if end_frequency_unit == "KHz":
            end_frequency *= 1
        elif end_frequency_unit == "MHz":
            end_frequency *= 1000
        elif end_frequency_unit == "GHz":
            end_frequency *= 1000000
            
        color = QColorDialog.getColor()
        if color.isValid():
            service_color = color
        else:
            service_color = QColor(255, 0, 0)  # Predefined color (red)

        if service_name and start_frequency and end_frequency:
            service = RFService(service_name, start_frequency, end_frequency, service_color)
            self.rf_services.append(service)
            self.update_rf_map()

    def update_rf_map(self):
        self.rf_map_scene.clear()

        rf_spectrum_width = self.rf_spectrum_rect.width()

        for service in self.rf_services:
            normalized_start = (service.start - self.rf_spectrum_rect.x()) / rf_spectrum_width
            normalized_end = (service.end - self.rf_spectrum_rect.x()) / rf_spectrum_width
            box_width = (normalized_end - normalized_start) * rf_spectrum_width * 4 # Adjust the scaling factor as needed

            service_rect = QGraphicsRectItem(
                self.rf_spectrum_rect.x() + normalized_start * rf_spectrum_width,
                self.rf_spectrum_rect.y(),
                box_width,
                self.rf_spectrum_rect.height()
            )
            service_rect.setPen(QPen(Qt.black))
            service_rect.setBrush(QBrush(service.color))
            self.rf_map_scene.addItem(service_rect)

            text_item = self.rf_map_scene.addSimpleText(service.name)
            text_item.setPos(service_rect.rect().topLeft() + QPoint(5, 5))
            text_item.setFont(QFont("Arial", 8))

            # Add tooltip for each service
            tooltip_text = f"Name: {service.name}\nStart Frequency: {service.start}\nEnd Frequency: {service.end}"
            service_rect.setToolTip(tooltip_text)

            overlapping_services = []
            for existing_service in self.rf_services:
                if existing_service != service:
                    # Check if there is overlap with existing services
                    overlap_threshold = 0.001
                    if (service.end >= existing_service.start + overlap_threshold and 
                        service.start <= existing_service.end - overlap_threshold) or \
                       (service.start <= existing_service.end - overlap_threshold and 
                        service.end >= existing_service.start + overlap_threshold):
                        overlapping_services.append(existing_service)


            if overlapping_services:
                num_overlapping = len(overlapping_services) + 1
                box_height = self.rf_spectrum_rect.height() / num_overlapping
                box_y = self.rf_spectrum_rect.y() + box_height

                for overlapping_service in overlapping_services:
                    overlapping_normalized_start = (
                            overlapping_service.start - self.rf_spectrum_rect.x()) / rf_spectrum_width
                    overlapping_normalized_end = (
                            overlapping_service.end - self.rf_spectrum_rect.x()) / rf_spectrum_width
                    overlapping_box_width = (
                            overlapping_normalized_end - overlapping_normalized_start) * rf_spectrum_width

                    overlapping_service_rect = QGraphicsRectItem(
                        self.rf_spectrum_rect.x() + overlapping_normalized_start * rf_spectrum_width,
                        box_y,
                        overlapping_box_width,
                        box_height
                    )
                    overlapping_service_rect.setPen(QPen(Qt.black))
                    overlapping_service_rect.setBrush(QBrush(overlapping_service.color))
                    self.rf_map_scene.addItem(overlapping_service_rect)

                    text_item = self.rf_map_scene.addSimpleText(overlapping_service.name)
                    text_item.setPos(overlapping_service_rect.rect().topLeft() + QPoint(5, 5))
                    text_item.setFont(QFont("Arial", 8))

                    # Add tooltip for each overlapping service
                    tooltip_text = f"Name: {overlapping_service.name}\nStart Frequency: {overlapping_service.start}\nEnd Frequency: {overlapping_service.end}"
                    overlapping_service_rect.setToolTip(tooltip_text)

                    box_y += box_height

    def resizeEvent(self, event):
        self.rf_map_scene.setSceneRect(0, 0, 400000, self.rf_spectrum_rect.height() + 100)
        self.rf_map_view.setSceneRect(self.rf_map_scene.sceneRect())
        super().resizeEvent(event)

    def save_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "radio map (*.rfmap)")
        if file_path:
            if not file_path.endswith(".rfmap"):
                file_path += ".rfmap"
            data = {
                "services": [
                    {
                        "name": service.name,
                        "start": service.start,
                        "end": service.end,
                        "color": service.color.name()
                    }
                    for service in self.rf_services
                ]
            }
            with open(file_path, "w") as file:
                json.dump(data, file)

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load File", "", "radio map (*.rfmap)")
        if file_path:
            with open(file_path, "r") as file:
                data = json.load(file)
                self.rf_services = []
                for service_data in data["services"]:
                    name = service_data["name"]
                    start = service_data["start"]
                    end = service_data["end"]
                    color = QColor(service_data["color"])
                    service = RFService(name, start, end, color)
                    self.rf_services.append(service)
                self.update_rf_map()

    def edit_service(self):
        if self.selected_service_index != -1:
            service = self.rf_services[self.selected_service_index]
            service.name = self.service_name_edit.text()
            service.start = float(self.start_frequency_edit.text())
            service.end = float(self.end_frequency_edit.text())

            start_frequency_unit = self.start_frequency_unit_combo.currentText()
            end_frequency_unit = self.end_frequency_unit_combo.currentText()

            if start_frequency_unit == "KHz":
                service.start *= 1  # Convert KHz to Hz
            elif start_frequency_unit == "MHz":
                service.start *= 1000  # Convert MHz to Hz
            elif start_frequency_unit == "GHz":
                service.start *= 1000000  # Convert GHz to Hz

            if end_frequency_unit == "KHz":
                service.end *= 1
            elif end_frequency_unit == "MHz":
                service.end *= 1000
            elif end_frequency_unit == "GHz":
                service.end *= 1000000

            color = QColorDialog.getColor(service.color)
            if color.isValid():
                service.color = color

            self.update_rf_map()

    def delete_service(self):
        if self.selected_service_index != -1:
            self.rf_services.pop(self.selected_service_index)
            self.selected_service_index = -1
            self.clear_input_fields()
            self.update_rf_map()

    def export_image(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Image", "", "PNG (*.png);;JPEG (*.jpg *.jpeg)")
        if file_path:
            pixmap = self.rf_map_view.grab()
            pixmap.save(file_path)

    def print_table(self):
        printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)
        dialog = QtPrintSupport.QPrintDialog(printer, self)
        if dialog.exec() == QtPrintSupport.QPrintDialog.Accepted:
            painter = QPainter(printer)
            painter.setRenderHint(QPainter.Antialiasing)
            self.rf_map_view.render(painter)
            painter.end()

    def clear_input_fields(self):
        self.service_name_edit.clear()
        self.start_frequency_edit.clear()
        self.end_frequency_edit.clear()

    def update_input_fields(self):
        if self.selected_service_index != -1:
            service = self.rf_services[self.selected_service_index]
            self.service_name_edit.setText(service.name)
            self.start_frequency_edit.setText(str(service.start))
            self.end_frequency_edit.setText(str(service.end))

    def item_selection_changed(self):
        selected_items = self.rf_map_scene.selectedItems()
        if len(selected_items) > 0:
            item = selected_items[0]
            index = self.rf_map_scene.items().index(item)
            self.selected_service_index = index
            self.update_input_fields()
        else:
            self.selected_service_index = -1
            self.clear_input_fields()

    def wheelEvent(self, event):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            # Enable zooming when holding the Ctrl key and scrolling
            zoom_factor = 1.05 if event.angleDelta().y() > 0 else 0.95  # Adjust the zoom factor as desired
            self.rf_map_view.scale(zoom_factor, zoom_factor)
        else:
            # Perform default vertical scrolling
            super().wheelEvent(event)


class CustomGraphicsView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setMouseTracking(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)

    def wheelEvent(self, event):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            # Enable horizontal scrolling when holding the Ctrl key and scrolling
            delta = event.angleDelta().y() / 120
            scroll_value = int(delta * 20)  # Convert scroll_value to an integer
            self.scroll(scroll_value, 0)
        else:
            # Perform default vertical scrolling
            super().wheelEvent(event)


if __name__ == "__main__":
    app = QApplication([])
    rf_allocation_table = RFAllocationTable()

    # Set the stylesheet for the input fields, buttons, and scene view
    rf_allocation_table.service_name_edit.setStyleSheet(
        """
        QLineEdit {
            border: 1px solid #999999;
            padding: 5px;
        }
        """
    )
    rf_allocation_table.start_frequency_edit.setStyleSheet(
        """
        QLineEdit {
            border: 1px solid #999999;
            padding: 5px;
        }
        """
    )
    rf_allocation_table.end_frequency_edit.setStyleSheet(
        """
        QLineEdit {
            border: 1px solid #999999;
            padding: 5px;
        }
        """
    )
    rf_allocation_table.add_service_button.setStyleSheet(
        """
        QPushButton {
            background-color: #0088cc;
            color: #ffffff;
            border: none;
            padding: 8px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #005580;
        }
        """
    )
    rf_allocation_table.rf_map_view.setStyleSheet(
        """
        QGraphicsView {
            border: 1px solid #999999;
        }
        """
    )

    rf_allocation_table.show()
    app.exec()