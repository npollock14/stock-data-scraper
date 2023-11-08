import os


def bytes_to_human_readable(num, suffix="B"):
    """Convert bytes to human-readable format."""
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


download_dir = "./downloads"
downloaded_files = os.listdir(download_dir)
downloaded_tickers = [f.split(".")[0].lower() for f in downloaded_files]
# Calculate file sizes
file_sizes = [os.path.getsize(f"{download_dir}/{f}") for f in downloaded_files]

# Compute analytics
total_size = sum(file_sizes)
min_size = min(file_sizes) if file_sizes else 0
max_size = max(file_sizes) if file_sizes else 0
average_size = total_size / len(downloaded_files) if downloaded_files else 0

# Display analytics
print(f"Total size of downloaded files: {bytes_to_human_readable(total_size)}")
print(f"Min size of downloaded files: {bytes_to_human_readable(min_size)}")
print(f"Max size of downloaded files: {bytes_to_human_readable(max_size)}")
print(f"Average size of downloaded files: {bytes_to_human_readable(average_size)}")
print(f"Number of files downloaded: {len(downloaded_files)}")
