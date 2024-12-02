import sys
from PySide6.QtWidgets import QApplication
from gui import MainWindow

app = QApplication(sys.argv)
video_path = sys.argv[1] if len(sys.argv) > 1 else None
window = MainWindow(app, video_path)
window.show()
sys.exit(app.exec())