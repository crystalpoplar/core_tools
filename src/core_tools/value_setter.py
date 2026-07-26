import logging
import os
from pathlib import Path


def _build_directories() -> dict[str, str]:
    app_data = os.environ.get("APPDATA") or os.environ.get("XDG_DATA_HOME")
    base_path = (Path(app_data) if app_data else (Path.home() / ".local" / "share")) / "core_tools"
    return {
        "main_dir": str(base_path) + os.sep,
        "indicator_dir": str(base_path / "indicators") + os.sep,
        "inputs_dir": str(base_path / "inputs") + os.sep,
        "images_dir": str(base_path / "images") + os.sep,
        "archive_dir": str(base_path / "archive") + os.sep,
        "logging_dir": str(base_path / "logging") + os.sep,
    }


_DIRECTORIES = _build_directories()

main_dir = _DIRECTORIES["main_dir"]
indicator_dir = _DIRECTORIES["indicator_dir"]
inputs_dir = _DIRECTORIES["inputs_dir"]
images_dir = _DIRECTORIES["images_dir"]
archive_dir = _DIRECTORIES["archive_dir"]
logging_dir = _DIRECTORIES["logging_dir"]


logging.basicConfig(
    filename=os.path.join(main_dir, "directory_creation.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def create_dirs() -> None:
    """Create the package's working directories when they do not already exist."""
    for directory in [main_dir, indicator_dir, inputs_dir, images_dir, archive_dir, logging_dir]:
        dir_path = directory.rstrip("\\/")
        try:
            if not os.path.isdir(dir_path):
                os.makedirs(dir_path)
                logging.info("Created required directory: %s", dir_path)
            else:
                logging.warning("Directory already exists: %s", dir_path)
        except OSError as error:
            logging.error("Failed to create directory %s: %s", dir_path, error)
            print(f"Error: Could not create directory {dir_path}. Check logs for details.")


def createDirs() -> None:
    """Backward-compatible alias for older callers."""
    create_dirs()


create_dirs()
