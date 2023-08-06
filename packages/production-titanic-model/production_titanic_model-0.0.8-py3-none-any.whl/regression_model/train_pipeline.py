from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

from config.core import config
from regression_model.processing.data_manager import load_dataset, save_model
from regression_model.processing.features_preprocessing import preprocess_data


def run_training() -> None:

    # Load dataset.
    df_data = load_dataset(config.model_config.data_url)

    # Select specified columns.
    df_data = df_data[config.model_config.columns_to_select]

    # Preprocess data.
    df_data = preprocess_data(df_data)

    # Specify features and target.
    features_columns = df_data.columns.difference([config.model_config.target])
    target_column = config.model_config.target

    # Divide train and test
    X_train, X_test, y_train, y_test = train_test_split(
        df_data[features_columns],
        df_data[target_column],
        test_size=config.model_config.test_size,
        random_state=config.model_config.random_state,
    )

    # Train model.
    model = LogisticRegression()
    model.fit(X_train, y_train)

    # Persist model.
    save_model(model)


if __name__ == "__main__":
    run_training()
