import csv
import os

class LoggingUtil:
    def __init__(self, log_file="log.csv"):
        self.iteration = 0  # Counter for iterations
        self.is_logging = False  # Flag to track whether logging is active
        self.log_file = log_file  # Path to the log file

    def _ensure_path_exists(self):
        """Ensure the directory for the log file exists."""
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
    def start_logging(self):
        """Start logging and reset the iteration counter."""
        self.iteration = 0
        self.is_logging = True
        self._ensure_path_exists()
        # Initialize the CSV file with a header
        with open(self.log_file, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["iteration", "config", "value", "elapsed_time"])
        
        print(f"Logging started. Logs will be saved to '{self.log_file}'. Iteration counter reset to zero.")

    def log(self, config, value, elapsed_time):
        """Log the current iteration, configuration, and evaluation value."""
        if not self.is_logging:
            raise RuntimeError("Logging is not active. Call 'start_logging()' first.")
        
        # Convert config to a string representation for storage
        config_str = str(config)
        elapsed_time_str = str(elapsed_time)
        value = str(value)
        # Write the log entry to the CSV file
        with open(self.log_file, mode="a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([self.iteration, config_str, value, elapsed_time_str])
        
        print(f"Logged Iteration {self.iteration}: Config={config}, Value={value}, Elapsed Time={elapsed_time}")
        self.iteration += 1

    def stop_logging(self):
        """Stop logging and reset the iteration counter."""
        self.is_logging = False
        self.iteration = 0
        print(f"Logging stopped. Logs saved to '{self.log_file}'. Iteration counter reset to zero.")
