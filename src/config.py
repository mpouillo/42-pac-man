from pathlib import Path
from pydantic import (
    BaseModel,
    FilePath,
    Field,
    RootModel,
    field_validator
)
from src.highscore import HighscoreEntry


class ConfigData(BaseModel):
    """Schema for validating and storing game configuration data."""

    highscores: str
    levels: list[FilePath]
    lives: int = Field(..., gt=0)
    points_per_pacgum: int = Field(..., ge=0)
    points_per_super_pacgum: int = Field(..., ge=0)
    points_per_ghost: int = Field(..., ge=0)
    points_per_second_left: int = Field(..., ge=0)

    @field_validator('highscores', mode='after')
    @classmethod
    def validate_highscores_file(cls, filename: str) -> str:
        """Check highscores file is valid and can be used."""
        path = Path(filename)

        if not path.exists():
            return filename

        if path.is_dir():
            raise ValueError(
                f"Path '{filename}' points to a directory, not a file."
            )

        contents = path.read_text(encoding="utf-8")
        if not contents.strip():
            return filename

        clean_lines = (
            line for line in contents.splitlines()
            if not line.strip().startswith("#")
        )
        clean_data = "\n".join(clean_lines)

        try:
            RootModel[list[HighscoreEntry]].model_validate_json(clean_data)
            return filename
        except Exception:
            raise ValueError("File exists but is not a valid highscores file.")


def load_config(file_path: str) -> ConfigData:
    """Load, pre-process, and validate a JSON configuration file."""
    try:
        return ConfigData.model_validate_json(Path(file_path).read_text())
    except Exception as e:
        raise ValueError(f"Invalid configuration data layout: {e}")
