from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel


class ErrorRow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.icon = QLabel()
        self.icon.setPixmap(QIcon.fromTheme('dialog-error').pixmap(16, 16))
        self.icon.setVisible(False)
        self.label = QLabel('')
        self.label.setVisible(False)

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.icon)
        layout.addWidget(self.label)
        self.setLayout(layout)

    def set_msg(self, msg: str):
        self.label.setText(msg)
        self.icon.setVisible(True)
        self.label.setVisible(True)

    def clear(self):
        self.label.setText('')
        self.icon.setVisible(False)
        self.label.setVisible(False)
