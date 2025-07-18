import torch
import sys
import os

def inspect_pickle_file(file_path):
    """
    Loads a pickle file, handling PyTorch-specific serialization and persistent IDs,
    and prints its contents.
    """
    print(f"Attempting to load pickle file with torch: {file_path}")

    # The individual binary data files are in a 'data' subdirectory
    # relative to the main pickle file.
    base_dir = os.path.dirname(file_path)
    data_dir = os.path.join(base_dir, 'data')

    def persistent_load_func(pid):
        """This function is called by pickle when it finds a persistent ID.
           It loads the corresponding binary file.
        """
        # The persistent ID is the filename in the 'data' directory.
        file_path = os.path.join(data_dir, str(pid))
        try:
            with open(file_path, 'rb') as f:
                # The individual files are also torch-serialized
                return torch.load(f, map_location=torch.device('cpu'))
        except FileNotFoundError:
            print(f"[persistent_load] Error: Could not find file {file_path}")
            return None
        except Exception as e:
            print(f"[persistent_load] Error loading file {file_path}: {e}")
            return None

    try:
        # Pass the custom loader to torch.load
        data = torch.load(file_path, map_location=torch.device('cpu'), persistent_load=persistent_load_func)

        print("\nSuccessfully loaded the file with torch using persistent_load.")
        print("-" * 40)
        
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

            # Inspect the first element of the 'train' list
            if 'train' in data and isinstance(data['train'], list) and data['train']:
                print("\n--- Inspecting first element of 'train' list ---")
                first_element = data['train'][0]
                print(f"Type of first element: {type(first_element)}")
                
                # If it's a tuple or list, print its contents
                if isinstance(first_element, (list, tuple)):
                    print(f"Length of first element: {len(first_element)}")
                    for i, item in enumerate(first_element):
                        print(f"  Item {i}:")
                        print(f"    Type: {type(item)}")
                        if hasattr(item, 'shape'):
                            print(f"    Shape: {item.shape}")
                        else:
                            # Truncate long strings for readability
                            item_repr = repr(item)
                            if len(item_repr) > 100:
                                print(f"    Value (truncated): {item_repr[:100]}...")
                            else:
                                print(f"    Value: {item_repr}")
                else:
                    print(f"Content of first element: {first_element}")
                print("\n--- Deeper inspection of the first element ---")
                # The Data object acts like a dictionary
                for key, value in first_element.items():
                    print(f"\nAttribute key: '{key}'")
                    print(f"  Type: {type(value)}")
                    if isinstance(value, torch.Tensor):
                        print(f"  Shape: {value.shape}")
                    elif isinstance(value, (list, tuple)):
                        print(f"  Length: {len(value)}")
                    else:
                        print(f"  Value: {value}")

                # Also check for non-standard attributes that might not be in .keys()
                print("\n--- Checking for other non-tensor attributes ---")
                for attr in dir(first_element):
                    if not attr.startswith('_') and attr not in first_element.keys():
                        try:
                            value = getattr(first_element, attr)
                            if not isinstance(value, torch.Tensor) and not callable(value):
                                print(f"  {attr}: {value}")
                        except Exception:
                            continue

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
    pickle_file = 'all_datasets/data.pkl'
    inspect_pickle_file(pickle_file)
