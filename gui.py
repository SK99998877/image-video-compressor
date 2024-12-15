import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QLabel, QProgressBar, QTableWidget, QTableWidgetItem, QComboBox, QSlider, QCheckBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from image_compressor import compress_image
from video_compressor import compress_video


class CompressionThread(QThread):
    progress_signal = pyqtSignal(int, str, int, int, float)

    def __init__(self, files, output_dir, compress_function, quality):
        super().__init__()
        self.files = files
        self.output_dir = output_dir
        self.compress_function = compress_function
        self.quality = quality

    def run(self):
        for i, file in enumerate(self.files):
            output_path = os.path.join(self.output_dir, f"compressed_{os.path.basename(file)}")
            before_size = os.path.getsize(file) // 1024
            self.compress_function(file, output_path, self.quality)
            after_size = os.path.getsize(output_path) // 1024
            saved_percent = ((before_size - after_size) / before_size) * 100 if before_size > 0 else 0
            self.progress_signal.emit(i + 1, os.path.basename(file), before_size, after_size, saved_percent)


class ModernCompressorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Advanced Compressor")
        self.setGeometry(300, 100, 800, 600)
        layout = QVBoxLayout()

        # Header
        self.header = QLabel("Advanced Image & Video Compressor")
        self.header.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.header)

        # Buttons Layout
        buttons_layout = QHBoxLayout()
        self.single_image_btn = QPushButton("Single Image")
        self.single_image_btn.clicked.connect(self.compress_single_image)

        self.batch_image_btn = QPushButton("Batch Images")
        self.batch_image_btn.clicked.connect(self.compress_batch_images)

        self.single_video_btn = QPushButton("Single Video")
        self.single_video_btn.clicked.connect(self.compress_single_video)

        self.batch_video_btn = QPushButton("Batch Videos")
        self.batch_video_btn.clicked.connect(self.compress_batch_videos)

        buttons_layout.addWidget(self.single_image_btn)
        buttons_layout.addWidget(self.batch_image_btn)
        buttons_layout.addWidget(self.single_video_btn)
        buttons_layout.addWidget(self.batch_video_btn)
        layout.addLayout(buttons_layout)

        # Compression Level Slider
        self.slider_label = QLabel("Compression Level (%): 85")
        layout.addWidget(self.slider_label)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(50)
        self.slider.setMaximum(100)
        self.slider.setValue(85)
        self.slider.valueChanged.connect(self.update_slider_label)
        layout.addWidget(self.slider)

        # Progress Bar
        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)

        # Table for Stats
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["File", "Before (KB)", "After (KB)", "Saved (%)"])
        layout.addWidget(self.table)

        # Reset Button
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_fields)
        layout.addWidget(self.reset_button)

        # Dark Mode Check
        self.dark_mode = QCheckBox("Enable Dark Mode")
        self.dark_mode.stateChanged.connect(self.toggle_dark_mode)
        layout.addWidget(self.dark_mode)

        self.setLayout(layout)

    def update_slider_label(self, value):
        self.slider_label.setText(f"Compression Level (%): {value}")

    def toggle_dark_mode(self):
        if self.dark_mode.isChecked():
            self.setStyleSheet("background-color: #2E2E2E; color: white;")
            self.table.setStyleSheet("color: white;")
        else:
            self.setStyleSheet("")
            self.table.setStyleSheet("")

    def reset_fields(self):
        self.progress_bar.setValue(0)
        self.table.setRowCount(0)

    def update_table(self, filename, before, after, saved):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        self.table.setItem(row_position, 0, QTableWidgetItem(filename))
        self.table.setItem(row_position, 1, QTableWidgetItem(str(before)))
        self.table.setItem(row_position, 2, QTableWidgetItem(str(after)))
        self.table.setItem(row_position, 3, QTableWidgetItem(f"{saved:.2f}%"))

    def compress_single_image(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.jpg *.jpeg *.png)")
        if file:
            output_format = "jpg"
            output_path, _ = QFileDialog.getSaveFileName(self, "Save Compressed Image", "", f"{output_format.upper()} Files (*.{output_format})")
            if output_path:
                before_size = os.path.getsize(file) // 1024
                if compress_image(file, output_path, quality=self.slider.value()):
                   after_size = os.path.getsize(output_path) // 1024
                   saved_percent = ((before_size - after_size) / before_size) * 100 if before_size > after_size else 0
                   self.update_table(os.path.basename(file), before_size, after_size, saved_percent)
                   self.progress_bar.setValue(100)
            else:
                   print("image compression failed!")    

    def compress_single_video(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Video", "", "Video Files (*.mp4 *.avi *.mkv)")
        if file:
            output_path, _ = QFileDialog.getSaveFileName(self, "Save Compressed Video", "", "*.mp4")
            if output_path:
                before_size = os.path.getsize(file) // 1024
                compress_video(file, output_path, crf=23)
                after_size = os.path.getsize(output_path) // 1024
                saved_percent = ((before_size - after_size) / before_size) * 100 if before_size > after_size else 0
                self.update_table(os.path.basename(file), before_size, after_size, saved_percent)
                self.progress_bar.setValue(100)

    def compress_batch_images(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Images", "", "Image Files (*.jpg *.jpeg *.png)")
        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if files and output_dir:
            self.start_thread(files, output_dir, compress_image)

    def compress_batch_videos(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Videos", "", "Video Files (*.mp4 *.avi *.mkv)")
        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if files and output_dir:
            self.start_thread(files, output_dir, compress_video)

    def start_thread(self, files, output_dir, function):
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(len(files))
        self.thread = CompressionThread(files, output_dir, function, self.slider.value())
        self.thread.progress_signal.connect(self.update_progress)
        self.thread.start()

    def update_progress(self, value, filename, before_size, after_size, saved_percent):
        self.progress_bar.setValue(value)
        self.update_table(filename, before_size, after_size, saved_percent)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernCompressorApp()
    window.show()
    sys.exit(app.exec_())
