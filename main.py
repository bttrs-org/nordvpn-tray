import sys
import signal
from PySide6.QtWidgets import QApplication
from nvt.gui import SystemTrayIcon
from nvt import log_config

log_config.config()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setStyleSheet("""
    QPushButton {
        padding: 8px;
    }
    QListWidget::item {
        padding: 5px;
    }
    """)

    trayIcon = SystemTrayIcon(None)
    trayIcon.show()

    sys.exit(app.exec())
