import os
import time
from tqdm import tqdm
from utils import (
    init_driver,
    get_ticker_list,
)
import logging
from tqdm import tqdm
from threading import Thread
from queue import Queue
from tqdm import tqdm
import os
import time

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s:%(levelname)s:%(message)s")


def file_exists(download_dir, filename):
    """Check if a file exists in the directory."""
    return filename in os.listdir(download_dir)


def wait_for_download(download_dir, possible_filenames, timeout=10):
    """Wait for a file to appear in the directory within a specified timeout."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        time.sleep(1)  # sleep for a second before trying each time
        for filename in possible_filenames:
            if file_exists(download_dir, filename):
                return filename
        logging.info("Could not find file. Waiting 1 second...")
    return None


def download_with_retry(driver, url, download_dir, filenames, max_retries=3):
    """Attempt to download a file with retries."""
    for attempt in range(max_retries):
        driver.get(url)
        downloaded_file = wait_for_download(download_dir, filenames)
        if downloaded_file:
            return downloaded_file
        else:
            logging.warning(
                f"Retry {attempt + 1} for {filenames}. Waiting 5 seconds..."
            )
            time.sleep(5)
    return None


def scrape_worker(sublist, results_queue, download_dir, progress_bar):
    driver = init_driver(download_dir)
    file_names = []

    for symbol in sublist:
        try:
            data_url = f"https://query1.finance.yahoo.com/v7/finance/download/{symbol}?period1=0&period2=16993152000&interval=1d&events=history&includeAdjustedClose=true"
            filenameU = f"{symbol.upper()}.csv"
            filenameL = f"{symbol.lower()}.csv"
            file_name = download_with_retry(
                driver, data_url, download_dir, [filenameU, filenameL]
            )
            if file_name:
                file_names.append(file_name)
        except Exception as e:
            logging.error(f"Error downloading data for symbol {symbol}: {e}")
        finally:
            # Update the progress bar safely within the thread
            progress_bar.update(1)

    driver.quit()
    results_queue.put(file_names)


def scrape_urls(ticker_list, num_threads=5, download_dir="./downloads"):
    # if download_dir does not exist, create it
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    download_dir = os.path.abspath(download_dir)
    chunk_size = len(ticker_list) // num_threads + (len(ticker_list) % num_threads > 0)
    chunks = [
        ticker_list[i : i + chunk_size] for i in range(0, len(ticker_list), chunk_size)
    ]

    threads = []
    results_queue = Queue()
    final_results = []

    # Create a shared tqdm progress bar
    pbar = tqdm(total=len(ticker_list))

    for chunk in chunks:
        thread = Thread(
            target=scrape_worker, args=(chunk, results_queue, download_dir, pbar)
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # Close the progress bar after all threads are done
    pbar.close()

    while not results_queue.empty():
        final_results.extend(results_queue.get())

    return final_results


ticker_list = get_ticker_list()
# check what we have already downloaded
download_dir = "./downloads"
downloaded_files = os.listdir(download_dir)
downloaded_tickers = [f.split(".")[0].lower() for f in downloaded_files]
# remove already downloaded tickers
ticker_list = [t for t in ticker_list if t.lower() not in downloaded_tickers]
print(len(ticker_list))
# scrape the remaining tickers
# scrape_urls(ticker_list, num_threads=5)
