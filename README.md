# Install requirements

``` sh
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

To install jax with GPU support:

``` sh
pip install -U "jax[cuda12]"
```

# Running jobs on a single server

``` sh
# With screen
screen -S experiment_session
scripts/parallel.sh jsonpath numjobs
# Detach with Ctrl-A, D
# Reatach:
screen -r

# With tmux
tmux new-session -s experiment_session
scripts/parallel.sh jsonpath numjobs
# Detach with Ctrl-B, D
# Reattach:
tmux attach-session
```

# Running an experiment

``` sh
python -m src.train configs/test.json
```

# Generating a plot

``` sh
python analysis/experiment_test.py
```
