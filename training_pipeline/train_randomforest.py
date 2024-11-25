import pickle
import mlflow
import pathlib
import dagshub
import pandas as pd
import xgboost as xgb
import mlflow.sklearn
from mlflow import MlflowClient
from hyperopt.pyll import scope
from sklearn.metrics import root_mean_squared_error
from sklearn.feature_extraction import DictVectorizer
from hyperopt import fmin, tpe, hp, STATUS_OK, Trials
from prefect import flow, task
from sklearn.metrics import mean_squared_error
import yfinance as yf
import numpy as np
from sklearn.ensemble import RandomForestRegressor


## df
google_stock = yf.download('GOOGL', start='2015-01-01', end='2024-01-01')

# Configura la URL del experimento en DagsHub
DAGSHUB_URL = "https://dagshub.com/PacoTinoco/Proyecto_Final_CDD"
CSV_PATH = "../data/GOOGL_yfinance_daily_2023-11-03_to_2024-11-02.csv"

# Definir la función de lectura de datos

@task(name="Read Data", retries=4, retry_delay_seconds=[1, 4, 8, 16])
def read_data(file_path: str) -> pd.DataFrame:
    """Read data into DataFrame"""
    df = pd.read_csv(file_path)

    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(by="Date")


    # Filtrar datos para evitar valores anómalos (ajustar según tu dataset)
    df = df[(df['Volume'] > 0) & (df['Close'] > 0)]

    return df



# Definir función para agregar características
@task(name="Add features")
def add_features(df: pd.DataFrame):


    # Variables numéricas
    X = google_stock.drop(columns=["Close"])
    y = google_stock["Close"]
    from sklearn.model_selection import train_test_split
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
    return X_train, X_val, y_train, y_val


# Función de ajuste de hiperparámetros
@task(name="Hyperparameter tuning")
def hyper_parameter_tuning_rf(X_train, X_val, y_train, y_val):
    mlflow.sklearn.autolog()

    # Definición de la función objetivo
    def objective_rf(params):
        with mlflow.start_run(nested=True):
            # Set model tag
            mlflow.set_tag("model_family", "random_forest")

            # Crear modelo de RandomForest con parámetros específicos
            rf_model = RandomForestRegressor(
                n_estimators=int(params['n_estimators']),
                max_depth=int(params['max_depth']),
                min_samples_split=int(params['min_samples_split']),
                min_samples_leaf=int(params['min_samples_leaf']),
                random_state=42
            )

            # Entrenar el modelo
            rf_model.fit(X_train, y_train)

            # Predecir en el conjunto de validación
            y_pred = rf_model.predict(X_val)

            # Calcular RMSE
            rmse = np.sqrt(mean_squared_error(y_val, y_pred))

            # Logear métrica de RMSE en mlflow
            mlflow.log_metric("rmse", rmse)

            return {'loss': rmse, 'status': STATUS_OK}

    # Espacio de búsqueda de hiperparámetros para Random Forest
    search_space_rf = {
        'n_estimators': scope.int(hp.quniform('n_estimators', 50, 200, 1)),
        'max_depth': scope.int(hp.quniform('max_depth', 5, 30, 1)),
        'min_samples_split': scope.int(hp.quniform('min_samples_split', 2, 10, 1)),
        'min_samples_leaf': scope.int(hp.quniform('min_samples_leaf', 1, 4, 1)),
    }

    # Ejecución de la optimización de hiperparámetros
    with mlflow.start_run(run_name="Optimización de Hiperparámetros Random Forest", nested=True):
        best_params = fmin(
            fn=objective_rf,
            space=search_space_rf,
            algo=tpe.suggest,
            max_evals=10,
            trials=Trials()
        )

        # Ajustar los tipos de parámetros según Random Forest
        best_params["n_estimators"] = int(best_params["n_estimators"])
        best_params["max_depth"] = int(best_params["max_depth"])
        best_params["min_samples_split"] = int(best_params["min_samples_split"])
        best_params["min_samples_leaf"] = int(best_params["min_samples_leaf"])

        # Loggear los mejores parámetros en mlflow
        mlflow.log_params(best_params)

    return best_params


# Función para entrenar el mejor modelo
@task(name="Train Best Model")
def train_best_model(X_train, X_val, y_train, y_val, best_params) -> None:
    with mlflow.start_run(run_name="Mejor modelo Random Forest"):
        # Registrar los mejores parámetros en mlflow
        mlflow.log_params(best_params)

        # Crear y entrenar el modelo RandomForest con los mejores parámetros
        rf_model = RandomForestRegressor(
            n_estimators=int(best_params['n_estimators']),
            max_depth=int(best_params['max_depth']),
            min_samples_split=int(best_params['min_samples_split']),
            min_samples_leaf=int(best_params['min_samples_leaf']),
            random_state=42
        )

        rf_model.fit(X_train, y_train)

        # Realizar predicciones en el conjunto de validación
        y_pred = rf_model.predict(X_val)

        # Calcular la métrica RMSE
        rmse = np.sqrt(mean_squared_error(y_val, y_pred))
        mlflow.log_metric("rmse", rmse)


        # Guardar el modelo RandomForest entrenado
        with open("models/random_forest_model.pkl", "wb") as f_model:
            pickle.dump(rf_model, f_model)
        mlflow.log_artifact("models/random_forest_model.pkl", artifact_path="model")

    return None


@task(name = 'Register Model')
def register_model():
    MLFLOW_TRACKING_URI = mlflow.get_tracking_uri()
    client = MlflowClient(tracking_uri=MLFLOW_TRACKING_URI)

    df = mlflow.search_runs(order_by=['metrics.rmse'])
    run_id = df.loc[df['metrics.rmse'].idxmin()]['run_id']
    run_uri = f"runs:/{run_id}/model"

    result = mlflow.register_model(
        model_uri=run_uri,
        name="google-stock-model-randomforest-perfect"
    )
    model_name = "google-stock-model-randomforest-perfect"
    model_version_alias = "champion"

    # create "champion" alias for version 1 of model "nyc-taxi-model"
    client.set_registered_model_alias(
        name=model_name,
        alias=model_version_alias,
        version= '1'
    )



# Definir el flujo principal con Prefect
@flow(name="Main Flow")
def main_flow() -> None:
    """Pipeline de entrenamiento principal para datos de Google Stocks"""

    # Inicializar MLflow en DagsHub
    dagshub.init(url=DAGSHUB_URL, mlflow=True)
    mlflow.set_experiment(experiment_name="google-stock-model-randomforest-prefect")

    # Paso 1: Lectura de datos
    df = read_data(CSV_PATH)

    # Paso 2: Agregar características
    X_train, X_val, y_train, y_val = add_features(df)

    # Paso 3: Ajuste de hiperparámetros
    best_params = hyper_parameter_tuning_rf(X_train, X_val, y_train, y_val)

    # Paso 4: Entrenar el mejor modelo
    train_best_model(X_train, X_val, y_train, y_val, best_params)

    # Paso 5: Registrar modelo
    register_model()


# Ejecutar el flujo principal
main_flow()


