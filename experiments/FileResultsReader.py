import os
import csv
import argparse

def read_second_row(folder_name, data_file_path, budget):
    dataset_name = os.path.splitext(os.path.basename(data_file_path))[0]
    file_path = os.path.join(folder_name, f"{dataset_name}_{budget}.csv")
    
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return None
    
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            rows = list(csv_reader)
            if len(rows) < 3:
                print("Error: The file is misformatted")
                return None
            return rows[1][:20], rows[2][:20]
    except Exception as e:
        print(f"Error reading the file: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Read the second row of a CSV file.")
    parser.add_argument("--folder_name", required=True, help="The folder containing the CSV file.")
    parser.add_argument("--data_file_path", required=True, help="The full path of the data file.")
    parser.add_argument("--budget", required=True, help="The budget (suffix of the file).")
    args = parser.parse_args()
    
    second_row = read_second_row(args.folder_name, args.data_file_path, args.budget)
    if second_row:
        print(second_row)
