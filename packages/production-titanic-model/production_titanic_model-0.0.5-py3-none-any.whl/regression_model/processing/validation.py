import pandas as pd
from typing import List, Optional, Tuple
from pydantic import BaseModel, ValidationError

from regression_model.config.core import config


def validate_inputs(input_data: pd.DataFrame) -> Tuple[pd.DataFrame, Optional[dict]]:

    # Select specified columns.
    validated_data = input_data[config.model_config.features].copy()
    errors = None

    try:
        MultipleDataInputs(inputs=validated_data.to_dict(orient="records"))
    except ValidationError as error:
        errors = error.json()

    return validated_data, errors


class DataInputSchema(BaseModel):
    Age: int
    Sex: str
    Embarked: str


class MultipleDataInputs(BaseModel):
    inputs: List[DataInputSchema]
