import json
import itertools
import os
import sys
import shutil


def find_list_args(data, prefix=""):
    list_args = {}
    if isinstance(data, dict):
        for key, value in data.items():
            new_prefix = f"{prefix}.{key}" if prefix else key
            list_args.update(find_list_args(value, new_prefix))
    elif isinstance(data, list):
        list_args[prefix] = data
    return list_args


def update_nested(data, path, value):
    keys = path.split(".")
    for key in keys[:-1]:
        data = data[key]
    data[keys[-1]] = value


def split_json(input_file):
    print(input_file)
    file_root = os.path.splitext(input_file)[0]
    file_root = os.path.split(file_root)[-1]
    output_dir = os.path.join("configs/split_" + file_root)

    # Remove existing directory if it exists
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    with open(input_file, "r") as f:
        data = json.load(f)

    list_args = find_list_args(data)
    combinations = list(itertools.product(*list_args.values()))

    os.makedirs(output_dir, exist_ok=True)

    for i, combo in enumerate(combinations):
        new_data = json.loads(json.dumps(data))  # Deep copy
        name_parts = []
        for path, value in zip(list_args.keys(), combo):
            update_nested(new_data, path, value)
            name_parts.append(f"{path}={value}")

        # if "config" in new_data and "name" in new_data["config"]:
        new_data["config"]["name"] = "_".join(name_parts)

        output_file = os.path.join(output_dir, f"split_{i+1}.json")
        with open(output_file, "w") as f:
            json.dump(new_data, f, indent=4)

        if i == 0:
            output_file = os.path.join(output_dir, f"debug.json")
            new_data["config"]["wandb"] = "debug"
            new_data["config"]["overwrite"] = "false"
            with open(output_file, "w") as f:
                json.dump(new_data, f, indent=4)

    print(f"Split into {len(combinations)} files in {output_dir}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <input_json_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    split_json(input_file)
