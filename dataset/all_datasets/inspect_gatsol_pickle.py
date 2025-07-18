import torch
import sys

def inspect_pickle_file(file_path):
    """
    Loads a pickle file using torch and prints information about its contents.
    """
    print(f"Attempting to load pickle file with torch: {file_path}")
    try:
        # Use torch.load and map_location to ensure it loads on CPU
        data = torch.load(file_path, map_location=torch.device('cpu'))
        
        print("\nSuccessfully loaded the file with torch.")
        print("----------------------------------------")
        
        print(f"Type of loaded data: {type(data)}")
        
        if isinstance(data, dict):
            print(f"Data is a dictionary with {len(data)} keys.")
            print("Keys:", list(data.keys()))
            # Print info about the items
            for key, value in data.items():
                print(f"\n--- Content for key '{key}' ---")
                print(f"  Type: {type(value)}")
                if hasattr(value, '__len__'):
                    print(f"  Length: {len(value)}")
                if hasattr(value, 'shape'):
                    print(f"  Shape: {value.shape}")

        elif isinstance(data, list):
            print(f"Data is a list with {len(data)} elements.")
            # Print info about the first element
            if data:
                print("\nExample content of the first element:")
                print(f"  Type: {type(data[0])}")
                if hasattr(data[0], '__len__'):
                    print(f"  Length: {len(data[0])}")
                if hasattr(data[0], 'shape'):
                    print(f"  Shape: {data[0].shape}")

        elif hasattr(data, 'shape'): # For numpy arrays, torch tensors
             print(f"Data has shape: {data.shape}")

        else:
            print("Data is of a custom or basic type.")

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    pickle_file = 'GATSol_datasets.pkl'
    inspect_pickle_file(pickle_file)
