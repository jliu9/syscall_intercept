import os
import sys


def get_directory_stats(directory):
    total_files = 0
    total_dirs = 0
    total_size = 0

    for root, dirs, files in os.walk(directory):
        total_files += len(files)
        total_dirs += len(dirs) + 1  # Include the current root directory
        for file in files:
            filepath = os.path.join(root, file)
            if os.path.isfile(
                    filepath):  # Ensure it's not a symbolic link or similar
                total_size += os.path.getsize(filepath)

    # Avoid division by zero
    average_files = total_files / total_dirs if total_dirs else 0
    average_size = total_size / total_files if total_files else 0

    return total_files, total_dirs, average_files, average_size


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <directory>")
        sys.exit(1)

    directory = sys.argv[1]
    if not os.path.isdir(directory):
        print("The specified path is not a directory.")
        sys.exit(1)

    total_files, total_dirs, average_files, average_size = get_directory_stats(
        directory)

    print(f"Total number of files: {total_files}")
    print(
        f"Total number of directories (including subdirectories): {total_dirs}")
    print(f"Average number of files per directory: {average_files:.2f}")
    print(f"Average file size: {average_size:.2f} bytes")
