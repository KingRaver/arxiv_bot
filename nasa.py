import requests
import logging
import random
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

class NASAHandler:
    def __init__(self, api_key: str):
        """Initialize NASA API handler"""
        self.api_key = api_key
        self.base_url = "https://api.nasa.gov"
        self.endpoints = {
            'apod': '/planetary/apod',
            'mars': '/mars-photos/api/v1/rovers/curiosity/photos'
        }
        logging.info("NASAHandler initialized")

    def sanitize_text(self, text: str) -> str:
        """Clean and format text for tweets"""
        if not text:
            return ""
            
        # Remove any problematic characters or formatting
        text = text.replace('\n', ' ').replace('\r', '')
        text = ' '.join(text.split())  # Remove extra whitespace
        return text

    def get_apod(self, date: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get NASA's Astronomy Picture of the Day"""
        try:
            params = {
                'api_key': self.api_key,
                'thumbs': True  # Get thumbnail URL for videos
            }
            
            if date:
                params['date'] = date

            response = requests.get(
                f"{self.base_url}{self.endpoints['apod']}", 
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Clean up data for tweet
            if 'explanation' in data:
                data['explanation'] = self.sanitize_text(data['explanation'])
            if 'title' in data:
                data['title'] = self.sanitize_text(data['title'])
                
            return data

        except Exception as e:
            logging.error(f"Error fetching APOD: {e}")
            return None

    def get_random_mars_photo(self) -> Optional[Dict[str, Any]]:
        """Get a random Mars Rover (Curiosity) photo"""
        try:
            # Get a random date within Curiosity's mission
            start_date = datetime(2012, 8, 6)  # Curiosity landing date
            end_date = datetime.now()
            random_date = start_date + timedelta(
                days=random.randint(0, (end_date - start_date).days)
            )

            params = {
                'api_key': self.api_key,
                'earth_date': random_date.strftime('%Y-%m-%d')
            }

            response = requests.get(
                f"{self.base_url}{self.endpoints['mars']}", 
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            if data['photos']:
                photo = random.choice(data['photos'])
                # Add formatted date to photo data
                photo['formatted_date'] = datetime.strptime(
                    photo['earth_date'], '%Y-%m-%d'
                ).strftime('%B %d, %Y')
                return photo
                
            return None

        except Exception as e:
            logging.error(f"Error fetching Mars photo: {e}")
            return None

    def format_apod_tweet(self, data: Dict[str, Any]) -> Optional[str]:
        """Format APOD data into a tweet"""
        try:
            title = data.get('title', 'Astronomy Picture of the Day')
            if len(title) > 100:
                title = title[:97] + "..."

            # Use appropriate URL based on media type
            url = data.get('url', '')
            if data.get('media_type') == 'video':
                url = data.get('thumbnail_url', url)

            tweet = f"NASA's Astronomy Picture of the Day\n\n"
            tweet += f"{title}\n\n"
            
            # Add date if available
            if 'date' in data:
                formatted_date = datetime.strptime(
                    data['date'], '%Y-%m-%d'
                ).strftime('%B %d, %Y')
                tweet += f"Date: {formatted_date}\n"
            
            tweet += f"Link: {url}"

            if len(tweet) > 280:
                tweet = tweet[:277] + "..."

            return tweet

        except Exception as e:
            logging.error(f"Error formatting APOD tweet: {e}")
            return None

    def format_mars_tweet(self, data: Dict[str, Any]) -> Optional[str]:
        """Format Mars photo data into a tweet"""
        try:
            camera_name = data.get('camera', {}).get('full_name', 'Curiosity Rover Camera')
            date = data.get('formatted_date', data.get('earth_date', ''))
            
            tweet = f"Mars Curiosity Rover\n\n"
            tweet += f"Captured by: {camera_name}\n"
            if date:
                tweet += f"Date: {date}\n\n"
            tweet += f"Link: {data.get('img_src', '')}"

            if len(tweet) > 280:
                tweet = tweet[:277] + "..."

            return tweet

        except Exception as e:
            logging.error(f"Error formatting Mars tweet: {e}")
            return None
