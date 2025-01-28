import arxiv
import random
import logging
import re
from typing import Optional, Dict, Any, List

class ArxivHandler:
    def __init__(self):
        self.categories = [
            'cs.CL',    # Computation and Language
            'cs.AI',    # Artificial Intelligence
            'cs.LG',    # Machine Learning
            'cs.CV',    # Computer Vision
            'stat.ML'   # Statistics - Machine Learning
        ]
        logging.info("ArxivHandler initialized")

    def sanitize_text(self, text: str) -> str:
        """Remove or replace problematic characters"""
        replacements = {
            '−': '-',    # minus sign
            '›': '>',    # quotation mark
            '‹': '<',    # quotation mark
            '"': '"',    # fancy quotes
            '"': '"',
            ''': "'",
            ''': "'",
            '×': 'x',    # multiplication
            '∞': 'inf',  # infinity
            '≈': '~',    # approximately
            '≤': '<=',   # less than or equal
            '≥': '>=',   # greater than or equal
            'μ': 'u',    # mu
            'α': 'alpha',
            'β': 'beta',
            'γ': 'gamma',
            'θ': 'theta'
        }
        
        # Apply replacements
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Remove any remaining non-ASCII characters
        text = ''.join(char for char in text if ord(char) < 128)
        
        # Clean up any double spaces
        text = ' '.join(text.split())
        
        return text

    def get_random_paper(self) -> Optional[Dict[Any, Any]]:
        """Fetch a random paper from specified categories"""
        try:
            category = random.choice(self.categories)
            
            search = arxiv.Search(
                query=f"cat:{category}",
                max_results=100,
                sort_by=arxiv.SortCriterion.SubmittedDate
            )
            
            results = list(search.results())
            if not results:
                logging.error(f"No papers found in category {category}")
                return None
            
            paper = random.choice(results)
            
            return {
                'id': paper.entry_id.split('/')[-1],
                'title': self.sanitize_text(paper.title),
                'authors': self.sanitize_text(', '.join([author.name for author in paper.authors])),
                'url': paper.entry_id,
                'abstract': self.sanitize_text(paper.summary),
                'category': category
            }
            
        except Exception as e:
            logging.error(f"Error fetching paper: {e}")
            return None

    def format_paper_tweet(self, paper: Dict[str, Any]) -> Optional[str]:
        """Format paper details into a tweet"""
        try:
            title = paper['title']
            if len(title) > 100:
                title = title[:97] + "..."

            tweet = f"{title}\n\n"
            tweet += f"By: {paper['authors'][:100]}...\n\n" if len(paper['authors']) > 100 else f"By: {paper['authors']}\n\n"
            tweet += f"Link: {paper['url']}"

            if len(tweet) > 280:
                tweet = tweet[:277] + "..."

            return tweet

        except Exception as e:
            logging.error(f"Error formatting tweet: {e}")
            return None

    def get_related_paper(self, topics: List[str]) -> Optional[Dict[str, Any]]:
        """Get a paper related to specific topics"""
        try:
            # Construct search query from topics
            query = ' OR '.join([f'"{topic}"' for topic in topics])
            
            search = arxiv.Search(
                query=query,
                max_results=50,
                sort_by=arxiv.SortCriterion.Relevance
            )
            
            results = list(search.results())
            if not results:
                return None
                
            # Choose from top 5 most relevant results
            paper = random.choice(results[:5])
            
            return {
                'id': paper.entry_id.split('/')[-1],
                'title': self.sanitize_text(paper.title),
                'authors': self.sanitize_text(', '.join([author.name for author in paper.authors])),
                'url': paper.entry_id,
                'abstract': self.sanitize_text(paper.summary),
                'category': paper.primary_category
            }
            
        except Exception as e:
            logging.error(f"Error fetching related paper: {e}")
            return None
