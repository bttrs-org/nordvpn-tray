from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel

from nvt.utils import svg_icon


class ErrorRow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVisible(False)
        self.icon = QLabel()
        self.icon.setPixmap(svg_icon('error').pixmap(24, 24))
        self.label = QLabel('')

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.icon)
        layout.addWidget(self.label)
        self.setLayout(layout)

    def set_msg(self, msg: str):
        self.label.setText(msg)
        self.setVisible(True)

    def clear(self):
        self.label.setText('')
        self.setVisible(False)
