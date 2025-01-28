import os
from dotenv import load_dotenv
import logging

class Config:
    # Load environment variables
    load_dotenv()

    # Twitter credentials
    TWITTER_USERNAME = os.getenv('TWITTER_USERNAME')
    TWITTER_PASSWORD = os.getenv('TWITTER_PASSWORD')

    # NASA API
    NASA_API_KEY = os.getenv('NASA_API_KEY')

    @classmethod
    def validate(cls):
        """Validate all required environment variables are set"""
        required_vars = [
            'TWITTER_USERNAME',
            'TWITTER_PASSWORD',
            'NASA_API_KEY'
        ]

        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )

        logging.info("Config validation successful")
