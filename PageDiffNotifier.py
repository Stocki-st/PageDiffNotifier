import requests
import hashlib
import os
import time

def get_website_content(url):
    response = requests.get(url)
    response.raise_for_status() 
    return response.text

def hash_content(content):
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def load_previous_hash(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return file.read().strip()
    return None

def save_current_hash(file_path, current_hash):
    with open(file_path, 'w') as file:
        file.write(current_hash)

def check_website_change(url, hash_file):
    current_content = get_website_content(url)
    current_hash = hash_content(current_content)

    previous_hash = load_previous_hash(hash_file)

    if previous_hash is None:
        print(f"No previous hash found for {url}. Saving current hash.")
        save_current_hash(hash_file, current_hash)
    elif current_hash != previous_hash:
        print(f"The website {url} has changed!")
        save_current_hash(hash_file, current_hash)
    else:
        print(f"No changes detected for {url}.")

def load_watchlist(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return [line.strip() for line in file.readlines()]
    return []

def save_watchlist(file_path, watchlist):
    with open(file_path, 'w') as file:
        for url in watchlist:
            file.write(url + '\n')

def add_watcher(file_path, url):
    watchlist = load_watchlist(file_path)
    if url not in watchlist:
        watchlist.append(url)
        save_watchlist(file_path, watchlist)
        print(f"Added {url} to watchlist.")
    else:
        print(f"{url} is already in the watchlist.")

def remove_watcher(file_path, url):
    watchlist = load_watchlist(file_path)
    if url in watchlist:
        watchlist.remove(url)
        save_watchlist(file_path, watchlist)
        print(f"Removed {url} from watchlist.")
    else:
        print(f"{url} is not in the watchlist.")

def check_all_websites(watchlist_file):
    watchlist = load_watchlist(watchlist_file)
    for url in watchlist:
        hash_file_path = f'hash_{url.replace("https://", "").replace("http://", "").replace("/", "_")}.txt'
        check_website_change(url, hash_file_path)

if __name__ == "__main__":
    watchlist_file = 'watchlist.txt'  # File to store the list of websites to watch

 
    add_watcher(watchlist_file, 'https://orf.at')

    # Remove a website from watch
    # remove_watcher(watchlist_file, 'https://example.com')

    while True:
        print("Checking for website changes...")
        check_all_websites(watchlist_file)
        print("Waiting for 10 minutes before the next check...")
        time.sleep(600)  # Sleep for 600 seconds (10 minutes)