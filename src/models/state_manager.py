"""
State manager for saving and loading application state.

Handles persistence of:
- Selected FITS file path
- Currently displayed image
- Number of detected stars
- Timestamp of save
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any


class StateManager:
    """
    Manages application state persistence using JSON files.

    Allows users to save their current session and restore it on next launch.
    """

    def __init__(self, state_file: Path | str = "./results/state.json"):
        """
        Initializes the state manager.

        Args:
            state_file: Path to the state file
        """
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

    def save_state(
        self,
        fits_path: str,
        displayed_image: str = "original.png",
        num_stars: int = 0
    ) -> bool:
        """
        Saves the current application state to a JSON file.

        Args:
            fits_path: Path to the currently loaded FITS file
            displayed_image: Currently displayed image filename
            num_stars: Number of detected stars

        Returns:
            True if save was successful, False otherwise
        """
        try:
            state = {
                "fits_file": fits_path,
                "displayed_image": displayed_image,
                "num_stars": num_stars,
                "timestamp": datetime.now().isoformat()
            }

            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)

            print(f"State saved: {self.state_file}")
            return True

        except Exception as e:
            print(f"Error saving state: {e}")
            return False

    def load_state(self) -> Optional[Dict[str, Any]]:
        """
        Loads the application state from the JSON file.

        Returns:
            State dictionary with keys: fits_file, displayed_image, num_stars, timestamp
            None if no saved state exists or if loading fails
        """
        if not self.state_file.exists():
            return None

        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)

            # Validate required keys
            required_keys = ["fits_file", "displayed_image", "num_stars", "timestamp"]
            if not all(key in state for key in required_keys):
                print("Invalid state file: missing required keys")
                return None

            print(f"State loaded: {self.state_file}")
            return state

        except json.JSONDecodeError as e:
            print(f"Error parsing state file: {e}")
            return None
        except Exception as e:
            print(f"Error loading state: {e}")
            return None

    def has_saved_state(self) -> bool:
        """
        Checks if a saved state exists.

        Returns:
            True if state file exists and is valid, False otherwise
        """
        if not self.state_file.exists():
            return False

        # Try to load and validate
        state = self.load_state()
        return state is not None

    def clear_state(self) -> bool:
        """
        Deletes the saved state file.

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            if self.state_file.exists():
                self.state_file.unlink()
                print(f"State cleared: {self.state_file}")
            return True
        except Exception as e:
            print(f"Error clearing state: {e}")
            return False

    def get_fits_path(self) -> Optional[str]:
        """
        Convenience method to get only the FITS file path from saved state.

        Returns:
            FITS file path or None if no state exists
        """
        state = self.load_state()
        return state["fits_file"] if state else None

    def __repr__(self) -> str:
        return f"StateManager(state_file='{self.state_file}')"

