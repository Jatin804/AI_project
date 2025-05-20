import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout
)
from PyQt5.QtGui import QMovie, QPixmap, QFont
from PyQt5.QtCore import Qt

class SystemAIGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SYSTEMAI Desktop Assistant")
        self.setGeometry(100, 100, 1000, 600)
        self.setStyleSheet("background-color: #121212; color: white;")
        self.init_ui()

    def init_ui(self):
        # === GIF/Image Label ===
        self.gif_label = QLabel()
        self.gif_label.setFixedSize(600, 600)
        self.gif_label.setStyleSheet(
            "border: 2px solid #00FFFF; border-radius: 10px;"
        )

        # Load assets
        self.blank_image = QPixmap(r"black_image_600x600.png")
        self.movie = QMovie(r"gif_main.gif")
        self.movie.setScaledSize(self.gif_label.size())  # Ensure GIF fits area
        self.set_idle_state()

        # === Version / Details ===
        version_label = QLabel("SYSTEMAI\nVersion: 3.0.1\nStatus: Ready")
        version_label.setFont(QFont("Consolas", 10))
        version_label.setAlignment(Qt.AlignTop)
        version_label.setStyleSheet(
            "border: 1px solid #00FFFF; padding: 10px; border-radius: 5px; background-color: #1e1e1e;"
        )

        # === Buttons ===
        start_btn = QPushButton("▶ Start")
        stop_btn = QPushButton("■ Stop")

        button_style = """
            QPushButton {
                background-color: #0d7377;
                color: white;
                border: 1px solid #14ffec;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #14ffec;
                color: #0d1b2a;
            }
        """

        start_btn.setStyleSheet(button_style)
        stop_btn.setStyleSheet(button_style)
        start_btn.setFixedWidth(120)
        stop_btn.setFixedWidth(120)

        button_layout = QHBoxLayout()
        button_layout.addWidget(start_btn)
        button_layout.addWidget(stop_btn)

        # === Output Box ===
        self.output_box = QTextEdit()
        self.output_box.setPlaceholderText("Text outputs of code...")
        self.output_box.setReadOnly(True)
        self.output_box.setFont(QFont("Courier", 10))
        self.output_box.setStyleSheet(
            "background-color: #1e1e1e; color: #14ffec; border-radius: 8px; padding: 8px;"
        )

        # === Right Layout ===
        right_layout = QVBoxLayout()
        right_layout.addWidget(version_label)
        right_layout.addSpacing(10)
        right_layout.addLayout(button_layout)
        right_layout.addSpacing(10)
        right_layout.addWidget(self.output_box)

        # === Main Layout ===
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.gif_label)
        main_layout.addLayout(right_layout)
        self.setLayout(main_layout)

        # === Signals ===
        start_btn.clicked.connect(self.start_system_ai)
        stop_btn.clicked.connect(self.stop_system_ai)

    def set_idle_state(self):
        self.movie.stop()
        scaled_pixmap = self.blank_image.scaled(
            self.gif_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.gif_label.setPixmap(scaled_pixmap)

    def start_system_ai(self):
        self.gif_label.setMovie(self.movie)
        self.movie.start()
        self.output_box.append("[+] SYSTEMAI started...")

    def stop_system_ai(self):
        self.movie.stop()
        self.set_idle_state()
        self.output_box.append("[-] SYSTEMAI stopped.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SystemAIGUI()
    window.show()
    sys.exit(app.exec_())

