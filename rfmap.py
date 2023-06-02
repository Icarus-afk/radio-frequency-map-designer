from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsRectItem, QInputDialog, QColorDialog
from PyQt5.QtGui import QColor, QPen, QBrush
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

    def mousePressEvent(self, event):
        if self.rf_spectrum_rect.contains(event.pos()):
            service_name, ok = QInputDialog.getText(self, "Add RF Service", "Service Name:")
            if ok and service_name:
                start, ok1 = QInputDialog.getDouble(self, "Add RF Service", "Start Frequency:")
                if ok1:
                    end, ok2 = QInputDialog.getDouble(self, "Add RF Service", "End Frequency:")
                    if ok2:
                        color = QColorDialog.getColor()
                        if color.isValid():
                            service = RFService(service_name, start, end, color)
                            self.rf_services.append(service)
                            self.update_rf_map()

        super().mousePressEvent(event)

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
            self.rf_map_scene.addSimpleText(service.name).setPos(service_rect.x(), service_rect.y() + service_rect.height() + 5)

    def resizeEvent(self, event):
        self.rf_map_scene.setSceneRect(0, 0, self.rf_spectrum_rect.width() + 100, self.rf_spectrum_rect.height() + 100)
        super().resizeEvent(event)


if __name__ == "__main__":
    app = QApplication([])
    rf_allocation_table = RFAllocationTable()
    rf_allocation_table.show()
    app.exec_()
