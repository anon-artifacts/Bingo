DATASETS_DIR = data/moot/optimize/
COMMAND_FILE = commands.sh
NAME ?= DEHB
BASE_CMD = python3 experiement_runner_parallel.py --name $(NAME) --repeats 20 --budget 6 12 18 24 50 100 200 --runs_output_folder ../results/results_$(NAME) --logging_folder ../logging/logging_$(NAME) --output_directory ../results/tmp/$(NAME)_tmp
generate-commands:
	@echo "#!/bin/bash" > $(COMMAND_FILE)
	@find $(DATASETS_DIR) -type f -name "*.csv" | while read dataset; do \
		echo "$(BASE_CMD) --datasets ../$$dataset;" >> $(COMMAND_FILE); \
	done
	@echo "wait" >> $(COMMAND_FILE)
	@chmod +x $(COMMAND_FILE)
	@mv $(COMMAND_FILE) experiments/$(COMMAND_FILE)
run-commands:
	@nohup ./$(COMMAND_FILE) > run.log 2>&1 &
	@echo "Commands are running in the background. Output is in run.log"