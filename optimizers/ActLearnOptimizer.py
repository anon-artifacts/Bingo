from pathlib import Path
import sys
# Add parent directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from optimizers.base_optimizer import BaseOptimizer
import active_learning.src.bl as bl        
class ActLearnOptimizer(BaseOptimizer):
    def __init__(self, config, model_wrapper, model_config, logging_util, seed):
        super().__init__(config, model_wrapper, model_config, logging_util, seed)
        self.best_config = None
        self.best_value = None
        self.config_space = None
    def optimize(self):
        config_dict =self.model_config.get_dataset_file()
        n_trials =  self.config['n_trials']
        data = bl.Data(bl.csv(config_dict))
        bl.the.Stop = n_trials
        res = bl.first(bl.actLearn(data, shuffle=True).best.rows )
        x_len = len(data.cols.x)
        self.best_config = dict(zip(data.cols.names[:x_len], res[:x_len]))
        self.best_value = bl.ydist(res,data)
        
        total_evaluations = n_trials
        print(f"Evaluated {total_evaluations} configurations")
        print(f"Found best config {self.best_config} with value: {self.best_value}")
        
   