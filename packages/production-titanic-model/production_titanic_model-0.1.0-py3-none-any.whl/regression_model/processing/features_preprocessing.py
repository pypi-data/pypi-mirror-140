import pandas as pd


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:

    categorical_arr = []

    for col, col_type in df.dtypes.iteritems():
        if col_type == "O":
            categorical_arr.append(col)
        else:
            df[col].fillna(0, inplace=True)

    df_ohe = pd.get_dummies(df, columns=categorical_arr, dummy_na=True)

    return df_ohe
