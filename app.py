import os
if 'WAYLAND_DISPLAY' in os.environ:
    os.environ["QT_QPA_PLATFORM"] = "xcb"
import sys
import json
from PyQt5 import QtWidgets, QtCore, QtGui

class LightBulb(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(LightBulb, self).__init__(parent)
        self.setFixedSize(18, 24)  # Adjusted size to be oval
        self.color = QtCore.Qt.black

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # Draw the oval bulb
        painter.setBrush(QtGui.QBrush(self.color))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawEllipse(0, 6, self.width(), self.height() - 6)  # Adjusted to be oval

        gradient = QtGui.QRadialGradient(self.width() / 2, self.height() / 2 + 6, self.width() / 2)
        gradient.setColorAt(0, QtGui.QColor(255, 255, 255, 150))
        gradient.setColorAt(1, QtCore.Qt.transparent)
        painter.setBrush(QtGui.QBrush(gradient))
        painter.drawEllipse(0, 6, self.width(), self.height() - 6)  # Adjusted to be oval

        # Draw the black rectangle on top
        painter.setBrush(QtGui.QBrush(QtCore.Qt.black))
        painter.drawRect(6, 0, 6, 6)  # Rectangle on top to simulate bulb connection

    def set_color(self, color):
        self.color = color
        self.update()

class ChristmasLights(QtWidgets.QWidget):
    def __init__(self):
        super(ChristmasLights, self).__init__()
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint  |
            QtCore.Qt.X11BypassWindowManagerHint
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        screen = QtWidgets.QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        window_width = 800
        window_height = 24
        x = (screen_geometry.width() - window_width) // 2
        y = 0
        self.setGeometry(x, y, window_width, window_height)
        self.lights = [LightBulb(self) for _ in range(20)]
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_lights)
        self.timer.start(500)
        self.dragging = False
        self.drag_position = None

        # Load patterns from JSON
        self.patterns = self.load_patterns()
        self.current_pattern_index = 0
        self.current_shift = 0

        self.pattern_change_timer = QtCore.QTimer(self)
        self.pattern_change_timer.timeout.connect(self.change_pattern)
        self.pattern_change_timer.start(15000)  # Change pattern every 15 seconds

    def load_patterns(self):
        patterns_json = '''
        [
            {"pattern": [0, 1], "interval": 500},
            {"pattern": [0, 1, 2, 3, 4, 3, 2, 1], "interval": 500},
            {"pattern": [2, 2, 3], "interval": 500}
        ]
        '''
        return json.loads(patterns_json)

    def update_lights(self):
        base_pattern = self.patterns[self.current_pattern_index]["pattern"]
        pattern_length = len(base_pattern)
        colors = [
            QtGui.QColor(255, 16, 16, 255), 
            QtGui.QColor(16, 255, 16, 255),
            QtGui.QColor(24, 24, 255, 255),
            QtGui.QColor(255, 255, 16, 255),
            QtGui.QColor(24, 255, 255, 255),
        ]
        for i, light in enumerate(self.lights):
            pattern_index = (self.current_shift + i) % pattern_length
            light.set_color(colors[base_pattern[pattern_index]])
        self.current_shift = (self.current_shift + 1) % pattern_length

    def change_pattern(self):
        self.current_pattern_index = (self.current_pattern_index + 1) % len(self.patterns)
        self.current_shift = 0

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            QtWidgets.qApp.quit()
        elif event.button() == QtCore.Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(event.globalPos() - self.drag_position)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.dragging = False

    def paintEvent(self, event):
        for i, light in enumerate(self.lights):
            light.move(i * 40, 0)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    lights = ChristmasLights()
    lights.show()
    sys.exit(app.exec_())