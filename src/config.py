from pathlib import Path

from pydantic import BaseModel, FilePath


class ConfigData(BaseModel):
    highscores: str
    levels: list[FilePath]
    lives: int
    points_per_pacgum: int
    points_per_super_pacgum: int
    points_per_ghost: int


def load_config(file_path: str) -> ConfigData:
    path = Path(file_path)
    if not path.exists() or path.is_dir():
        raise OSError("File does not exist.")

    try:
        raw_data = path.read_text()
    except OSError as e:
        raise OSError(f"Error while reading config file: {e}")

    try:
        clean_data = "\n".join([
            line for line in raw_data.split('\n')
            if not line.strip().startswith('#')
        ])
        validated_data = ConfigData.model_validate_json(clean_data)
    except Exception as e:
        raise ValueError(f"Invalid data in config: {e}")

    return validated_data
