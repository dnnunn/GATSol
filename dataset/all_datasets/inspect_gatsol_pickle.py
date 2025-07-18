import pickle
import sys

def inspect_pickle_file(file_path):
    """
    Loads a pickle file and prints information about its contents.
    """
    print(f"Attempting to load pickle file: {file_path}")
    try:
        with open(file_path, 'rb') as f:
            # Use encoding='latin1' which is common for older pickle files, especially in ML.
            data = pickle.load(f, encoding='latin1')
        
        print("\nSuccessfully loaded the pickle file.")
        print("-----------------------------------")
        
        print(f"Type of loaded data: {type(data)}")
        
        if isinstance(data, dict):
            print(f"Data is a dictionary with {len(data)} keys.")
            print("Keys:", list(data.keys()))
            # Print info about the first item
            if data:
                first_key = list(data.keys())[0]
                print(f"\nExample content for key '{first_key}':")
                print(f"  Type: {type(data[first_key])}")
                if hasattr(data[first_key], '__len__'):
                    print(f"  Length: {len(data[first_key])}")

        elif isinstance(data, list):
            print(f"Data is a list with {len(data)} elements.")
            # Print info about the first element
            if data:
                print("\nExample content of the first element:")
                print(f"  Type: {type(data[0])}")
                if hasattr(data[0], '__len__'):
                    print(f"  Length: {len(data[0])}")

        elif hasattr(data, 'shape'): # For numpy arrays, torch tensors
             print(f"Data has shape: {data.shape}")

        else:
            print("Data is of a custom or basic type.")

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except pickle.UnpicklingError as e:
        print(f"Error unpickling the file: {e}")
        print("This could be due to a corrupted file, a version mismatch, or if it requires a specific library (like torch) to load.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    pickle_file = 'dataset/all_datasets/data.pkl'
    inspect_pickle_file(pickle_file)
