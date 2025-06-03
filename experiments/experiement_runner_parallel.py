from pathlib import Path
import sys
# Add parent directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import os
import signal
import time
from models.configurations.model_config_static import ModelConfigurationStatic
from models.model_wrapper_static import ModelWrapperStatic
from optimizers.ActLearnOptimizer import ActLearnOptimizer
from optimizers.DEHBOptimizer import DEHBOptimizer
from utils.LoggingUtil import LoggingUtil
from utils.data_loader_templated import load_data
import glob
from tqdm import tqdm
seed = None

hyperparameter_configs = {}


def write_to_file(filepath, content):
    # Ensure the parent directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Write content to the file
    with open(filepath, 'w') as file:
        file.write(content)

def init_optimizer(optimizer_name, optimizer_config, model_wrapper, seed=1):
    """Initialize optimizer based on its name and configuration."""
    optimizer_classes = {
        'DEHB': DEHBOptimizer,
        'Active_Learning': ActLearnOptimizer,
    }
    if optimizer_name not in optimizer_classes:
        return None
    
    #initially set model_config to zero, and set after getting seeds
    return optimizer_classes[optimizer_name](optimizer_config, model_wrapper, None, None, seed)

            
def checkFileExists(hyperparam_model_path):
    return (os.path.exists(hyperparam_model_path) and os.path.isfile(hyperparam_model_path))

# Main function to prepare and run optimizers
def run_experiment(datasets, optimizers, repeats, checkpoints, tmp_output_dir, logging_dir):
    dataset_files = []

    if isinstance(datasets, str) and os.path.isdir(datasets):
        # It's a directory, collect all CSV files
        for root, _, _ in os.walk(datasets):
            dataset_files.extend(glob.glob(os.path.join(root, "*.csv")))
    else:
        if isinstance(datasets, str):
            dataset_files = [datasets]  # single file as string
        else:
            dataset_files = datasets  # list of files
    for dataset_file in dataset_files:   
        optimize_single_dataset(optimizers, repeats, checkpoints, tmp_output_dir, logging_dir, dataset_file)
        
# Wrapper function for parallel execution
def run_repeat_wrapper(args):
    (logging_dir, data_name, dataset_file, hyperparameter_configs, model_wrapper,
    optimizer, checkpoint, optimizer_name, i) = args

    elapsed_time, best_config, best_value = run_single_repeat(
        logging_dir, data_name, dataset_file, hyperparameter_configs,
        model_wrapper, optimizer, checkpoint, optimizer_name, i
    )

    return str(best_config), str(best_value), str(elapsed_time)

def optimize_single_dataset(optimizers, repeats, checkpoints, tmp_output_dir, logging_dir, dataset_file):
    
    def terminate_all_processes(signum, frame):
        print("Terminating all processes...")
        sys.exit(0)
        
    data_name = get_file_name(dataset_file)
    
    X, Y = load_data(dataset_file)
    hyperparameter_configs = {col: list((X[col].tolist())) for col in X.columns}
    model_wrapper = ModelWrapperStatic(X, Y)
    for optimizer in optimizers:
        if optimizer.get('disable'): continue
        for checkpoint in checkpoints:
            if optimizer:
                optimizer_name = optimizer['name']
                if tmp_output_dir: results_filepath = os.path.join(tmp_output_dir, optimizer_name,  f"{data_name}_{checkpoint}.csv")
                if tmp_output_dir and checkFileExists(results_filepath):
                    continue
                
                optimizer['n_trials'] = checkpoint
                print(f'Running {optimizer_name}')
                results = {key: [] for key in ["configs", "best_values", "runtimes"]}
                    
                #Prepare arguments
                args_list = [
                    (logging_dir, data_name, dataset_file, hyperparameter_configs, model_wrapper,
                    optimizer, checkpoint, optimizer_name, i)
                    for i in range(repeats)
                ]
                # Register the signal handler for Ctrl+C
                signal.signal(signal.SIGINT, terminate_all_processes)
                with ProcessPoolExecutor() as executor:
                    # Submit all tasks
                    futures = [executor.submit(run_repeat_wrapper, args) for args in args_list]
                    try:
                        # Progress bar for completed tasks
                        for future in tqdm(as_completed(futures), total=len(futures), desc=f"{optimizer_name} {checkpoint}"):
                            best_config, best_value, elapsed_time = future.result()
                            metrics = [best_config, best_value, elapsed_time]

                            for key, value in zip(results.keys(), map(str, metrics)):
                                results[key].append(value)
                    except KeyboardInterrupt:
                        print("\nProcess interrupted, cleaning up...")
                        executor.shutdown(wait=False)
                        sys.exit(0)
                content = '\n'.join([', '.join(results[key]) for key in results])
                if tmp_output_dir: write_to_file(results_filepath, content)

def run_single_repeat(logging_dir, data_name, dataset_file, hyperparameter_configs, model_wrapper, optimizer, checkpoint, optimizer_name, i):
    seed = i+1
    optimizer_log_filename = os.path.join(logging_dir,optimizer_name, f"{data_name}_{seed}.csv")
    hyperconfigs = ModelConfigurationStatic(hyperparameter_configs, dataset_file, seed)
    optimizer = init_optimizer(optimizer_name, optimizer, model_wrapper)
    optimizer.set_seed(seed)
    optimizer.set_model_config(hyperconfigs)
    optimizer.set_logging_util(LoggingUtil(optimizer_log_filename))
    start_time = time.time()
    optimizer.optimize()
    elapsed_time = time.time() - start_time
    best_config, best_value, elapsed_time = optimizer.best_config, optimizer.best_value, elapsed_time
    print(f'Best config for {optimizer_name} for {data_name}: {best_config}, completed in {elapsed_time:.2f}s')
    return elapsed_time,best_config,best_value

def get_file_name(dataset_file):
    dataset_file_name = os.path.basename(dataset_file)
    data_name = os.path.splitext(dataset_file_name)[0]
    return data_name

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the experiment with the specified configuration.")

    # Add arguments for each of the required parameters
    parser.add_argument('--datasets', type=str, help='Datasets to use for the experiment')
    parser.add_argument('--output_directory', type=str, help='Directory for output results')
    parser.add_argument('--name', type=str, help='Name to be included in the optimizer dictionary')

    parser.add_argument('--repeats', type=int, help='Number of repeats for the experiment')
    parser.add_argument('--budget', type=int, nargs='+', help='budgets', default=None)
    parser.add_argument('--runs_output_folder', type=str, help='Output folder for the experiment runs')
    parser.add_argument('--logging_folder', type=str, help='Logging folder for experiment logs')

    # Parse the command-line arguments
    args = parser.parse_args()
    config = {}
    
    optimizer_config = {}
    if args.name and args.output_directory:
        optimizer_config['name'] = args.name
        optimizer_config['output_directory'] = args.output_directory
        
    # Run the experiment with the provided arguments or defaults
    run_experiment(
        datasets=args.datasets or config['datasets'],
        optimizers=[optimizer_config] or config['optimizer'],
        repeats=args.repeats or config['repeats'],
        checkpoints=args.budget or config.get('checkpoints'),
        tmp_output_dir=args.runs_output_folder or (config['runs_output_folder'] if config and 'runs_output_folder' in config else None),
        logging_dir=args.logging_folder or config['logging_folder']
    )
