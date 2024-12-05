import numpy as np
import os

def inspect_dataset(file_path):
    """
    Inspects the structure of the dataset.
    """
    try:
        # Load the dataset
        data = np.load(file_path)
        
        # Basic information
        shape = data.shape
        missing_values = np.sum(np.isnan(data))
        summary = {
            "mean": np.nanmean(data, axis=0).tolist(),
            "std": np.nanstd(data, axis=0).tolist(),
            "min": np.nanmin(data, axis=0).tolist(),
            "max": np.nanmax(data, axis=0).tolist()
        }
        
        return {
            "file": file_path,
            "shape": shape,
            "missing_values": missing_values,
            "summary": summary
        }
    except Exception as e:
        return {
            "file": file_path,
            "error": str(e)
        }

def main():
    # Define the directory containing your .npy files
    directory = "./"  # Update this to the directory where your files are located
    output_file = "dataset_inspection_output.txt"
    
    results = []
    for file_name in os.listdir(directory):
        if file_name.endswith(".npy"):
            file_path = os.path.join(directory, file_name)
            result = inspect_dataset(file_path)
            results.append(result)
    
    # Save results to a text file
    with open(output_file, "w") as f:
        for result in results:
            f.write(str(result) + "\n\n")
    
    print(f"Inspection complete. Results saved to {output_file}")

if __name__ == "__main__":
    main()
