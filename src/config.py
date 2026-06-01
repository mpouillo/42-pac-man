from pathlib import Path

from pydantic import BaseModel


class ConfigData(BaseModel):
    highscore_filename: str
    lives: int
    points_per_pacgum: int
    points_per_super_pacgum: int
    points_per_ghost: int


class Config:
    @staticmethod
    def load(file_path: Path) -> ConfigData:
        if not file_path.exists() or file_path.is_dir():
            raise ValueError("File does not exist.")

        try:
            raw_data = file_path.read_text()
        except Exception as e:
            raise IOError(f"Error while reading config file: {e}")

        try:
            clean_data = "".join([
                line for line in raw_data.split('\n')
                if not line.strip().startswith('#')
            ])
            print(clean_data)
            validated_data = ConfigData.model_validate_json(clean_data)
        except Exception as e:
            raise ValueError(f"Invalid data in config: {e}")

        return validated_data
