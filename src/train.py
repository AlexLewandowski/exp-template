#!/usr/bin/env python3

import pdb

import json
import argparse
import os

import equinox as eqx
import jax
import optax

import neptune
from .measurements.csv import save_experiment_config, save_metrics

parser = argparse.ArgumentParser()
parser.add_argument("experiment_config", type=str, help="Path to JSON config file")
args = parser.parse_args()
with open(args.experiment_config, "r") as f:
    experiment = json.load(f)

##
## WanDB logging setup
##

run = neptune.init_run(
    project="alexlewandowski/" + experiment["config"]["project"],
    name=experiment["config"]["name"],
    mode=experiment["config"]["wandb"],
)
run["parameters"] = experiment


experiment_file = os.path.join(
    "experiments",
    experiment["config"]["project"],
    experiment["config"]["name"],
    "measurements.csv",
)
save_experiment_config(
    experiment,
    os.path.join(
        "experiments", experiment["config"]["project"], experiment["config"]["name"]
    ),
    overwrite=experiment["config"]["overwrite"],
)

log_interval = experiment["config"]["log_interval"]
for iteration in range(experiment["config"]["num_iterations"]):

    print(f"Progress: {iteration}%", end="\r")
    if (
        iteration == 0  # Always log first iteration
        or iteration % log_interval == 0  # Regular interval
        or iteration
        == experiment["config"]["num_iterations"] - 1  # Always log last iteration
    ):

        metrics = {"iteration": iteration}
        save_metrics(metrics, experiment_file)
        run["metrics"].append(value=metrics, step=iteration)

run.stop()
