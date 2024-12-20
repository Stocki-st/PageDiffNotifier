import requests
import hashlib
import os
import asyncio
import signal
from telegram_bot import TelegramNotifier
from config import TELEGRAM_BOT_TOKEN, CHAT_ID

class PageDiffNotifier:
    def __init__(self, watchlist_file='watchlist.txt'):
        self.watchlist_file = watchlist_file
        self.notifier = TelegramNotifier(TELEGRAM_BOT_TOKEN, CHAT_ID)
        self.watchlist = self.load_watchlist()

    def get_website_content(self, url):
        response = requests.get(url)
        response.raise_for_status() 
        return response.text

    def hash_content(self, content):
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def load_previous_hash(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                return file.read().strip()
        return None

    def save_current_hash(self, file_path, current_hash):
        with open(file_path, 'w') as file:
            file.write(current_hash)

    async def check_website_change(self, url):
        current_content = self.get_website_content(url)
        current_hash = self.hash_content(current_content)

        hash_file = f'hash_{url.replace("https://", "").replace("http://", "").replace("/", "_")}.txt'
        previous_hash = self.load_previous_hash(hash_file)

        if previous_hash is None:
            print(f"No previous hash found for {url}. Saving current hash.")
            self.save_current_hash(hash_file, current_hash)
        elif current_hash != previous_hash:
            message = f"The website {url} has changed!"
            print(message)
            await self.notifier.send_message(message)
            self.save_current_hash(hash_file, current_hash)
        else:
            print(f"No changes detected for {url}.")

    def load_watchlist(self):
        if os.path.exists(self.watchlist_file):
            with open(self.watchlist_file, 'r') as file:
                return [line.strip() for line in file.readlines()]
        return []

    def get_watchlist(self):
        return self.watchlist 

    def save_watchlist(self):
        with open(self.watchlist_file, 'w') as file:
            for url in self.watchlist:
                file.write(url + '\n')

    def add_watcher(self, url):
        if url not in self.watchlist:
            self.watchlist.append(url)
            self.save_watchlist()
            print(f"Added {url} to watchlist.")
        else:
            print(f"{url} is already in the watchlist.")

    def remove_watcher(self, url):
        if url in self.watchlist:
            self.watchlist.remove(url)
            self.save_watchlist()
            print(f"Removed {url} from watchlist.")
        else:
            print(f"{url} is not in the watchlist.")

    async def check_all_websites(self):
        for url in self.watchlist:
            await self.check_website_change(url)

    async def run(self):
        message = "Page Diff notifier started!"
        await self.notifier.send_message(message)
        
        try:
            while True:
                print("Checking for website changes...")
                await self.check_all_websites()
                print("Waiting for 10 minutes before the next check...")
                await asyncio.sleep(600)  # Sleep for 600 seconds (10 minutes)
        except asyncio.CancelledError:
            print("Main loop cancelled, shutting down...")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

# If you want to run the notifier in a standalone mode
if __name__ == "__main__":
    notifier = PageDiffNotifier()
    asyncio.run(notifier.run())