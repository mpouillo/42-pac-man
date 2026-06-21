from pathlib import Path
from pydantic import BaseModel, FilePath, Field


class ConfigData(BaseModel):
    """Schema for validating and storing game configuration data."""

    highscores: str
    levels: list[FilePath]
    lives: int = Field(..., gt=0)
    points_per_pacgum: int = Field(..., ge=0)
    points_per_super_pacgum: int = Field(..., ge=0)
    points_per_ghost: int = Field(..., ge=0)
    points_per_second_left: int = Field(..., ge=0)


def load_config(file_path: str) -> ConfigData:
    """Load, pre-process, and validate a JSON configuration file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {file_path}")
    if path.is_dir():
        raise IsADirectoryError(f"Config path is a directory: {file_path}")

    try:
        raw_data = path.read_text()
    except OSError as e:
        raise OSError(f"Error while reading config file: {e}")

    clean_lines = (
        line for line in raw_data.splitlines()
        if not line.strip().startswith("#")
    )
    clean_data = "\n".join(clean_lines)

    try:
        return ConfigData.model_validate_json(clean_data)
    except Exception as e:
        raise ValueError(f"Invalid configuration data layout: {e}")
