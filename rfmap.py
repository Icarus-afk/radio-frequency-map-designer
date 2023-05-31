from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsRectItem, QInputDialog, QColorDialog, QComboBox, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtGui import QColor, QPen, QBrush
from PyQt5.QtCore import Qt, QRectF

class RFService:
    def __init__(self, name, start, end, color):
        self.name = name
        self.start = start
        self.end = end
        self.color = color

class RFMapDesigner(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RF Map Designer")
        self.setGeometry(100, 100, 800, 400)

        self.rf_map_scene = QGraphicsScene(self)
        self.rf_map_view = QGraphicsView(self.rf_map_scene)
        self.setCentralWidget(self.rf_map_view)

        self.rf_spectrum_rect = QRectF(50, 50, 700, 300)
        self.rf_map_scene.setSceneRect(0, 0, self.rf_spectrum_rect.width() + 100, self.rf_spectrum_rect.height() + 100)
        self.rf_map_view.setScene(self.rf_map_scene)

        self.rf_services = []

        self.init_sidebar()

        self.full_spectrum_rect = self.rf_map_scene.addRect(self.rf_spectrum_rect, QPen(Qt.black), QBrush(Qt.white))

    def init_sidebar(self):
        sidebar = QWidget()
        sidebar.setMaximumWidth(200)

        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        sidebar.setLayout(sidebar_layout)

        service_name_label = QLabel("Service Name:")
        self.service_name_input = QLineEdit()

        start_freq_label = QLabel("Start Frequency:")
        self.start_freq_input = QLineEdit()
        self.start_freq_unit_combo = QComboBox()
        self.start_freq_unit_combo.addItem("kHz")
        self.start_freq_unit_combo.addItem("MHz")
        self.start_freq_unit_combo.addItem("GHz")

        end_freq_label = QLabel("End Frequency:")
        self.end_freq_input = QLineEdit()
        self.end_freq_unit_combo = QComboBox()
        self.end_freq_unit_combo.addItem("kHz")
        self.end_freq_unit_combo.addItem("MHz")
        self.end_freq_unit_combo.addItem("GHz")

        color_button = QPushButton("Select Color")
        color_button.clicked.connect(self.select_color)

        add_button = QPushButton("Add Service")
        add_button.clicked.connect(self.add_service)

        sidebar_layout.addWidget(service_name_label)
        sidebar_layout.addWidget(self.service_name_input)
        sidebar_layout.addWidget(start_freq_label)

        start_freq_layout = QHBoxLayout()
        start_freq_layout.addWidget(self.start_freq_input)
        start_freq_layout.addWidget(self.start_freq_unit_combo)
        sidebar_layout.addLayout(start_freq_layout)

        sidebar_layout.addWidget(end_freq_label)

        end_freq_layout = QHBoxLayout()
        end_freq_layout.addWidget(self.end_freq_input)
        end_freq_layout.addWidget(self.end_freq_unit_combo)
        sidebar_layout.addLayout(end_freq_layout)

        sidebar_layout.addWidget(color_button)
        sidebar_layout.addWidget(add_button)

        main_layout = QHBoxLayout()
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.rf_map_view)

        main_widget = QWidget()
        main_widget.setLayout(main_layout)

        self.setCentralWidget(main_widget)

    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.selected_color = color

    def add_service(self):
        service_name = self.service_name_input.text()
        start_freq = float(self.start_freq_input.text())
        end_freq = float(self.end_freq_input.text())
        start_freq_unit = self.start_freq_unit_combo.currentText()
        end_freq_unit = self.end_freq_unit_combo.currentText()

        if start_freq >= end_freq or start_freq < 0 or end_freq > 3000000000:
            return

        start_freq, end_freq = self.convert_frequency(start_freq, end_freq, start_freq_unit, end_freq_unit)

        if self.selected_color:
            service = RFService(service_name, start_freq, end_freq, self.selected_color)
            self.rf_services.append(service)
            self.update_rf_map()

        self.service_name_input.clear()
        self.start_freq_input.clear()
        self.end_freq_input.clear()

    def convert_frequency(self, start_freq, end_freq, start_freq_unit, end_freq_unit):
        if start_freq_unit == "kHz":
            start_freq *= 1000
        elif start_freq_unit == "MHz":
            start_freq *= 1000000
        elif start_freq_unit == "GHz":
            start_freq *= 1000000000

        if end_freq_unit == "kHz":
            end_freq *= 1000
        elif end_freq_unit == "MHz":
            end_freq *= 1000000
        elif end_freq_unit == "GHz":
            end_freq *= 1000000000

        return start_freq, end_freq

    def update_rf_map(self):
        self.rf_map_scene.clear()

        # Add the full spectrum box
        self.rf_map_scene.addRect(self.rf_spectrum_rect, QPen(Qt.black), QBrush(Qt.white))

        for service in self.rf_services:
            start_freq = service.start
            end_freq = service.end

            # Calculate the position of the box within the spectrum
            start_x = self.rf_spectrum_rect.x() + (start_freq / 3000000000) * self.rf_spectrum_rect.width()
            end_x = self.rf_spectrum_rect.x() + (end_freq / 3000000000) * self.rf_spectrum_rect.width()
            width = end_x - start_x

            # Check if there is any overlapping box in the current position
            overlapping = False
            for existing_service in self.rf_services:
                if existing_service != service:
                    existing_start_x = self.rf_spectrum_rect.x() + (existing_service.start / 3000000000) * self.rf_spectrum_rect.width()
                    existing_end_x = self.rf_spectrum_rect.x() + (existing_service.end / 3000000000) * self.rf_spectrum_rect.width()

                    # If there is overlap, adjust the starting position of the new box
                    if existing_end_x >= start_x >= existing_start_x:
                        start_x = existing_end_x  # Place the new box adjacent to the existing box
                        width = end_x - start_x
                        overlapping = True
                        break

            service_rect = QRectF(start_x, self.rf_spectrum_rect.y(), width, self.rf_spectrum_rect.height())

            pen = QPen(Qt.black)
            brush = QBrush(service.color)

            self.rf_map_scene.addRect(service_rect, pen, brush)
            self.rf_map_scene.addSimpleText(service.name).setPos(service_rect.x(), service_rect.y() + service_rect.height() + 5)


    def resizeEvent(self, event):
        self.rf_map_scene.setSceneRect(0, 0, self.rf_spectrum_rect.width() + 100, self.rf_spectrum_rect.height() + 100)
        super().resizeEvent(event)


if __name__ == "__main__":
    app = QApplication([])
    rf_map_designer = RFMapDesigner()
    rf_map_designer.show()
    app.exec_()
