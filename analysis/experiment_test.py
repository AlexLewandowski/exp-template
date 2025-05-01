import os

from plot_results import load_experiment_data,\
    filter_results, filter_sensitivity_results, plot_filtered_results

base_dir = 'test'

###
### Print all conditions
###

if not os.path.exists('plots/' + base_dir):
    conditions = []
    configs, results = load_experiment_data('experiments/' + base_dir)
    filtered_results = filter_results(conditions, configs, results)

conditions = [
    ]
configs, results = load_experiment_data('experiments/' + base_dir)
filtered_results = filter_results(conditions, configs, results)
plot_filtered_results(filtered_results, measurement='iteration', ylabel='Iteration', base_dir = 'plots/' + base_dir, filename='test')

