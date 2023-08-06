import typing

import pandas as pd

from regression_model import __version__ as _version
from regression_model.config.core import TRAINED_MODEL_DIR
from regression_model.processing.data_manager import load_model
from regression_model.processing.features_preprocessing import preprocess_data
from regression_model.processing.validation import validate_inputs

model_file_name = TRAINED_MODEL_DIR / f"model_{_version}.pkl"
_model = load_model(file_name=model_file_name)


def make_prediction(input_data: typing.Union[pd.DataFrame, dict]) -> dict:

    data = pd.DataFrame(input_data)
    validated_data, errors = validate_inputs(input_data=data)
    validated_data = preprocess_data(validated_data)

    results = {"predictions": None, "version": _version, "errors": errors}

    all_features = [
        "Age",
        "Embarked_C",
        "Embarked_Q",
        "Embarked_S",
        "Embarked_nan",
        "Sex_female",
        "Sex_male",
        "Sex_nan",
    ]

    # Sync inputs.
    for feature in all_features:
        if feature not in validated_data:
            validated_data[feature] = 0
    validated_data = validated_data[all_features]

    if not errors:
        predictions = _model.predict_proba(X=validated_data)
        predictions = [x[1] for x in predictions]
        results = {"predictions": predictions, "version": _version, "errors": errors}

    # .
    return results
