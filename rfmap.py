import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsRectItem, \
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QAction, QFileDialog, QColorDialog, QToolTip
from PyQt5.QtGui import QColor, QPen, QBrush, QFont, QPainter, QPixmap
from PyQt5.QtCore import Qt, QRectF, QPoint
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

        self.setWindowTitle("National Radio Frequency Allocation Table")
        self.setGeometry(100, 100, 800, 600)

        self.rf_map_scene = QGraphicsScene(self)
        self.rf_map_view = CustomGraphicsView(self.rf_map_scene)
        self.setCentralWidget(self.rf_map_view)

        self.rf_spectrum_rect = QRectF(50, 50, 700, 300)
        self.rf_map_scene.setSceneRect(0, 0, self.rf_spectrum_rect.width() + 100,
                                       self.rf_spectrum_rect.height() + 100)
        self.rf_map_view.setScene(self.rf_map_scene)

        self.rf_services = []

        self.input_widget = QWidget()
        self.input_layout = QVBoxLayout()
        self.input_widget.setLayout(self.input_layout)

        self.service_name_label = QLabel("Service Name:")
        self.service_name_edit = QLineEdit()
        self.input_layout.addWidget(self.service_name_label)
        self.input_layout.addWidget(self.service_name_edit)

        self.start_frequency_label = QLabel("Start Frequency:")
        self.start_frequency_edit = QLineEdit()
        self.input_layout.addWidget(self.start_frequency_label)
        self.input_layout.addWidget(self.start_frequency_edit)

        self.end_frequency_label = QLabel("End Frequency:")
        self.end_frequency_edit = QLineEdit()
        self.input_layout.addWidget(self.end_frequency_label)
        self.input_layout.addWidget(self.end_frequency_edit)

        self.add_service_button = QPushButton("Add Service")
        self.add_service_button.clicked.connect(self.add_service)
        self.input_layout.addWidget(self.add_service_button)

        self.input_layout.addStretch()

        self.input_widget.setMaximumWidth(200)
        toolbar = self.addToolBar("Input Fields")
        toolbar.setFixedWidth(200)
        toolbar.setMovable(False)
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

    def create_menus(self):
        file_menu = self.menuBar().addMenu("File")
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.load_action)
        file_menu.addAction(self.export_image_action)
        file_menu.addAction(self.print_action)

    def add_service(self):
        service_name = self.service_name_edit.text()
        start_frequency = float(self.start_frequency_edit.text())
        end_frequency = float(self.end_frequency_edit.text())

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

        for service in self.rf_services:
            normalized_start = (service.start - self.rf_spectrum_rect.x()) / self.rf_spectrum_rect.width()
            normalized_end = (service.end - self.rf_spectrum_rect.x()) / self.rf_spectrum_rect.width()
            box_width = (normalized_end - normalized_start) * self.rf_spectrum_rect.width()

            service_rect = QGraphicsRectItem(
                self.rf_spectrum_rect.x() + normalized_start * self.rf_spectrum_rect.width(),
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
                    if (service.end >= existing_service.start and service.start <= existing_service.end) or \
                            (service.start <= existing_service.end and service.end >= existing_service.start):
                        overlapping_services.append(existing_service)

            if overlapping_services:
                num_overlapping = len(overlapping_services) + 1
                box_height = self.rf_spectrum_rect.height() / num_overlapping
                box_y = self.rf_spectrum_rect.y() + box_height

                for overlapping_service in overlapping_services:
                    overlapping_normalized_start = (
                            overlapping_service.start - self.rf_spectrum_rect.x()) / self.rf_spectrum_rect.width()
                    overlapping_normalized_end = (
                            overlapping_service.end - self.rf_spectrum_rect.x()) / self.rf_spectrum_rect.width()
                    overlapping_box_width = (
                            overlapping_normalized_end - overlapping_normalized_start) * self.rf_spectrum_rect.width()

                    overlapping_service_rect = QGraphicsRectItem(
                        self.rf_spectrum_rect.x() + overlapping_normalized_start * self.rf_spectrum_rect.width(),
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
        self.rf_map_scene.setSceneRect(0, 0, self.rf_spectrum_rect.width() + 100,
                                       self.rf_spectrum_rect.height() + 100)
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
        selected_items = self.rf_map_scene.selectedItems()
        if len(selected_items) > 0:
            item = selected_items[0]
            index = self.rf_map_scene.items().index(item)
            service = self.rf_services[index]
            self.service_name_edit.setText(service.name)
            self.start_frequency_edit.setText(str(service.start))
            self.end_frequency_edit.setText(str(service.end))
            color = QColorDialog.getColor(service.color)
            if color.isValid():
                service.color = color
            self.update_rf_map()

    def delete_service(self):
        selected_items = self.rf_map_scene.selectedItems()
        if len(selected_items) > 0:
            item = selected_items[0]
            index = self.rf_map_scene.items().index(item)
            self.rf_services.pop(index)
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


class CustomGraphicsView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        position = event.pos()
        tooltip_text = ""
        for item in self.scene().items():
            if isinstance(item, QGraphicsRectItem) and item.rect().contains(position):
                tooltip_text = item.toolTip()
                break
        QToolTip.showText(event.globalPos(), tooltip_text, self)


if __name__ == "__main__":
    app = QApplication([])
    rf_allocation_table = RFAllocationTable()
    rf_allocation_table.show()
    app.exec()
