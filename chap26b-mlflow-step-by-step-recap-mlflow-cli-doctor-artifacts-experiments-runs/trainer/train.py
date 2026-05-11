"""Seed a couple of runs in experiment 'experiment_cli_demo' so the MLflow CLI
demos in chap26b have something to inspect.

Same shape as chap25/chap26's trainer (context manager + main()).
"""
import argparse
import logging
import os
import warnings

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)


def eval_metrics(actual, pred):
    rmse = np.sqrt(mean_squared_error(actual, pred))
    mae = mean_absolute_error(actual, pred)
    r2 = r2_score(actual, pred)
    return rmse, mae, r2


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--alpha", type=float, required=False, default=0.4)
    parser.add_argument("--l1_ratio", type=float, required=False, default=0.4)
    parser.add_argument(
        "--experiment-name",
        type=str,
        required=False,
        default="experiment_cli_demo",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    warnings.filterwarnings("ignore")
    np.random.seed(40)

    data = pd.read_csv("data/red-wine-quality.csv")
    train, test = train_test_split(data)

    train_x = train.drop(["quality"], axis=1)
    test_x = test.drop(["quality"], axis=1)
    train_y = train[["quality"]]
    test_y = test[["quality"]]

    mlflow.set_tracking_uri(
        os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
    )
    print("Tracking URI:", mlflow.get_tracking_uri())

    experiment = mlflow.set_experiment(experiment_name=args.experiment_name)
    print("Experiment   :", experiment.name, "(id =", experiment.experiment_id, ")")

    with mlflow.start_run(experiment_id=experiment.experiment_id) as run:
        lr = ElasticNet(
            alpha=args.alpha, l1_ratio=args.l1_ratio, random_state=42
        )
        lr.fit(train_x, train_y)

        predicted_qualities = lr.predict(test_x)
        rmse, mae, r2 = eval_metrics(test_y, predicted_qualities)

        print(
            f"ElasticNet model (alpha={args.alpha:.4f}, "
            f"l1_ratio={args.l1_ratio:.4f}) -> rmse={rmse:.4f} "
            f"mae={mae:.4f} r2={r2:.4f}"
        )

        mlflow.log_params({"alpha": args.alpha, "l1_ratio": args.l1_ratio})
        mlflow.log_metrics({"rmse": rmse, "mae": mae, "r2": r2})
        mlflow.set_tags(
            {
                "stage": "cli-demo-seed",
                "source": "chap26b-trainer",
            }
        )

        mlflow.sklearn.log_model(lr, artifact_path="model")

        print("Seeded run id:", run.info.run_id)


if __name__ == "__main__":
    main()
