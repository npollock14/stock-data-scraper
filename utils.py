import undetected_chromedriver as uc
import time
import os
import time
import json
import requests
import random


def get_ticker_list(
    source_url="https://raw.githubusercontent.com/rreichel3/US-Stock-Symbols/main/nasdaq/nasdaq_tickers.txt",
    cache_path="ticker_cache.json",
    cache_duration=86400,  # Cache duration in seconds (1 day)
):
    # Check if cache file exists and is not expired
    if os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            try:
                cache_data = json.load(f)
                # Check if cached data is not expired and the URL matches
                if (
                    time.time() - cache_data["timestamp"] < cache_duration
                    and cache_data["source_url"] == source_url
                ):
                    return cache_data["ticker_list"]
            except json.JSONDecodeError:
                # If JSON is corrupt, ignore cache and fetch new data
                pass

    # If cache is invalid or doesn't exist, fetch new data and update cache
    return fetch_and_cache_tickers(source_url, cache_path)


def fetch_and_cache_tickers(source_url, cache_path):
    # make request to get the list of tickers
    r = requests.get(source_url)
    ticker_list = r.text.split("\n")
    # Remove empty lines
    ticker_list = [t.strip() for t in ticker_list if t]

    # Prepare cache data with timestamp and source URL
    cache_data = {
        "source_url": source_url,
        "timestamp": time.time(),
        "ticker_list": ticker_list,
    }

    # Write the fresh list of tickers and metadata to cache file
    with open(cache_path, "w") as f:
        json.dump(cache_data, f)

    return ticker_list


def init_driver(download_dir="./downloads", retries=5, delay=5):
    for i in range(retries):
        try:
            chrome_options = uc.ChromeOptions()
            chrome_options.headless = True
            # Disable cache
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-cache")
            chrome_options.add_argument("--disable-application-cache")
            chrome_options.add_experimental_option(
                "prefs",
                {
                    "download.default_directory": download_dir,
                    "profile.default_content_settings.cookies": 2,  # disable cookies
                    "profile.default_content_settings.images": 2,  # disable images to speed up loading
                },
            )
            driver = uc.Chrome(options=chrome_options)
            return driver
        except Exception:
            print(f"Failed to start driver, retrying ({i + 1}/{retries})")
            if i < retries - 1:  # i is 0 indexed
                time.sleep(random.random() * delay)
                continue
            else:
                raise

    print("!!!Could not start driver!!!")
    exit(1)
