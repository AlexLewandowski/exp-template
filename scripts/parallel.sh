#!/usr/bin/env sh

if [ $# -eq 0 ]; then
    echo "Usage: $0 /path/to/json_file"
    exit 1
fi
json_file="$1"
num_jobs="$2"

base_name=$(basename "$json_file" .json)
dir="${json_file%/*}/"split_"${base_name}"

python configs/config_split.py $json_file

parallel --jobs $num_jobs --colsep ' ' bash scripts/run_single_experiment.sh {} {%} ::: "$dir"/"split_"*.json
