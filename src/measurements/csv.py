#!/usr/bin/env python3

import os
import shutil
import json
import csv

def save_experiment_config(experiment_config, output_dir, overwrite=False):
    """
    Save experiment configuration details

    Args:
        experiment_config (dict): Full experiment configuration
        output_dir (str): Directory to save configuration
    """
    if overwrite:
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.makedirs(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    config_filename = os.path.join(output_dir, "experiment_config.json")

    if os.path.exists(config_filename) and not overwrite:
        raise FileExistsError(
            f"Config file already exists: {config_filename}. Use overwrite=True to replace."
        )

    with open(config_filename, "w") as f:
        json.dump(experiment_config, f, indent=4)


def save_metrics(metrics_dict, experiment_file="metrics.csv"):
    """
    Save metrics to CSV, dynamically creating headers from dictionary keys

    Args:
        metrics_dict (dict): Dictionary of metric names and their values
        metric_file (str): Path to CSV file
    """
    os.makedirs(os.path.dirname(experiment_file), exist_ok=True)
    file_exists = os.path.exists(experiment_file)

    with open(experiment_file, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(metrics_dict.keys()))

        # Write headers only if file is new
        if not file_exists:
            writer.writeheader()

        writer.writerow(metrics_dict)
