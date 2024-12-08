from PyQt5.QtWidgets import QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import sys

app = QApplication(sys.argv)
view = QWebEngineView()

# Test HTML
test_html = """
<!DOCTYPE html>
<html>
<body>
<p>Testing image rendering:</p>
<img src="file:///home/jamie/Programming/venv_Python/jmd_editor/images/tux.png" alt="Test Image" />
</body>
</html>
"""

view.setHtml(test_html, QUrl("file:///home/jamie/Programming/venv_Python/jmd_editor/"))
view.show()
sys.exit(app.exec_())
