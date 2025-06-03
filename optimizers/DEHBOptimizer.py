import time
from optimizers.base_optimizer import BaseOptimizer
from ConfigSpace import ConfigurationSpace
from ConfigSpace.configuration import Configuration
import random
from dehb import DEHB
import uuid
class CustomConfigurationSpace(ConfigurationSpace):
    def __init__(self, predefined_configs, mapping = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.predefined_configs = predefined_configs
        self.mapping = mapping
    
    def set_mapping(self, mapping):
        self.mapping = mapping
    
    def get_mapping(self):
        if self.mapping is None:
            return None
        return self.mapping
    
    def sample_configuration(self, size=1):
        # Sample configurations from the predefined list
        if size == 1:
            sampled_dict = random.sample(self.predefined_configs, size)
            sample = sampled_dict[0]
            return Configuration(self, values=sample)
        else:
            sample_dicts = random.sample(self.predefined_configs, size)
            samples=[]
            for sample in sample_dicts:
                samples.append(Configuration(self, values=sample))
            return samples
        
class DEHBOptimizer(BaseOptimizer):
    def __init__(self, config, model_wrapper, model_config, logging_util, seed):
        super().__init__(config, model_wrapper, model_config, logging_util, seed)
        self.best_config = None
        self.best_value = None
        self.config_space = None
    def optimize(self):
        
        if not self.logging_util:
            raise ValueError("logging utils not set!!")
        def objective(x: Configuration, fidelity: float, config_dict = None, **kwargs):
            # Replace this with your actual objective value (y) and cost.
            
            if not config_dict:
                config_dict =self.model_config.cs_to_dict(x)
            #print(config_dict)
            # start_in= time.time()
            score = self.model_wrapper.run_model(config_dict)
            #end = time.time()
            #self.logging_util.log(config_dict, (1-score), end-start_time)
            return {"fitness": (1-score), "cost": 1}
        print("Starting DEHB optimization")
        n_trials =  self.config['n_trials']
        #start_time = time.time()
        output_directory = f"{self.config['output_directory']}/{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
        random.seed(self.seed)
        #hyperparameter_dict = self.model_config.get_hyperparam_dict()
        config_space, param_names, space = self.model_config.get_configspace()
        self.config_space = self.create_configspace(config_space, param_names, space) 
        min_vals = [float('inf')] * len(param_names)
        max_vals = [float('-inf')] * len(param_names)

        
        
        for index, (name, values) in enumerate(self.model_config.get_hyperparam_dict().items()):
            if isinstance(values[0], (int, float)):
                min_vals[index] = min(values)
                max_vals[index] = max(values)
        
        rows = list(zip(*space))
        rows = [list(item) for item in rows]
        data = Data(rows, min_vals, max_vals)
   
        dehb = DEHB(
            f=objective, 
            cs=self.config_space, 
            min_fidelity=1, 
            max_fidelity=10,
            n_workers=1,
            seed=self.seed,
            output_path=output_directory
        )
        self.logging_util.start_logging()
        print(f"Starting DEHB optimization with {n_trials} trials")
        for _ in range(n_trials):
            #while True:
            #    job_info = dehb.ask()
            #    config = job_info["config"]
            #    config_dict =self.model_config.cs_to_dict(config)
            #    if config_dict in self.config_space.predefined_configs:
            #        break
            job_info = dehb.ask()
            config = job_info["config"]
            config_dict =self.model_config.cs_to_dict(config)
            config_values = [config_dict[key] for key in param_names]
            row = data.nearestRow(config_values)
            config_dict = dict(zip(param_names, row))
            result = objective(None, job_info["fidelity"], config_dict= config_dict)
            dehb.tell(job_info, result)
        # Run the optimizer
        #traj, runtime, history = dehb.run(fevals = n_trials)
        """
        traj, runtime, history = dehb.traj, dehb.runtime, dehb.history
        best_config = dehb.vector_to_configspace(dehb.inc_config)
        row = data.nearestRow(best_config)
        best_config = str(dict(zip(param_names, row)))
        print(f"Best config: {best_config}")
        self.best_config = best_config.get_dictionary()
        self.best_value = objective(best_config, 0.0)['fitness']
        total_evaluations = len(history)
        print(f"Evaluated {total_evaluations} configurations")
        print(f"Found best config {self.best_config} with value: {self.best_value}")
        self.logging_util.stop_logging()
        """
        traj, runtime, history = dehb.traj, dehb.runtime, dehb.history
        best_config = dehb.vector_to_configspace(dehb.inc_config)
        best_config_values = [best_config.get_dictionary()[key] for key in param_names]
        row = data.nearestRow(best_config_values)
        self.best_config = dict(zip(param_names, row))
        self.best_value = objective(None, 0.0, config_dict=self.best_config)['fitness']
        total_evaluations = len(history)
        print(f"Evaluated {total_evaluations} configurations")
        print(f"Found best config {self.best_config} with value: {self.best_value}")
        self.logging_util.stop_logging()
        
    def create_configspace(self, config_space, param_names, space):
        #print(self.model_config.get_hyperparam_dict())
        combined_space = list(zip(*self.model_config.get_hyperparam_dict().values()))
        config_dict = [dict(zip(param_names, values)) for values in combined_space]
        #random.shuffle(config_dict)
        #config_dict = config_dict[:20000]
        #print(config_dict)
        cs = CustomConfigurationSpace(config_dict)
        for hyperparameter in config_space.get_hyperparameters():
            cs.add_hyperparameter(hyperparameter)
        # Convert each parameter to a CategoricalHyperparameter
       
        return cs
    

class Data:
    def __init__(self, rows, min_vals, max_vals):
        self.rows = rows  # List of data points
        self.min_vals = min_vals  # Min values for normalization
        self.max_vals = max_vals
    
    
    def normalize(self, value, feature_index):
            """Normalize a numerical value between 0 and 1."""
            if value == "?":
                return "?"

            min_val, max_val = self.min_vals[feature_index], self.max_vals[feature_index]
            return (value - min_val) / (max_val - min_val) if max_val > min_val else 0

    def dist(self, a, b, index):
        if a == "?" and b == "?":
            return 1 
        if isinstance(a, str) and isinstance(b, str):
            return 0 if a == b else 1
        a, b = self.normalize(a, index), self.normalize(b, index)
        if a == "?":
            a = 1 if b < 0.5 else 0  # Handle missing a
        if b == "?":
            b = 1 if a < 0.5 else 0  # Handle missing b
        return abs(a - b)

    def xdist(self, p1, p2, p =2):
        #return sum((a - b) ** 2 for a, b in zip(p1, p2)) ** 0.5
        n = 0
        d = 0
        for a, b in zip(p1, p2):
            d += abs(self.dist(a, b, n)) ** p
            n += 1
        return (d / n) ** (1 / p) if n > 0 else 0
    
    def nearestRow(self, target_row):
        """Find the row nearest to the target_row."""
        best_dist = float("inf")
        nearest = None
        for row in self.rows:
            if row == target_row:
                continue
            dist = self.xdist(target_row, row)
            if dist < best_dist:
                best_dist = dist
                nearest = row
        return nearest