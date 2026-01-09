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
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QObject, QUrl
from PyQt6.QtGui import QPixmap, QImage, QFont, QIcon, QFontDatabase, QDesktopServices

# Import existing model classes and controller
from ..models import ImageModel, StateManager, Config
from ..controllers import PipelineController
from .advanced_processing_window import AdvancedProcessingWindow, create_advanced_window


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
        parent: Optional[QWidget] = None,
        saved_state: Optional[dict] = None
    ):
        """
        Initializes the GUI window.

        Args:
            results_dir: Directory for result images
            parent: Parent widget
            saved_state: Optional saved state to restore (from StateManager)
        """
        super().__init__(parent)
        self.results_dir = Path(results_dir)
        self.image_model: Optional[ImageModel] = None
        self.num_stars: int = 0
        self.current_displayed_image: str = "original.png"  # Track currently displayed image

        # State manager for save/load functionality
        self.state_manager = StateManager(Config.STATE_FILE)

        # Closing flag to prevent re-entrancy in close event
        self._is_closing: bool = False

        # Flag to indicate if state was restored (so PNG clicks work)
        self._state_restored: bool = False

        # Tutorial state variables
        self.tutorial_active: bool = False
        self.tutorial_step: int = 0
        self._tuto_advanced_opened: bool = False  # Track if advanced window was opened from tutorial

        # Advanced processing window reference
        self.advanced_window: Optional[AdvancedProcessingWindow] = None

        # Setup UI first
        self._setup_ui()
        self._setup_styles()
        self._connect_signals()

        # Load saved state if available
        if saved_state:
            self._restore_state(saved_state)

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

        self.advanced_button = QPushButton("⚙ Traitement avancé")
        self.advanced_button.setObjectName("advancedButton")
        self.advanced_button.clicked.connect(self._on_advanced_clicked)
        top_layout.addWidget(self.advanced_button, alignment=Qt.AlignmentFlag.AlignRight)

        self.open_button = QPushButton("Open FITS")
        self.open_button.setObjectName("openButton")
        self.open_button.clicked.connect(self._on_open_fits)
        top_layout.addWidget(self.open_button, alignment=Qt.AlignmentFlag.AlignRight)

        self.close_button = QPushButton("Close APP")
        self.close_button.setObjectName("closeButton")
        self.close_button.clicked.connect(self._on_close_clicked)
        top_layout.addWidget(self.close_button, alignment=Qt.AlignmentFlag.AlignRight)

        main_layout.addWidget(top_bar)

        # === Progress Bar ===
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progressBar")
        self.progress_bar.setRange(0, 7)
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

        # Row 1: first 4 result files
        row1_widget = QWidget()
        row1_layout = QHBoxLayout(row1_widget)
        row1_layout.setContentsMargins(0, 0, 0, 0)
        row1_layout.setSpacing(10)

        self.result_labels: List[QLabel] = []
        result_files = [
            "original.png",
            "starmask.png",
            "eroded.png",
            "selective_eroded.png",
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

        # Row 2: last 4 result files
        row2_widget = QWidget()
        row2_layout = QHBoxLayout(row2_widget)
        row2_layout.setContentsMargins(0, 0, 0, 0)
        row2_layout.setSpacing(10)

        result_files_row2 = [
            "smooth_mask.png",
            "dilated.png",
            "selective_dilated.png",
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

        # === Open Results Folder Button ===
        results_button_widget = QWidget()
        results_button_layout = QHBoxLayout(results_button_widget)
        results_button_layout.setContentsMargins(0, 10, 0, 0)

        results_button_layout.addStretch()

        self.open_results_button = QPushButton("Open Results Folder")
        self.open_results_button.setObjectName("openResultsButton")
        self.open_results_button.clicked.connect(self._on_open_results_folder)
        results_button_layout.addWidget(self.open_results_button)

        results_button_layout.addStretch()

        content_layout.addWidget(results_button_widget)

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
            QPushButton#advancedButton {
                background-color: #5a4a7a;
            }
            QPushButton#advancedButton:hover {
                background-color: #7a6a9a;
            }
            QPushButton#closeButton {
                background-color: #5a3a3a;
            }
            QPushButton#closeButton:hover {
                background-color: #7a4a4a;
            }
            QPushButton#openResultsButton {
                background-color: #4a7a4a;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 12px;
                min-width: 120px;
            }
            QPushButton#openResultsButton:hover {
                background-color: #6a9a6a;
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
        self.progress_bar.setValue(7)
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
        # Security check: if no FITS file is loaded and no state was restored, show tutorial
        if self.image_model is None and not self._state_restored:
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

        # Continue to step 4
        self._show_tuto_step_4()

    def _show_tuto_step_4(self) -> None:
        """Shows step 4 of the tutorial: explain advanced parameters button"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Tutoriel - Étape 4")
        msg.setText("Vous pouvez cliquer sur traitement avancé")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

        # Mark that we need to open advanced window and show step 5
        self._tuto_advanced_opened = True
        # Open the advanced processing window
        self._on_advanced_clicked()

    def _show_tuto_step_5(self) -> None:
        """Shows step 5 of the tutorial: explain dilation/erosion with real-time preview"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Tutoriel - Étape 5")
        msg.setText(
            "vous pouvez effectuer une dilatation ou érosion avec des parametres dans cette fenetre "
            "et voir le résulat en temps réel dans la fenetre principal"
        )
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

        # Step 6 will be triggered by the advanced processing done signal

    def _show_tuto_step_6(self) -> None:
        """Shows step 6 of the tutorial: explain image selection change after processing"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Tutoriel - Étape 6")
        msg.setText(
            "après un traitement, la selection de l'image affiché change pour le fichier "
            "correspondant au résultat du traitement"
        )
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

        # End of tutorial
        self.tutorial_active = False
        self.tutorial_step = 0
        self._tuto_advanced_opened = False

    def _on_advanced_clicked(self) -> None:
        """Opens the advanced processing window"""
        # Security check: if no FITS file is loaded and no state was restored, show tutorial
        if self.image_model is None and not self._state_restored:
            self._on_tuto_clicked()
            return

        if self.advanced_window is None or not self.advanced_window.isVisible():
            self.advanced_window = create_advanced_window(
                image_model=self.image_model,
                parent=self  # Set parent to main window for proper lifecycle management
            )
            # Connect the processing done signal
            self.advanced_window.processing_done.connect(self._on_advanced_processing_done)
        
        self.advanced_window.show()
        self.advanced_window.raise_()
        self.advanced_window.activateWindow()

        # Trigger tutorial step 5 if tutorial is active and advanced window was opened from tutorial
        if self.tutorial_active and self._tuto_advanced_opened:
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(100, self._show_tuto_step_5)

    def _on_advanced_processing_done(self, filename: str) -> None:
        """
        Handles the completion of advanced processing.
        
        Args:
            filename: The filename of the result image to display
        """
        # Update the image model reference in the advanced window
        if self.advanced_window is not None:
            self.advanced_window.set_image_model(self.image_model)
        
        # Display the result image
        self._display_image(filename)
        
        # Update timestamp
        self._update_timestamp()

        # Trigger tutorial step 6 if tutorial is active
        if self.tutorial_active and self._tuto_advanced_opened:
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(500, self._show_tuto_step_6)

    def _show_close_confirmation(self) -> None:
        """Shows a confirmation dialog before closing the application"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Quitter l'application")
        msg.setText("Vous êtes sur le point de quitter l'application, voulez-vous sauvegarder l'état actuel ?")
        msg.setIcon(QMessageBox.Icon.Question)

        # Add custom buttons
        btn_yes = msg.addButton("Oui", QMessageBox.ButtonRole.YesRole)
        btn_no = msg.addButton("Non", QMessageBox.ButtonRole.NoRole)
        btn_cancel = msg.addButton("Annuler", QMessageBox.ButtonRole.RejectRole)

        # Set default button
        msg.setDefaultButton(btn_yes)

        msg.exec()

        if msg.clickedButton() == btn_yes:
            # Save state and close without deleting images
            self._save_and_close()
        elif msg.clickedButton() == btn_no:
            # Delete images and close
            self._cleanup_results()
            self.state_manager.clear_state()
            # Set closing flag to prevent re-entrancy
            self._is_closing = True
            self.close()
        else:
            # Cancel - do nothing
            pass

    def _on_close_clicked(self) -> None:
        """Handles the Close APP button click"""
        # If no image is loaded and no state was restored, just close without confirmation
        if self.image_model is None and not self._state_restored:
            self.close()
            return

        # Show confirmation dialog
        self._show_close_confirmation()

    def _on_open_results_folder(self) -> None:
        """Handles the Open Results Folder button click"""
        try:
            results_url = QUrl.fromLocalFile(str(self.results_dir.absolute()))
            QDesktopServices.openUrl(results_url)
        except Exception as e:
            print(f"Error opening results folder: {e}")

    def _save_and_close(self) -> None:
        """Saves the current state and closes without deleting images"""
        fits_path = str(self.image_model.fits_path) if self.image_model else ""

        # Save state using state manager
        self.state_manager.save_state(
            fits_path=fits_path,
            displayed_image=self.current_displayed_image,
            num_stars=self.num_stars
        )

        # Set closing flag to prevent re-entrancy
        self._is_closing = True

        # Close the application
        self.close()

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

    def _restore_state(self, state: dict) -> None:
        """
        Restores application state from saved data.

        Args:
            state: Dictionary containing saved state (fits_file, displayed_image, num_stars, timestamp)
        """
        try:
            fits_path = state.get("fits_file")
            displayed_image = state.get("displayed_image", "original.png")
            num_stars = state.get("num_stars", 0)
            timestamp = state.get("timestamp", "")

            if not fits_path:
                return

            fits_file_path = Path(fits_path)

            # Check if FITS file still exists
            if not fits_file_path.exists():
                print(f"FITS file not found: {fits_file_path}")
                # Still restore UI state but show warning
                self.file_label.setText(f"{fits_file_path.name} (file not found)")
                self.current_displayed_image = displayed_image
                self.num_stars = num_stars
                self.stars_count.setText(str(num_stars))
                self._state_restored = True

                if timestamp:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(timestamp)
                        formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                        self.timestamp_label.setText(f"Restored: {formatted_time} (FITS file missing)")
                    except (ValueError, TypeError):
                        self.timestamp_label.setText(f"Restored: {timestamp} (FITS file missing)")
                else:
                    self.timestamp_label.setText("Restored from save (FITS file missing)")

                # Update result labels and display image anyway
                self._update_result_labels_selection()
                self._display_image(displayed_image)
                return

            # FITS file exists, load it
            self.load_fits(str(fits_file_path))

            # Override the displayed image to match saved state
            self.current_displayed_image = displayed_image
            self._update_result_labels_selection()
            self._display_image(displayed_image)

            # Update timestamp
            if timestamp:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(timestamp)
                    formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                    self.timestamp_label.setText(f"Restored: {formatted_time}")
                except (ValueError, TypeError):
                    self.timestamp_label.setText(f"Restored: {timestamp}")
            else:
                self.timestamp_label.setText("Restored from save")

            print(f"State restored: {fits_path}")

        except Exception as e:
            print(f"Error restoring state: {e}")

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
        """
        Override close event to handle save/cleanup before closing.
        Shows confirmation dialog if an image is loaded or state was restored.
        """
        # If already closing or no image loaded and no state restored, accept close
        if self._is_closing or (self.image_model is None and not self._state_restored):
            event.accept()
            return

        # Prevent default closing
        event.ignore()

        # Show confirmation dialog
        self._show_close_confirmation()

    def _cleanup_advanced_window(self) -> None:
        """
        Cleans up the advanced processing window.
        Note: Since windows are now independent, this only clears the reference.
        """
        self.advanced_window = None

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


def create_window(saved_state: Optional[dict] = None) -> "ImageViewGraphic":
    """
    Creates and returns an ImageViewGraphic window.

    Args:
        saved_state: Optional saved state to restore (from StateManager)

    Returns:
        ImageViewGraphic instance
    """
    window = ImageViewGraphic(saved_state=saved_state)
    return window


def main() -> None:
    """Main entry point for the GUI application"""
    from ..models import Config, StateManager

    app = create_app()

    # Check for saved state
    state_manager = StateManager(Config.STATE_FILE)
    saved_state = state_manager.load_state() if state_manager.has_saved_state() else None

    window = create_window(saved_state=saved_state)
    window.show()
    app.exec()


if __name__ == "__main__":
    main()

