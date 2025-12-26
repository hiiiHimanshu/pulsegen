"""
Module to fetch Google Play Store reviews
"""
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from google_play_scraper import app, reviews, Sort
import pandas as pd
from tqdm import tqdm


class ReviewFetcher:
    """Fetches reviews from Google Play Store"""
    
    def __init__(self, package_name: str):
        self.package_name = package_name
        
    def fetch_reviews_for_date(self, target_date: datetime) -> List[Dict]:
        """
        Fetch reviews for a specific date
        
        Args:
            target_date: The date to fetch reviews for
            
        Returns:
            List of review dictionaries
        """
        all_reviews = []
        continuation_token = None
        
        # Fetch reviews in batches
        for _ in range(10):  # Limit to prevent excessive API calls
            try:
                result, continuation_token = reviews(
                    self.package_name,
                    lang='en',
                    country='in',
                    sort=Sort.NEWEST,
                    count=200,
                    continuation_token=continuation_token
                )
                
                # Filter reviews for the target date
                date_reviews = []
                for review in result:
                    review_date = datetime.fromtimestamp(review['at'] / 1000)
                    if review_date.date() == target_date.date():
                        date_reviews.append({
                            'review_id': review['reviewId'],
                            'content': review['content'],
                            'score': review['score'],
                            'thumbs_up': review['thumbsUpCount'],
                            'date': review_date.isoformat(),
                            'review_date': review_date.date().isoformat()
                        })
                
                all_reviews.extend(date_reviews)
                
                # If no continuation token or no more reviews for this date, break
                if not continuation_token:
                    break
                    
                # If we've gone past the target date, break
                if result and datetime.fromtimestamp(result[-1]['at'] / 1000).date() < target_date.date():
                    break
                    
            except Exception as e:
                print(f"Error fetching reviews: {e}")
                break
        
        return all_reviews
    
    def fetch_reviews_date_range(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        Fetch reviews for a date range
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            DataFrame with reviews
        """
        all_reviews = []
        current_date = start_date
        
        while current_date <= end_date:
            print(f"Fetching reviews for {current_date.date()}")
            date_reviews = self.fetch_reviews_for_date(current_date)
            all_reviews.extend(date_reviews)
            current_date += timedelta(days=1)
        
        return pd.DataFrame(all_reviews)
    
    def save_reviews(self, reviews_df: pd.DataFrame, date: datetime, output_dir: str):
        """Save reviews to JSON file"""
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f"reviews_{date.date().isoformat()}.json")
        reviews_df.to_json(file_path, orient='records', indent=2)
        print(f"Saved {len(reviews_df)} reviews to {file_path}")
    
    def load_reviews(self, date: datetime, input_dir: str) -> Optional[pd.DataFrame]:
        """Load reviews from JSON file"""
        file_path = os.path.join(input_dir, f"reviews_{date.date().isoformat()}.json")
        if os.path.exists(file_path):
            return pd.read_json(file_path)
        return None


