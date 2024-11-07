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
    train = xgb.DMatrix(X_train, label=y_train)
    valid = xgb.DMatrix(X_val, label=y_val)
    return train, valid


# Función de ajuste de hiperparámetros
@task(name="Hyperparameter tuning")

def hyper_parameter_tuning(train, valid):
    mlflow.xgboost.autolog()
    def objective(params):
        with mlflow.start_run(nested=True):
            mlflow.set_tag("model_family", "xgboost")

            # Entrenar modelo
            booster = xgb.train(
                params=params,
                dtrain=train,
                num_boost_round=100,
                early_stopping_rounds=10,
            )

            # Calcular métrica
            y_pred = booster.predict(valid)
            rmse = mean_squared_error(y_val, y_pred, squared=False)
            mlflow.log_metric("rmse", rmse)

        return {'loss': rmse, 'status': STATUS_OK}

    with mlflow.start_run(run_name="Optimización de hiperparámetros Xgboost", nested=True):
        search_space = {
            'max_depth': scope.int(hp.quniform('max_depth', 4, 100, 1)),
            'learning_rate': hp.loguniform('learning_rate', -3, 0),
            'reg_alpha': hp.loguniform('reg_alpha', -5, -1),
            'reg_lambda': hp.loguniform('reg_lambda', -6, -1),
            'min_child_weight': hp.loguniform('min_child_weight', -1, 3),
            'objective': 'reg:squarederror',
            'seed': 42
        }

        best_params = fmin(
            fn=objective,
            space=search_space,
            algo=tpe.suggest,
            max_evals=10,
            trials=Trials()
        )

        # Ajustar tipos de parámetros según XGBoost
        best_params["max_depth"] = int(best_params["max_depth"])
        best_params["seed"] = 42
        best_params["objective"] = "reg:squarederror"

        mlflow.log_params(best_params)

    return best_params


# Función para entrenar el mejor modelo
@task(name = "Train Best Model")
def train_best_model(X_train, X_val, y_train, y_val, best_params) -> None:
    with mlflow.start_run(run_name="Mejor modelo"):
        train = xgb.DMatrix(X_train, label=y_train)
        valid = xgb.DMatrix(X_val, label=y_val)

        mlflow.log_params(best_params)


        # Entrenar el modelo con los mejores parámetros
        booster = xgb.train(
            params=best_params,
            dtrain=train,
            num_boost_round=100,
            evals=[(valid, 'validation')],
            early_stopping_rounds=10
        )

        y_pred = booster.predict(valid)
        rmse = np.sqrt(mean_squared_error(y_val, y_pred))
        mlflow.log_metric("rmse", rmse)

        # Guardar preprocesador
        pathlib.Path("models").mkdir(exist_ok=True)
        with open("models/preprocessor.b", "wb") as f_out:
            pickle.dump(f_out)
        mlflow.log_artifact("models/preprocessor.b", artifact_path="preprocessor")

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
        name="google-stock-model-perfect"
    )
    model_name = "google-stock-model-perfect"
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
    mlflow.set_experiment(experiment_name="google-stock-model-prefect")

    # Paso 1: Lectura de datos
    df = read_data(CSV_PATH)

    # Paso 2: Agregar características
    X, y, dv = add_features(df)

    # Paso 3: Ajuste de hiperparámetros
    best_params = hyper_parameter_tuning(X, y, dv)

    # Paso 4: Entrenar el mejor modelo
    train_best_model(X, y, dv, best_params)

    # Paso 5: Registrar modelo
    register_model()


# Ejecutar el flujo principal
main_flow()



    





