import pdb

import os
import pandas as pd
import json
import numpy as np

import matplotlib.pyplot as plt
import matplotlib as mpl

my_colors = [
    "#D55E00",
    "#E69F00",
    "#56B4E9",
    "#009E73",
    "#F0E442",
    "#0072B2",
    "#CC79A7",
    "#000000",
    "#999999",
    "#D35400",
    "#2ECC71",
    "#005555",
]


def flatten_json(json_data, prefix=""):
    flattened = {}
    for key, value in json_data.items():
        new_key = f"{prefix}{key}" if prefix else key

        if isinstance(value, dict):
            flattened.update(flatten_json(value, new_key + "_"))
        else:
            flattened[new_key] = value

    return flattened


def load_experiment_data(base_dir):
    configs = []
    results = []
    idx = 0
    for subdir in os.listdir(base_dir):
        config_path = os.path.join(base_dir, subdir, "experiment_config.json")
        results_path = os.path.join(base_dir, subdir, "measurements.csv")

        with open(config_path) as f:
            config = flatten_json(json.load(f))

        result = pd.read_csv(results_path)

        configs.append(config)

        results.append(result)
        idx += 1

    return pd.DataFrame(configs), results


def apply_conditions(df, conditions):
    result = df.copy()
    for column, values in conditions:
        if values is None:  # Skip filtering for this column
            continue
        elif isinstance(values, list):
            result = result[result[column].isin(values)]
        else:
            result = result[result[column] == values]
    return result


def flatten_name(config, cols):
    name = []
    for col in cols:
        name.append(config[col])
    return name


def filter_results(conditions, configs, results, name_dict=None):
    filtered_configs = apply_conditions(configs, conditions)
    grouped_configs = filtered_configs.drop(columns=["config_seed"])
    grouped_configs = grouped_configs.drop(columns=["config_name"])

    unique_indices = (
        grouped_configs.groupby(grouped_configs.columns.tolist())
        .apply(lambda x: x.index.tolist(), include_groups=False)
        .tolist()
    )

    filtered_columns = grouped_configs.columns[grouped_configs.nunique() > 1].values
    print("Columns with more than one value: ")

    for col in filtered_columns:
        vals = list(set(grouped_configs[col].values))
        vals.sort()
        print('    ["', col, '", ', vals, "]", sep="")

    names = [flatten_name(configs.iloc[i[0]], filtered_columns) for i in unique_indices]
    if name_dict is not None:
        names = [[name_dict[name[0]]] for name in names]

    filtered_results = [
        {
            "mean": pd.concat([results[i] for i in unique_indices[n]])
            .groupby(level=0)
            .mean(),
            "std": pd.concat([results[i] for i in unique_indices[n]])
            .groupby(level=0)
            .std(),
            "xs": results[unique_indices[n][0]]["iteration"],
            "num_samples": len(unique_indices[n]),
            "name": names[n],
        }
        for n in range(len(unique_indices))
    ]

    return filtered_results


def sensitivity_aggregation(x):
    x = x.values
    try:
        index = np.where(x == 1.0)[0][0]
    except:
        index = len(x) + 100
    return index / len(x)


def filter_sensitivity_results(
    conditions, sensitivity_parameter, configs, results, name_dict=None
):
    filtered_configs = apply_conditions(configs, conditions)
    grouped_configs = filtered_configs.drop(columns=["config_seed"])
    grouped_configs = grouped_configs.drop(columns=["config_name"])
    temporary_grouped_configs = grouped_configs.drop(columns=[sensitivity_parameter])

    sensitivity_values = filtered_configs[sensitivity_parameter].unique()
    sensitivity_values.sort()

    filtered_columns = temporary_grouped_configs.columns[
        temporary_grouped_configs.nunique() > 1
    ].values

    print("Columns with more than one value: ")
    for col in filtered_columns:
        vals = list(set(temporary_grouped_configs[col].values))
        vals.sort()
        print('    ["', col, '", ', vals, "]", sep="")

    temporary_unique_indices = (
        temporary_grouped_configs.groupby(temporary_grouped_configs.columns.tolist())
        .apply(lambda x: x.index.tolist(), include_groups=False)
        .tolist()
    )
    names = [
        flatten_name(configs.iloc[i[0]], filtered_columns)
        for i in temporary_unique_indices
    ]
    if name_dict is not None:
        names = [[name_dict[name[0]]] for name in names]

    unique_indices = []
    for local_unique_indices in temporary_unique_indices:
        split_unique_indices = []
        temporary_configs = grouped_configs.loc[local_unique_indices]
        for sensitivity_value in sensitivity_values:
            split_configs = temporary_configs[
                temporary_configs[sensitivity_parameter] == sensitivity_value
            ]
            split_unique_index = (
                split_configs.groupby(split_configs.columns.tolist())
                .apply(lambda x: x.index.tolist(), include_groups=False)
                .tolist()
            )
            split_unique_indices.append(split_unique_index[0])
        unique_indices.append(split_unique_indices)

    filtered_results = [
        {
            "mean": pd.concat(
                [
                    pd.concat(
                        [
                            results[i]
                            .apply(lambda x: sensitivity_aggregation(x))
                            .to_frame()
                            .T
                            for i in local_unique_indices
                        ]
                    )
                    .groupby(level=0)
                    .mean()
                    for local_unique_indices in unique_indices[n]
                ],
                keys=sensitivity_values,
                names=[sensitivity_parameter],
            ),
            "std": pd.concat(
                [
                    pd.concat(
                        [
                            results[i]
                            .apply(lambda x: sensitivity_aggregation(x))
                            .to_frame()
                            .T
                            for i in local_unique_indices
                        ]
                    )
                    .groupby(level=0)
                    .std()
                    for local_unique_indices in unique_indices[n]
                ],
                keys=sensitivity_values,
                names=[sensitivity_parameter],
            ),
            "xs": sensitivity_values,
            "num_samples": len(unique_indices[n][0]),
            "name": names[n],
            "sensitivity_parameter": sensitivity_parameter,
        }
        for n in range(len(unique_indices))
    ]

    return filtered_results, sensitivity_values


def plot_filtered_results(
    filtered_results,
    measurement="offline_total_acc",
    ylabel="Total Accuracy",
    xlabel="Iterations",
    title="",
    base_dir="plots",
    ylims=None,
    xlims=None,
    linewidth=5,
    fillalpha=0.2,
    legend_fontsize=24,
    legend_ncol=1,
    label_fontsize=24,
    ticks_fontsize=20,
    xscale=None,
    xticks=None,
    legend=True,
    optional=None,
    filename="plot",
):
    plt.rcParams["pdf.fonttype"] = 42
    # plt.figure(figsize=(10, 6))
    fig, ax = plt.subplots(figsize=(10, 6))

    i = 0
    for result in filtered_results:
        mean = result["mean"][measurement]
        std = result["std"][measurement]
        name = " ".join(map(str, result["name"]))

        x = result["xs"]
        n = result["num_samples"]
        ax.plot(x, mean, label=f"{name}", linewidth=linewidth, color=my_colors[i])
        ax.fill_between(
            x, mean - std / n, mean + std / n, alpha=fillalpha, color=my_colors[i]
        )
        i += 1

    ax.set_title(title)
    ax.set_xlabel(xlabel, fontsize=label_fontsize)
    ax.set_ylabel(ylabel, fontsize=label_fontsize)
    if legend:
        ax.legend(
            fontsize=legend_fontsize, ncol=legend_ncol, frameon=False, fancybox=False
        )
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if xscale is not None:
        ax.set_xscale(xscale)
    if xticks is not None:
        ax.set_xticks(xticks)
        ax.get_xaxis().set_major_formatter(mpl.ticker.ScalarFormatter())
    ax.tick_params(axis="x", labelsize=ticks_fontsize)
    ax.tick_params(axis="y", labelsize=ticks_fontsize)
    if ylims is not None:
        ax.set_ylim(ylims)  # e.g., plt.ylim(0, 100)
    if xlims is not None:
        ax.set_xlim(xlims)  # e.g., plt.ylim(0, 100)
        ax.minorticks_off()
    fig.tight_layout()
    if optional is not None:
        optional(ax)

    # Create plots directory if it doesn't exist
    os.makedirs(base_dir, exist_ok=True)

    # Save plot
    filename = os.path.join(base_dir, f"{filename}.pdf")
    fig.savefig(filename)
    plt.close(fig)  # Close the plot to free memory
