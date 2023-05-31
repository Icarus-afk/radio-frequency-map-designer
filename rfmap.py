from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsRectItem, QInputDialog, QColorDialog, QComboBox
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

    def mousePressEvent(self, event):
        if self.rf_spectrum_rect.contains(event.pos()):
            service_name, ok = QInputDialog.getText(self, "Add RF Service", "Service Name:")
            if ok and service_name:
                frequency_unit_combo = QComboBox()
                frequency_unit_combo.addItem("kHz")
                frequency_unit_combo.addItem("MHz")
                frequency_unit_combo.addItem("GHz")
                frequency_unit_combo.setCurrentIndex(1)

                start, ok1 = QInputDialog.getDouble(self, "Add RF Service", "Start Frequency:", decimals=3)
                if ok1:
                    frequency_unit_dialog = QInputDialog()
                    frequency_unit_dialog.setComboBoxItems(["kHz", "MHz", "GHz"])
                    frequency_unit_dialog.setWindowTitle("Add RF Service")
                    frequency_unit_dialog.setLabelText("Select Frequency Unit:")
                    frequency_unit_index = frequency_unit_dialog.exec_()
                    if frequency_unit_index != -1:
                        frequency_unit = frequency_unit_combo.itemText(frequency_unit_index)

                        end, ok2 = QInputDialog.getDouble(self, "Add RF Service", "End Frequency:", decimals=3)
                        if ok2:
                            color = QColorDialog.getColor()
                            if color.isValid():
                                service = RFService(service_name, start, end, color)
                                self.rf_services.append(service)
                                self.update_rf_map()

        super().mousePressEvent(event)

    def update_rf_map(self):
        self.rf_map_scene.clear()

        services_by_bandwidth = {}
        for service in self.rf_services:
            bandwidth = service.end - service.start
            if bandwidth not in services_by_bandwidth:
                services_by_bandwidth[bandwidth] = []
            services_by_bandwidth[bandwidth].append(service)

        box_height = self.rf_spectrum_rect.height() / len(services_by_bandwidth)

        for bandwidth, services in services_by_bandwidth.items():
            normalized_start = (services[0].start - self.rf_spectrum_rect.x()) / self.rf_spectrum_rect.width()
            normalized_end = (services[0].end - self.rf_spectrum_rect.x()) / self.rf_spectrum_rect.width()
            box_width = (normalized_end - normalized_start) * self.rf_spectrum_rect.width()

            for i, service in enumerate(services):
                service_rect = QRectF(
                    self.rf_spectrum_rect.x() + normalized_start * self.rf_spectrum_rect.width(),
                    self.rf_spectrum_rect.y() + i * box_height,
                    box_width,
                    box_height
                )

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
