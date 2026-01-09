"""
Advanced Processing Window for custom erosion and dilatation operations.

Provides:
- Numerical input fields for kernel_size, iterations, blur_sigma
- Checkbox for selective vs global mode
- "Apply Erosion" and "Apply Dilatation" buttons
"""

from typing import Optional, Callable
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSpinBox, QCheckBox, QGroupBox, QMessageBox, QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

import cv2 as cv
import numpy as np

from ..models import ImageModel, Erosion, Dilatation, SelectiveErosion, SelectiveDilatation


class AdvancedProcessingWindow(QWidget):
    """
    Advanced processing window for custom erosion and dilatation operations.
    
    Allows users to:
    - Set kernel_size and iterations for erosion/dilatation
    - Set blur_sigma for selective operations
    - Choose between global and selective mode via checkbox
    - Apply treatments and see results in the main window
    """

    # Signal emitted when processing is done (emits the filename to display)
    processing_done = pyqtSignal(str)

    # Default values for parameters
    _DEFAULT_EROSION_KERNEL = 3
    _DEFAULT_EROSION_ITER = 1
    _DEFAULT_DILATATION_KERNEL = 3
    _DEFAULT_DILATATION_ITER = 1
    _DEFAULT_BLUR_SIGMA = 5
    _DEFAULT_SELECTIVE = True

    def __init__(
        self,
        image_model: Optional[ImageModel] = None,
        parent: Optional[QWidget] = None
    ):
        """
        Initializes the advanced processing window.
        
        Args:
            image_model: The current ImageModel instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.image_model = image_model
        self._setup_ui()
        self._setup_styles()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Sets up the UI components and layout"""
        self.setWindowTitle("Traitement Avancé - SAE Astro")
        self.setMinimumSize(450, 550)
        self.setWindowFlags(Qt.WindowType.Window)  # Separate window with close button

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Paramètres de Traitement")
        title.setObjectName("windowTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # === Erosion Parameters ===
        erosion_group = QGroupBox("Érosion")
        erosion_group.setObjectName("paramGroup")
        erosion_layout = QVBoxLayout(erosion_group)
        erosion_layout.setSpacing(12)

        # Kernel size
        erosion_kernel_layout = QHBoxLayout()
        erosion_kernel_label = QLabel("Kernel size:")
        erosion_kernel_label.setObjectName("paramLabel")
        self.erosion_kernel_spin = QSpinBox()
        self.erosion_kernel_spin.setObjectName("paramSpinBox")
        self.erosion_kernel_spin.setRange(1, 21)
        self.erosion_kernel_spin.setSingleStep(2)  # Only odd numbers
        self.erosion_kernel_spin.setValue(self._DEFAULT_EROSION_KERNEL)
        erosion_kernel_layout.addWidget(erosion_kernel_label)
        erosion_kernel_layout.addWidget(self.erosion_kernel_spin)
        erosion_kernel_layout.addStretch()
        erosion_layout.addLayout(erosion_kernel_layout)

        # Iterations
        erosion_iter_layout = QHBoxLayout()
        erosion_iter_label = QLabel("Iterations:")
        erosion_iter_label.setObjectName("paramLabel")
        self.erosion_iter_spin = QSpinBox()
        self.erosion_iter_spin.setObjectName("paramSpinBox")
        self.erosion_iter_spin.setRange(1, 20)
        self.erosion_iter_spin.setValue(self._DEFAULT_EROSION_ITER)
        erosion_iter_layout.addWidget(erosion_iter_label)
        erosion_iter_layout.addWidget(self.erosion_iter_spin)
        erosion_iter_layout.addStretch()
        erosion_layout.addLayout(erosion_iter_layout)

        main_layout.addWidget(erosion_group)

        # === Dilatation Parameters ===
        dilatation_group = QGroupBox("Dilatation")
        dilatation_group.setObjectName("paramGroup")
        dilatation_layout = QVBoxLayout(dilatation_group)
        dilatation_layout.setSpacing(12)

        # Kernel size
        dilatation_kernel_layout = QHBoxLayout()
        dilatation_kernel_label = QLabel("Kernel size:")
        dilatation_kernel_label.setObjectName("paramLabel")
        self.dilatation_kernel_spin = QSpinBox()
        self.dilatation_kernel_spin.setObjectName("paramSpinBox")
        self.dilatation_kernel_spin.setRange(1, 21)
        self.dilatation_kernel_spin.setSingleStep(2)
        self.dilatation_kernel_spin.setValue(self._DEFAULT_DILATATION_KERNEL)
        dilatation_kernel_layout.addWidget(dilatation_kernel_label)
        dilatation_kernel_layout.addWidget(self.dilatation_kernel_spin)
        dilatation_kernel_layout.addStretch()
        dilatation_layout.addLayout(dilatation_kernel_layout)

        # Iterations
        dilatation_iter_layout = QHBoxLayout()
        dilatation_iter_label = QLabel("Iterations:")
        dilatation_iter_label.setObjectName("paramLabel")
        self.dilatation_iter_spin = QSpinBox()
        self.dilatation_iter_spin.setObjectName("paramSpinBox")
        self.dilatation_iter_spin.setRange(1, 20)
        self.dilatation_iter_spin.setValue(self._DEFAULT_DILATATION_ITER)
        dilatation_iter_layout.addWidget(dilatation_iter_label)
        dilatation_iter_layout.addWidget(self.dilatation_iter_spin)
        dilatation_iter_layout.addStretch()
        dilatation_layout.addLayout(dilatation_iter_layout)

        main_layout.addWidget(dilatation_group)

        # === Selective Parameters ===
        selective_group = QGroupBox("Paramètres Sélectifs")
        selective_group.setObjectName("paramGroup")
        selective_layout = QVBoxLayout(selective_group)
        selective_layout.setSpacing(12)

        # Blur sigma
        blur_layout = QHBoxLayout()
        blur_label = QLabel("Blur sigma:")
        blur_label.setObjectName("paramLabel")
        self.blur_spin = QSpinBox()
        self.blur_spin.setObjectName("paramSpinBox")
        self.blur_spin.setRange(0, 50)
        self.blur_spin.setValue(self._DEFAULT_BLUR_SIGMA)
        blur_layout.addWidget(blur_label)
        blur_layout.addWidget(self.blur_spin)
        blur_layout.addStretch()
        selective_layout.addLayout(blur_layout)

        main_layout.addWidget(selective_group)

        # === Mode Selection ===
        mode_layout = QHBoxLayout()
        self.selective_checkbox = QCheckBox("Mode sélectif (avec masque d'étoiles)")
        self.selective_checkbox.setObjectName("modeCheckbox")
        self.selective_checkbox.setChecked(self._DEFAULT_SELECTIVE)
        mode_layout.addWidget(self.selective_checkbox)
        mode_layout.addStretch()
        main_layout.addLayout(mode_layout)

        # Spacer
        main_layout.addStretch()

        # === Action Buttons ===
        button_layout = QVBoxLayout()
        button_layout.setSpacing(12)

        # Apply Erosion button
        self.erosion_button = QPushButton("Appliquer érosion")
        self.erosion_button.setObjectName("erosionButton")
        self.erosion_button.setCursor(Qt.CursorShape.PointingHandCursor)
        button_layout.addWidget(self.erosion_button)

        # Apply Dilatation button
        self.dilatation_button = QPushButton("Appliquer dilatation")
        self.dilatation_button.setObjectName("dilatationButton")
        self.dilatation_button.setCursor(Qt.CursorShape.PointingHandCursor)
        button_layout.addWidget(self.dilatation_button)

        main_layout.addLayout(button_layout)

    def _setup_styles(self) -> None:
        """Applies custom styles to the UI"""
        self.setStyleSheet("""
            QWidget {
                background-color: #0f0f1a;
            }
            QLabel#windowTitle {
                color: #e0e0e0;
                font-size: 20px;
                font-weight: bold;
                padding: 15px;
            }
            QGroupBox#paramGroup {
                color: #a0a0c0;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #2a2a4a;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 20px;
            }
            QGroupBox#paramGroup::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
            }
            QLabel#paramLabel {
                color: #d0d0e0;
                font-size: 14px;
                min-width: 100px;
                padding: 5px;
            }
            QSpinBox#paramSpinBox {
                background-color: #1a1a2e;
                color: #e0e0e0;
                border: 2px solid #3a3a5a;
                border-radius: 6px;
                padding: 8px;
                min-width: 80px;
                font-size: 14px;
            }
            QSpinBox#paramSpinBox:focus {
                border-color: #5a8aba;
                background-color: #20203a;
            }
            QSpinBox#paramSpinBox::up-button, QSpinBox#paramSpinBox::down-button {
                background-color: #2a2a4a;
                width: 20px;
                border-radius: 3px;
            }
            QSpinBox#paramSpinBox::up-button:hover, QSpinBox#paramSpinBox::down-button:hover {
                background-color: #3a3a6a;
            }
            QCheckBox#modeCheckbox {
                color: #c0c0e0;
                font-size: 14px;
                padding: 8px;
            }
            QCheckBox#modeCheckbox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #3a3a5a;
                border-radius: 4px;
                background-color: #1a1a2e;
            }
            QCheckBox#modeCheckbox::indicator:checked {
                background-color: #4a7a9a;
                border-color: #5a9aba;
            }
            QPushButton {
                background-color: #3a3a5a;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 15px 25px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4a4a7a;
            }
            QPushButton:pressed {
                background-color: #2a2a4a;
            }
            QPushButton#erosionButton {
                background-color: #6a3a5a;
            }
            QPushButton#erosionButton:hover {
                background-color: #8a4a7a;
            }
            QPushButton#dilatationButton {
                background-color: #3a6a5a;
            }
            QPushButton#dilatationButton:hover {
                background-color: #4a8a7a;
            }
        """)

    def _connect_signals(self) -> None:
        """Connects signals to handlers"""
        self.erosion_button.clicked.connect(self._on_apply_erosion)
        self.dilatation_button.clicked.connect(self._on_apply_dilatation)

    def set_image_model(self, image_model: ImageModel) -> None:
        """
        Sets the current image model.
        
        Args:
            image_model: The ImageModel instance
        """
        self.image_model = image_model

    def _reset_to_defaults(self) -> None:
        """Resets all parameter values to their defaults"""
        self.erosion_kernel_spin.setValue(self._DEFAULT_EROSION_KERNEL)
        self.erosion_iter_spin.setValue(self._DEFAULT_EROSION_ITER)
        self.dilatation_kernel_spin.setValue(self._DEFAULT_DILATATION_KERNEL)
        self.dilatation_iter_spin.setValue(self._DEFAULT_DILATATION_ITER)
        self.blur_spin.setValue(self._DEFAULT_BLUR_SIGMA)
        self.selective_checkbox.setChecked(self._DEFAULT_SELECTIVE)

    def _get_erosion_params(self) -> dict:
        """Returns erosion parameters from UI"""
        return {
            "kernel_size": self.erosion_kernel_spin.value(),
            "iterations": self.erosion_iter_spin.value(),
            "blur_sigma": self.blur_spin.value() if self.selective_checkbox.isChecked() else None,
            "selective": self.selective_checkbox.isChecked()
        }

    def _get_dilatation_params(self) -> dict:
        """Returns dilatation parameters from UI"""
        return {
            "kernel_size": self.dilatation_kernel_spin.value(),
            "iterations": self.dilatation_iter_spin.value(),
            "blur_sigma": self.blur_spin.value() if self.selective_checkbox.isChecked() else None,
            "selective": self.selective_checkbox.isChecked()
        }

    def _on_apply_erosion(self) -> None:
        """Handles Apply Erosion button click"""
        if self.image_model is None:
            QMessageBox.warning(self, "Erreur", "Aucune image chargée !\nVeuillez charger un fichier FITS d'abord.")
            return

        try:
            params = self._get_erosion_params()
            result_filename = self._apply_erosion(params)
            self.processing_done.emit(result_filename)
            QMessageBox.information(self, "Succès", "Érosion appliquée avec succès !")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'érosion: {e}")

    def _apply_erosion(self, params: dict) -> str:
        """
        Applies erosion with given parameters.
        
        Args:
            params: Dictionary with erosion parameters
            
        Returns:
            Filename of the result image
        """
        image = self.image_model.image
        is_color = self.image_model.is_color

        if params["selective"]:
            # Get star mask for selective erosion
            gray_image = self.image_model.get_gray_image()
            detector = self._get_star_detector()
            star_mask, _ = detector.detect(gray_image)

            # First apply global erosion
            global_erosion = Erosion(
                kernel_size=params["kernel_size"],
                iterations=params["iterations"]
            )
            eroded_image = global_erosion.apply(image)

            # Apply selective erosion
            erosion = SelectiveErosion(blur_sigma=params["blur_sigma"])
            result, _ = erosion.apply(image, eroded_image, star_mask)

            # Save result
            if is_color:
                self.image_model.save_color(result, "selective_eroded")
            else:
                self.image_model.save_grayscale(result, "selective_eroded")

            return "selective_eroded.png"
        else:
            # Apply global erosion
            erosion = Erosion(
                kernel_size=params["kernel_size"],
                iterations=params["iterations"]
            )
            result = erosion.apply(image)

            # Save result
            if is_color:
                self.image_model.save_color(result, "eroded")
            else:
                self.image_model.save_grayscale(result, "eroded")

            return "eroded.png"

    def _on_apply_dilatation(self) -> None:
        """Handles Apply Dilatation button click"""
        if self.image_model is None:
            QMessageBox.warning(self, "Erreur", "Aucune image chargée !\nVeuillez charger un fichier FITS d'abord.")
            return

        try:
            params = self._get_dilatation_params()
            result_filename = self._apply_dilatation(params)
            self.processing_done.emit(result_filename)
            QMessageBox.information(self, "Succès", "Dilatation appliquée avec succès !")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la dilatation: {e}")

    def _apply_dilatation(self, params: dict) -> str:
        """
        Applies dilatation with given parameters.
        
        Args:
            params: Dictionary with dilatation parameters
            
        Returns:
            Filename of the result image
        """
        image = self.image_model.image
        is_color = self.image_model.is_color

        if params["selective"]:
            # Get star mask for selective dilatation
            gray_image = self.image_model.get_gray_image()
            detector = self._get_star_detector()
            star_mask, _ = detector.detect(gray_image)

            # First apply global dilatation
            global_dilatation = Dilatation(
                kernel_size=params["kernel_size"],
                iterations=params["iterations"]
            )
            dilated_image = global_dilatation.apply(image)

            # Apply selective dilatation
            dilatation = SelectiveDilatation(blur_sigma=params["blur_sigma"])
            result, _ = dilatation.apply(image, dilated_image, star_mask)

            # Save result
            if is_color:
                self.image_model.save_color(result, "selective_dilated")
            else:
                self.image_model.save_grayscale(result, "selective_dilated")

            return "selective_dilated.png"
        else:
            # Apply global dilatation
            dilatation = Dilatation(
                kernel_size=params["kernel_size"],
                iterations=params["iterations"]
            )
            result = dilatation.apply(image)

            # Save result
            if is_color:
                self.image_model.save_color(result, "dilated")
            else:
                self.image_model.save_grayscale(result, "dilated")

            return "dilated.png"

    def _get_star_detector(self):
        """Creates a star detector for selective operations"""
        from ..models import StarDetector
        return StarDetector(
            fwhm=4.0,
            threshold=2.0,
            radius_factor=1.5
        )

    def closeEvent(self, event) -> None:
        """
        Override close event to reset values to defaults.
        """
        self._reset_to_defaults()
        super().closeEvent(event)

    def __repr__(self) -> str:
        return "AdvancedProcessingWindow()"


def create_advanced_window(
    image_model: Optional[ImageModel] = None,
    parent: Optional[QWidget] = None
) -> AdvancedProcessingWindow:
    """
    Creates and returns an AdvancedProcessingWindow instance.
    
    Args:
        image_model: Optional ImageModel to set
        parent: Parent widget (can be None for independent window)
        
    Returns:
        AdvancedProcessingWindow instance
    """
    window = AdvancedProcessingWindow(image_model=image_model, parent=parent)
    return window

