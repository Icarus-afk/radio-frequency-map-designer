from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsRectItem, QInputDialog, QColorDialog, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtGui import QColor, QPen, QBrush, QFont
from PyQt5.QtCore import Qt, QRectF


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
        self.rf_map_view = QGraphicsView(self.rf_map_scene)
        self.setCentralWidget(self.rf_map_view)

        self.rf_spectrum_rect = QRectF(50, 50, 700, 300)
        self.rf_map_scene.setSceneRect(0, 0, self.rf_spectrum_rect.width() + 100, self.rf_spectrum_rect.height() + 100)
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
        self.color_button = QPushButton("Select Color")
        self.color_button.clicked.connect(self.select_color)
        self.input_layout.addWidget(self.color_button)
        self.input_layout.addWidget(self.add_service_button)

        self.input_layout.addStretch()

        self.input_widget.setMaximumWidth(200)
        toolbar = self.addToolBar("Input Fields")
        toolbar.setFixedWidth(200)
        toolbar.setMovable(False)
        toolbar.addWidget(self.input_widget)

    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.selected_color = color

    def add_service(self):
        service_name = self.service_name_edit.text()
        start_frequency = float(self.start_frequency_edit.text())
        end_frequency = float(self.end_frequency_edit.text())
        color = QColorDialog.getColor()

        if service_name and start_frequency and end_frequency and color.isValid():
            service = RFService(service_name, start_frequency, end_frequency, color)
            self.rf_services.append(service)
            self.update_rf_map()

    def update_rf_map(self):
        self.rf_map_scene.clear()

        for service in self.rf_services:
            normalized_start = (service.start - self.rf_spectrum_rect.x()) / self.rf_spectrum_rect.width()
            normalized_end = (service.end - self.rf_spectrum_rect.x()) / self.rf_spectrum_rect.width()
            box_width = (normalized_end - normalized_start) * self.rf_spectrum_rect.width()

            service_rect = QRectF(
                self.rf_spectrum_rect.x() + normalized_start * self.rf_spectrum_rect.width(),
                self.rf_spectrum_rect.y(),
                box_width,
                self.rf_spectrum_rect.height()
            )

            pen = QPen(Qt.black)
            brush = QBrush(service.color)

            self.rf_map_scene.addRect(service_rect, pen, brush)

            text_item = self.rf_map_scene.addSimpleText(service.name)
            text_item.setPos(service_rect.x() + 5, service_rect.y() + 5)
            text_item.setFont(QFont("Arial", 8))

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
                    overlapping_normalized_start = (overlapping_service.start - self.rf_spectrum_rect.x()) / self.rf_spectrum_rect.width()
                    overlapping_normalized_end = (overlapping_service.end - self.rf_spectrum_rect.x()) / self.rf_spectrum_rect.width()
                    overlapping_box_width = (overlapping_normalized_end - overlapping_normalized_start) * self.rf_spectrum_rect.width()

                    overlapping_service_rect = QRectF(
                        self.rf_spectrum_rect.x() + overlapping_normalized_start * self.rf_spectrum_rect.width(),
                        box_y,
                        overlapping_box_width,
                        box_height
                    )

                    pen = QPen(Qt.black)
                    brush = QBrush(overlapping_service.color)

                    self.rf_map_scene.addRect(overlapping_service_rect, pen, brush)

                    text_item = self.rf_map_scene.addSimpleText(overlapping_service.name)
                    text_item.setPos(overlapping_service_rect.x() + 5, overlapping_service_rect.y() + 5)
                    text_item.setFont(QFont("Arial", 8))

                    box_y += box_height

    def resizeEvent(self, event):
        self.rf_map_scene.setSceneRect(0, 0, self.rf_spectrum_rect.width() + 100, self.rf_spectrum_rect.height() + 100)
        super().resizeEvent(event)


if __name__ == "__main__":
    app = QApplication([])
    rf_allocation_table = RFAllocationTable()
    rf_allocation_table.show()
    app.exec_()
