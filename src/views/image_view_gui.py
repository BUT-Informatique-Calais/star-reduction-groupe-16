"""
PyQt6 GUI component for astronomical image processing application.

Handles:
- FITS file selection via file explorer
- PNG image display
- Image characteristics display (below image)
- File information and result paths

Layout:
- Top: Filename | Open FITS | Close APP
- Middle: Image display
- Below: Stars detected count
- Below: Result files (2 rows with separator)
"""

from pathlib import Path
from typing import Optional, List, Tuple
from datetime import datetime

import cv2 as cv
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QFrame, QScrollArea,
    QSizePolicy, QProgressBar, QMessageBox
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QObject
from PyQt6.QtGui import QPixmap, QImage, QFont, QIcon, QFontDatabase

# Import existing model classes and controller
from ..models import ImageModel
from ..controllers import PipelineController


class ImageViewGraphic(QMainWindow):
    """
    PyQt6 GUI window for astronomical image processing.

    Layout:
    - Top: Filename | Open FITS | Close APP
    - Middle: PNG image display
    - Below: Stars detected count
    - Below: Result files (2 rows with separator)
    """

    # Custom signals
    processing_started = pyqtSignal()
    processing_finished = pyqtSignal()
    stars_updated = pyqtSignal(int)
    results_updated = pyqtSignal(list)

    def __init__(
        self,
        results_dir: str = "./results",
        parent: Optional[QWidget] = None
    ):
        """
        Initializes the GUI window.

        Args:
            results_dir: Directory for result images
            parent: Parent widget
        """
        super().__init__(parent)
        self.results_dir = Path(results_dir)
        self.image_model: Optional[ImageModel] = None
        self.num_stars: int = 0
        self.current_displayed_image: str = "original.png"  # Track currently displayed image
        
        # Tutorial state variables
        self.tutorial_active: bool = False
        self.tutorial_step: int = 0
        self._setup_ui()
        self._setup_styles()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Sets up the UI components and layout"""
        self.setWindowTitle("SAE Astro - Image Processing")
        self.setMinimumSize(800, 700)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # === Top Bar ===
        top_bar = QWidget()
        top_bar.setObjectName("topBar")
        top_bar.setFixedHeight(50)
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(10, 5, 10, 5)

        # File info label
        self.file_label = QLabel("No file selected")
        self.file_label.setObjectName("fileLabel")
        top_layout.addWidget(self.file_label, alignment=Qt.AlignmentFlag.AlignLeft)

        # Spacer
        top_layout.addStretch()

        # Buttons
        self.tuto_button = QPushButton("Tuto")
        self.tuto_button.setObjectName("tutoButton")
        self.tuto_button.clicked.connect(self._on_tuto_clicked)
        top_layout.addWidget(self.tuto_button, alignment=Qt.AlignmentFlag.AlignRight)

        self.open_button = QPushButton("Open FITS")
        self.open_button.setObjectName("openButton")
        self.open_button.clicked.connect(self._on_open_fits)
        top_layout.addWidget(self.open_button, alignment=Qt.AlignmentFlag.AlignRight)

        self.close_button = QPushButton("Close APP")
        self.close_button.setObjectName("closeButton")
        self.close_button.clicked.connect(self.close)
        top_layout.addWidget(self.close_button, alignment=Qt.AlignmentFlag.AlignRight)

        main_layout.addWidget(top_bar)

        # === Progress Bar ===
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progressBar")
        self.progress_bar.setRange(0, 5)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.setContentsMargins(20, 0, 20, 0)
        main_layout.addWidget(self.progress_bar)

        # === Content Area ===
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(10)

        # === Image Display ===
        image_container = QWidget()
        image_container.setObjectName("imageContainer")
        image_layout = QVBoxLayout(image_container)
        image_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll area for image
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setObjectName("imageScrollArea")

        # Image label
        self.image_label = QLabel()
        self.image_label.setObjectName("imageLabel")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(400, 300)
        self.image_label.setText("No image loaded")
        self.image_label.setStyleSheet("""
            QLabel#imageLabel {
                background-color: #1a1a2e;
                border: 2px dashed #4a4a6a;
                border-radius: 5px;
                color: #888;
                font-size: 16px;
            }
        """)
        scroll_area.setWidget(self.image_label)
        image_layout.addWidget(scroll_area)

        content_layout.addWidget(image_container)

        # === Stars Detected Section ===
        stars_widget = QWidget()
        stars_widget.setObjectName("starsWidget")
        stars_layout = QHBoxLayout(stars_widget)
        stars_layout.setContentsMargins(0, 0, 0, 0)

        stars_title = QLabel("Stars detected:")
        stars_title.setObjectName("infoTitle")
        stars_layout.addWidget(stars_title, alignment=Qt.AlignmentFlag.AlignCenter)

        self.stars_count = QLabel("--")
        self.stars_count.setObjectName("starsCount")
        stars_layout.addWidget(self.stars_count, alignment=Qt.AlignmentFlag.AlignCenter)

        stars_layout.addStretch()

        content_layout.addWidget(stars_widget)

        # === Separator Line ===
        separator = QFrame()
        separator.setObjectName("separator")
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        content_layout.addWidget(separator)

        # === Result Files Section ===
        results_widget = QWidget()
        results_widget.setObjectName("resultsWidget")
        results_layout = QVBoxLayout(results_widget)
        results_layout.setContentsMargins(0, 0, 0, 0)
        results_layout.setSpacing(5)

        results_title = QLabel("Result files:")
        results_title.setObjectName("infoTitle")
        results_layout.addWidget(results_title)

        # Row 1: first 3 result files
        row1_widget = QWidget()
        row1_layout = QHBoxLayout(row1_widget)
        row1_layout.setContentsMargins(0, 0, 0, 0)
        row1_layout.setSpacing(10)

        self.result_labels: List[QLabel] = []
        result_files = [
            "original.png",
            "starmask.png",
            "eroded.png",
        ]

        for filename in result_files:
            label = self._create_result_label(filename)
            row1_layout.addWidget(label)
            self.result_labels.append(label)

        results_layout.addWidget(row1_widget)

        # Separator line between rows
        row_separator = QFrame()
        row_separator.setObjectName("rowSeparator")
        row_separator.setFrameShape(QFrame.Shape.HLine)
        row_separator.setFrameShadow(QFrame.Shadow.Sunken)
        results_layout.addWidget(row_separator)

        # Row 2: last 3 result files
        row2_widget = QWidget()
        row2_layout = QHBoxLayout(row2_widget)
        row2_layout.setContentsMargins(0, 0, 0, 0)
        row2_layout.setSpacing(10)

        result_files_row2 = [
            "selective_eroded.png",
            "smooth_mask.png",
            "difference.png",
        ]

        for filename in result_files_row2:
            label = self._create_result_label(filename)
            row2_layout.addWidget(label)
            self.result_labels.append(label)

        results_layout.addWidget(row2_widget)

        content_layout.addWidget(results_widget)

        # === Timestamp ===
        timestamp_widget = QWidget()
        timestamp_layout = QHBoxLayout(timestamp_widget)
        timestamp_layout.setContentsMargins(0, 0, 0, 0)

        timestamp_layout.addStretch()

        self.timestamp_label = QLabel()
        self.timestamp_label.setObjectName("timestampLabel")
        timestamp_layout.addWidget(self.timestamp_label)

        content_layout.addWidget(timestamp_widget)

        main_layout.addWidget(content_widget)

    def _create_result_label(self, filename: str) -> QLabel:
        """
        Creates a styled clickable result file label.

        Args:
            filename: The filename to display

        Returns:
            QLabel with filename that is clickable
        """
        label = QLabel(filename)
        label.setObjectName("resultLabel")
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        # Enable mouse tracking and cursor change for click feedback
        label.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Store the filename as a property
        label.setProperty("filename", filename)
        label.setProperty("clickable", True)
        
        # Connect click event
        label.mousePressEvent = lambda event, f=filename: self._on_result_clicked(f)
        
        return label

    def _setup_styles(self) -> None:
        """Applies custom styles to the UI"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0f0f1a;
            }
            QWidget#topBar {
                background-color: #1a1a2e;
                border-bottom: 1px solid #2a2a4a;
            }
            QLabel#fileLabel {
                color: #e0e0e0;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton {
                background-color: #3a3a5a;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                font-size: 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #4a4a7a;
            }
            QPushButton#tutoButton {
                background-color: #3a5a7a;
            }
            QPushButton#tutoButton:hover {
                background-color: #4a7a9a;
            }
            QPushButton#closeButton {
                background-color: #5a3a3a;
            }
            QPushButton#closeButton:hover {
                background-color: #7a4a4a;
            }
            QProgressBar {
                background-color: #1a1a2e;
                border: 1px solid #2a2a4a;
                border-radius: 4px;
                text-align: center;
                color: #ffffff;
            }
            QProgressBar::chunk {
                background-color: #4a7a4a;
                border-radius: 2px;
            }
            QWidget#starsWidget {
                background-color: #12121f;
                border: 1px solid #2a2a4a;
                border-radius: 5px;
                padding: 10px;
            }
            QWidget#resultsWidget {
                background-color: #12121f;
                border: 1px solid #2a2a4a;
                border-radius: 5px;
                padding: 10px;
            }
            QLabel#infoTitle {
                color: #a0a0c0;
                font-size: 12px;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            QLabel#starsCount {
                color: #60d060;
                font-size: 28px;
                font-weight: bold;
                font-style: italic;
            }
            QLabel#resultLabel {
                color: #8080a0;
                font-size: 12px;
                font-style: italic;
                padding: 2px 0px;
            }
            QLabel#resultLabel[clickable="true"] {
                color: #9090b0;
            }
            QLabel#resultLabel[clickable="true"]:hover {
                color: #b0b0d0;
                text-decoration: underline;
            }
            QLabel#resultLabel[selected="true"] {
                color: #60d060;
                text-decoration: underline;
                font-weight: bold;
            }
            QLabel#timestampLabel {
                color: #505070;
                font-size: 10px;
            }
            QFrame#separator, QFrame#rowSeparator {
                color: #2a2a4a;
            }
            QScrollArea#imageScrollArea {
                background-color: transparent;
                border: none;
            }
        """)

    def _connect_signals(self) -> None:
        """Connects custom signals to handlers"""
        self.stars_updated.connect(self._on_stars_updated)
        self.results_updated.connect(self._on_results_updated)
        self.processing_started.connect(self._on_processing_started)
        self.processing_finished.connect(self._on_processing_finished)

    def _on_open_fits(self) -> None:
        """Opens file dialog to select a FITS file"""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Select FITS File")
        file_dialog.setNameFilters(["FITS files (*.fits *.fit)", "All files (*)"])
        file_dialog.setDirectory(str(Path("./examples").absolute()))

        if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
            fits_path = file_dialog.selectedFiles()[0]
            self.load_fits(fits_path)

    def load_fits(self, fits_path: str) -> bool:
        """
        Loads a FITS file and runs the processing pipeline.

        Args:
            fits_path: Path to the FITS file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Update file label
            self.file_label.setText(Path(fits_path).name)

            # Print loaded message
            print(f"Loaded: {Path(fits_path).name}")

            # Run the pipeline with the FITS file
            self._run_pipeline(fits_path)

            return True

        except Exception as e:
            print(f"Error loading FITS file: {e}")
            return False

    def _run_pipeline(self, fits_path: str) -> None:
        """
        Runs the image processing pipeline.

        Args:
            fits_path: Path to the FITS file to process
        """
        def on_progress(step: int, message: str) -> None:
            """Progress callback"""
            self.progress_bar.setValue(step + 1)

        def on_stars_detected(num_stars: int) -> None:
            """Stars count callback"""
            self.stars_updated.emit(num_stars)

        def on_results_ready(paths: List[str]) -> None:
            """Results ready callback"""
            self.results_updated.emit(paths)

        # Create controller with callbacks
        controller = PipelineController(
            on_stars_detected=on_stars_detected,
            on_results_ready=on_results_ready,
            on_progress=on_progress
        )

        # Update config with custom results directory
        from ..models.config import Config
        controller.config.RESULTS_DIR = self.results_dir

        # Emit processing started signal
        self.processing_started.emit()

        # Run the pipeline
        self.image_model = controller.run_with_fits_path(Path(fits_path))

        # Display the image
        self._display_image()

        # Emit processing finished signal
        self.processing_finished.emit()

    def _on_processing_started(self) -> None:
        """Handles processing started signal"""
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Processing...")
        self.setCursor(Qt.CursorShape.WaitCursor)
        self.open_button.setEnabled(False)

    def _on_processing_finished(self) -> None:
        """Handles processing finished signal"""
        self.progress_bar.setValue(5)
        self.progress_bar.setFormat("Done!")
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.open_button.setEnabled(True)

        # Update timestamp
        self._update_timestamp()

    def _on_stars_updated(self, num_stars: int) -> None:
        """Handles star count update"""
        self.num_stars = num_stars
        self.stars_count.setText(str(num_stars))

    def _on_results_updated(self, paths: List[str]) -> None:
        """Handles result paths update"""
        for i, label in enumerate(self.result_labels):
            if i < len(paths):
                path = Path(paths[i])
                label.setText(f"• {path.name}")
                label.setToolTip(str(path))
            else:
                label.setText("")
        
        # Set original.png as selected by default and display it
        self.current_displayed_image = "original.png"
        self._update_result_labels_selection()
        self._display_image("original.png")
        
        # Trigger tutorial step 2 if tutorial is active
        if self.tutorial_active and self.tutorial_step == 1:
            self.tutorial_step = 2
            # Use singleShot to show popup after UI has updated
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(100, self._show_tuto_step_2)

    def _display_image(self, filename: str = "original.png") -> None:
        """
        Displays the specified PNG image in the image label.

        Args:
            filename: The filename of the image to display (default: "original.png")
        """
        image_path = self.results_dir / filename
        
        if not image_path.exists():
            return

        # Read the image with OpenCV
        image = cv.imread(str(image_path))
        
        if image is None:
            return

        # Convert BGR to RGB for display
        if len(image.shape) == 3 and image.shape[2] == 3:
            image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

        # Convert to QImage
        h, w = image.shape[:2] if image.ndim == 2 else image.shape[:2]
        bytes_per_line = image.shape[2] * 1 if image.ndim == 3 else 1

        q_image = QImage(
            image.tobytes(),
            w, h,
            bytes_per_line * w,
            QImage.Format.Format_RGB888 if image.ndim == 3 else QImage.Format.Format_Grayscale8
        )

        # Scale to fit while maintaining aspect ratio
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(
            self.image_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.setText("")
        
        # Update the current displayed image and refresh labels
        self.current_displayed_image = filename
        self._update_result_labels_selection()

    def _on_result_clicked(self, filename: str) -> None:
        """
        Handles click on a result file label.

        Args:
            filename: The filename of the clicked result
        """
        # Security check: if no FITS file is loaded, show tutorial
        if self.image_model is None:
            self._on_tuto_clicked()
            return
        self._display_image(filename)

    def _on_tuto_clicked(self) -> None:
        """Handles the Tuto button click - starts the tutorial"""
        self.tutorial_active = True
        self.tutorial_step = 1
        self._show_tuto_step_1()

    def _show_tuto_step_1(self) -> None:
        """Shows step 1 of the tutorial: instruct user to open FITS file"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Tutoriel - Étape 1")
        msg.setText("Cliquez sur le bouton 'Open FITS' pour charger un fichier FITS")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def _show_tuto_step_2(self) -> None:
        """Shows step 2 of the tutorial: explain the loaded image"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Tutoriel - Étape 2")
        msg.setText(
            "Vous avez l'image chargée sous forme de PNG du fichier .FITS au centre.\n\n"
            "Le nombre d'étoiles détectées est affiché en dessous.\n\n"
            "Les fichiers générés par rapport au fichier FITS chargé sont listés plus bas."
        )
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
        
        # After user clicks OK, show step 3
        self._show_tuto_step_3()

    def _show_tuto_step_3(self) -> None:
        """Shows step 3 of the tutorial: explain how to view results"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Tutoriel - Étape 3")
        msg.setText("Vous pouvez cliquer sur un nom d'image.png pour voir le résultat du traitement")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
        
        # End of tutorial
        self.tutorial_active = False
        self.tutorial_step = 0

    def _update_result_labels_selection(self) -> None:
        """Updates the visual selection state of result labels based on currently displayed image."""
        for label in self.result_labels:
            stored_filename = label.property("filename")
            if stored_filename == self.current_displayed_image:
                label.setProperty("selected", True)
            else:
                label.setProperty("selected", False)
            # Force style recalculation
            label.style().unpolish(label)
            label.style().polish(label)

    def _update_timestamp(self) -> None:
        """Updates the timestamp"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.setText(f"Last updated: {now}")

    def _cleanup_results(self) -> None:
        """Deletes all PNG files in the results directory when closing the app"""
        import os
        for file in self.results_dir.glob("*.png"):
            try:
                os.remove(file)
                print(f"Deleted: {file}")
            except Exception as e:
                print(f"Error deleting {file}: {e}")

    def resizeEvent(self, event) -> None:
        """Handles window resize to scale image appropriately"""
        super().resizeEvent(event)
        if self.image_label.pixmap():
            pixmap = self.image_label.pixmap()
            scaled_pixmap = pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)

    def closeEvent(self, event) -> None:
        """Override close event to clean up PNG files before closing"""
        self._cleanup_results()
        event.accept()

    def __repr__(self) -> str:
        return f"ImageViewGraphic(results_dir='{self.results_dir}')"


def create_app() -> QApplication:
    """
    Creates and returns a QApplication instance.

    Returns:
        QApplication instance
    """
    app = QApplication([])
    app.setStyle("Fusion")
    return app


def main() -> None:
    """Main entry point for the GUI application"""
    app = create_app()
    window = ImageViewGraphic()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()

