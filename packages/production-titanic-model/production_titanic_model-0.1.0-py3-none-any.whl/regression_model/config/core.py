from pathlib import Path
from typing import List

from pydantic import BaseModel
from strictyaml import YAML, load

import regression_model

# Project Directories
PACKAGE_ROOT = Path(regression_model.__file__).resolve().parent
CONFIG_FILE_PATH = PACKAGE_ROOT / "config.yml"
TRAINED_MODEL_DIR = PACKAGE_ROOT / "trained_models"


class AppConfig(BaseModel):

    """
    Application-level config.

    """

    package_name: str


class ModelConfig(BaseModel):

    """
    Model-level config.

    """

    data_url: str
    columns_to_select: List[str]
    features: List[str]
    target: str
    random_state: int
    test_size: float


class Config(BaseModel):

    """
    Master config object.

    """

    app_config: AppConfig
    model_config: ModelConfig


def fetch_config_from_yaml() -> YAML:

    with open(CONFIG_FILE_PATH, "r") as conf_file:
        parsed_config = load(conf_file.read())
        return parsed_config


def load_and_validate_config() -> Config:

    parsed_config = fetch_config_from_yaml()

    # Specify the data attribute from the strictyaml YAML type.
    _config = Config(
        app_config=AppConfig(**parsed_config.data),
        model_config=ModelConfig(**parsed_config.data),
    )

    return _config


config = load_and_validate_config()
