import sys
import signal
import qdarktheme
from PySide6.QtWidgets import QApplication
from nvt.gui import SystemTray
from nvt import log_config

log_config.config()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)
    qss = """
    QPushButton {
        padding: 8px;
    }
    QListWidget::item {
        padding-top: 4px;
        padding-bottom: 4px;
    }
    QListWidget::item:hover {
        padding-top: 4px;
        padding-bottom: 4px;
    }
    """
    qdarktheme.setup_theme('dark', corner_shape="sharp", custom_colors={"primary": "#67e8f9"}, additional_qss=qss)
    app.setQuitOnLastWindowClosed(False)

    trayIcon = SystemTray(None)
    trayIcon.show()

    sys.exit(app.exec())
