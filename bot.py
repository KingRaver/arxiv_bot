import logging
import time
import json
import os
import random
from datetime import datetime, timedelta
from src.config import Config
from src.utils.scraper import TweetScraper
from src.utils.arxiv import ArxivHandler
from src.utils.nasa import NASAHandler

class PostTracker:
    def __init__(self, storage_file="posted_content.json"):
        self.storage_file = storage_file
        self.posted_content = self._load_posted()
        self.clean_old_entries()  # Clean old entries on init
        logging.info("PostTracker initialized")

    def _load_posted(self):
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def _save_posted(self):
        with open(self.storage_file, 'w') as f:
            json.dump(self.posted_content, f)

    def clean_old_entries(self, days=30):
        """Remove entries older than specified days"""
        now = datetime.now()
        to_remove = []
        
        for content_id, data in self.posted_content.items():
            posted_date = datetime.fromisoformat(data['timestamp'])
            if (now - posted_date) > timedelta(days=days):
                to_remove.append(content_id)
                
        for content_id in to_remove:
            del self.posted_content[content_id]
            
        if to_remove:
            self._save_posted()
            logging.info(f"Cleaned {len(to_remove)} old entries")

    def is_duplicate(self, content_id: str) -> bool:
        return content_id in self.posted_content

    def mark_as_posted(self, content_id: str) -> None:
        self.posted_content[content_id] = {
            'timestamp': datetime.now().isoformat()
        }
        self._save_posted()

class TwitterBot:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.tweet_interval = 60  # 1 minute between posts
        self.max_retries = 3  # Maximum number of retries for getting content
        Config.validate()
        self.scraper = TweetScraper()
        self.arxiv = ArxivHandler()
        self.nasa = NASAHandler(Config.NASA_API_KEY)
        self.post_tracker = PostTracker()
        self.current_source = 'nasa'  # Start with NASA content
        logging.info("Bot initialized")

    def switch_source(self) -> None:
        self.current_source = 'arxiv' if self.current_source == 'nasa' else 'nasa'
        logging.info(f"Switched content source to: {self.current_source}")

    def get_nasa_content(self, attempt=1):
        """Get NASA content with multiple attempts"""
        content_types = ['apod', 'mars']
        random.shuffle(content_types)  # Randomize order
        
        for nasa_type in content_types:
            if nasa_type == 'apod':
                # Try different dates for APOD
                for _ in range(min(5, attempt)):  # Try up to 5 different dates
                    offset = random.randint(0, 30)  # Random day within last month
                    date = (datetime.now() - timedelta(days=offset)).strftime('%Y-%m-%d')
                    data = self.nasa.get_apod(date=date)
                    if data and not self.post_tracker.is_duplicate(f"nasa_apod_{date}"):
                        return {
                            'id': f"nasa_apod_{date}",
                            'type': 'nasa_apod',
                            'data': data
                        }
            else:
                # Try different Mars photos
                data = self.nasa.get_random_mars_photo()
                if data and not self.post_tracker.is_duplicate(f"nasa_mars_{data.get('id')}"):
                    return {
                        'id': f"nasa_mars_{data.get('id')}",
                        'type': 'nasa_mars',
                        'data': data
                    }
        return None

    def get_content(self):
        """Get content with retry logic"""
        for attempt in range(1, self.max_retries + 1):
            try:
                if self.current_source == 'nasa':
                    content = self.get_nasa_content(attempt)
                else:
                    # Try different arXiv categories
                    data = self.arxiv.get_random_paper()
                    if data and not self.post_tracker.is_duplicate(f"arxiv_{data['id']}"):
                        content = {
                            'id': f"arxiv_{data['id']}",
                            'type': 'arxiv',
                            'data': data
                        }
                    else:
                        content = None

                if content:
                    return content
                elif attempt < self.max_retries:
                    logging.info(f"Retry attempt {attempt} for content")
                    time.sleep(2)  # Short delay between retries
                    
            except Exception as e:
                logging.error(f"Error getting content (attempt {attempt}): {e}")
                if attempt == self.max_retries:
                    self.switch_source()  # Try other source if all attempts fail
                    return self.get_content()
        
        return None

    def format_content(self, content):
        try:
            if content['type'] == 'nasa_apod':
                return self.nasa.format_apod_tweet(content['data'])
            elif content['type'] == 'nasa_mars':
                return self.nasa.format_mars_tweet(content['data'])
            elif content['type'] == 'arxiv':
                return self.arxiv.format_paper_tweet(content['data'])
            return None
        except Exception as e:
            logging.error(f"Error formatting content: {e}")
            return None

    def run_scheduled(self):
        while True:
            try:
                logging.info(f"Starting tweet cycle (current source: {self.current_source})")
                if not self.scraper.is_logged_in:
                    logging.info("Logging in...")
                    self.scraper.login_twitter(Config.TWITTER_USERNAME, Config.TWITTER_PASSWORD)

                content = self.get_content()
                if content:
                    tweet_text = self.format_content(content)
                    if tweet_text:
                        success = self.scraper.post_tweet(tweet_text)
                        if success:
                            self.post_tracker.mark_as_posted(content['id'])
                            self.switch_source()
                            logging.info(f"Tweet posted successfully: {tweet_text}")
                        else:
                            logging.error("Failed to post tweet")
                    else:
                        logging.error("Failed to format tweet")
                else:
                    logging.error("Failed to get content after all retries")
                    self.switch_source()  # Try other source next time

                logging.info("Waiting for next cycle...")
                time.sleep(self.tweet_interval)
            except Exception as e:
                logging.error(f"Cycle error: {e}")
                time.sleep(300)  # 5 min retry delay

    def close(self):
        self.scraper.close()

if __name__ == "__main__":
    bot = TwitterBot()
    try:
        bot.run_scheduled()
    except KeyboardInterrupt:
        logging.info("Bot stopped by user")
        bot.close()
