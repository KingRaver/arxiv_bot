import logging
from anthropic import Anthropic

class ClaudeHandler:
   def __init__(self):
       self.client = Anthropic(api_key=your_anthropic_api_key_here)
       logging.info("Claude handler initialized")

   def generate_tweet(self, prompt):
       try:
           logging.info(f"Generating tweet for prompt: {prompt}")
           response = self.client.messages.create(
               model="claude-3-haiku-20240307",
               max_tokens=100,
               messages=[{
                   "role": "user",
                   "content": f"""Create a tweet based on this prompt: {prompt}
                   Requirements:
                   - Original and intellectual
                   - Reflect specified style and tone
                   - Under 280 characters
                   - Include 2-3 relevant hashtags
                   - No quotation marks"""
               }]
           )
           tweet = self._format_response(response.content[0].text)
           logging.info(f"Generated tweet: {tweet}")
           return tweet
       except Exception as e:
           logging.error(f"Tweet generation error: {e}")
           return ""

   def _format_response(self, response):
       # Remove quotes and extra spaces
       cleaned = response.strip().strip('"').strip()
       if len(cleaned) > 280:
           cleaned = cleaned[:277] + "..."
       return cleaned
