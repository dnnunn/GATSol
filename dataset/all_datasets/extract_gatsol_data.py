import torch
import csv
import sys

def extract_data_to_csv(pickle_path, output_csv_path):
    """
    Loads the GATSol pickle file and extracts solubility labels and sequence lengths
    into a CSV file.
    """
    print(f"Loading data from: {pickle_path}")
    try:
        data = torch.load(pickle_path, map_location=torch.device('cpu'))
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    print(f"Writing extracted data to: {output_csv_path}")
    try:
        with open(output_csv_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            # Write header
            writer.writerow(['split', 'item_index', 'solubility_label', 'sequence_length'])

            # Iterate through each data split ('train', 'test', etc.)
            for split_name, data_list in data.items():
                print(f"Processing {len(data_list)} items from '{split_name}' split...")
                for i, item in enumerate(data_list):
                    # Extract the solubility label (y)
                    # .item() gets the Python number from a single-element tensor
                    solubility_label = item.y.item() if hasattr(item, 'y') and item.y is not None else 'N/A'
                    
                    # Extract the number of nodes (sequence length)
                    seq_length = item.num_nodes if hasattr(item, 'num_nodes') else 'N/A'
                    
                    writer.writerow([split_name, i, solubility_label, seq_length])
        
        print("\nExtraction complete.")

    except Exception as e:
        print(f"An error occurred during CSV writing: {e}")

if __name__ == "__main__":
    pickle_file = 'GATSol_datasets.pkl'
    output_csv_file = 'gatsol_extracted_data.csv'
    extract_data_to_csv(pickle_file, output_csv_file)
