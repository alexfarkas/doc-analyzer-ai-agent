import json
from pathlib import Path
from typing import Any

import yaml
from pydantic_settings import PydanticBaseSettingsSource


class FileConfigSettingsSource(PydanticBaseSettingsSource):
    def __init__(self, settings_cls, file_path: str | Path):
        self.file_path = Path(file_path)
        super().__init__(settings_cls)

    def get_field_value(self, field, field_name: str) -> tuple[Any, str, bool]:
        return None, field_name, False

    def _load_file(self) -> dict[str, Any]:
        if not self.file_path.exists():
            return {}

        with open(self.file_path, "r", encoding="utf-8") as f:
            if self.file_path.suffix in (".yaml", ".yml"):
                return yaml.safe_load(f) or {}
            elif self.file_path.suffix == ".json":
                return json.load(f)
            else:
                raise ValueError(
                    f"Unsupported file format: {self.file_path.suffix}"
                )

    def __call__(self) -> dict[str, Any]:
        return self._load_file()
