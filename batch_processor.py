"""
Daily batch processing pipeline
"""
import os
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from review_fetcher import ReviewFetcher
from topic_extractor import TopicExtractor
from config import DATA_DIR, REVIEWS_DIR, TOPICS_DIR, START_DATE, ROLLING_WINDOW_DAYS


class BatchProcessor:
    """Processes daily batches of reviews"""
    
    def __init__(self, app_name: str, package_name: str):
        self.app_name = app_name
        self.package_name = package_name
        self.review_fetcher = ReviewFetcher(package_name)
        self.topic_extractor = TopicExtractor(app_name)
        
        # Ensure directories exist
        os.makedirs(REVIEWS_DIR, exist_ok=True)
        os.makedirs(TOPICS_DIR, exist_ok=True)
        
        # Load existing topic registry if available
        registry_path = os.path.join(TOPICS_DIR, f'topic_registry_{app_name}.json')
        if os.path.exists(registry_path):
            self.topic_extractor.load_topic_registry(registry_path)
    
    def process_daily_batch(self, target_date: datetime, fetch_if_missing: bool = True) -> pd.DataFrame:
        """
        Process reviews for a specific date
        
        Args:
            target_date: Date to process
            fetch_if_missing: Whether to fetch reviews if not found locally
            
        Returns:
            DataFrame with reviews and extracted topics
        """
        print(f"\n{'='*60}")
        print(f"Processing batch for {target_date.date()}")
        print(f"{'='*60}")
        
        # Try to load existing reviews
        reviews_df = self.review_fetcher.load_reviews(target_date, REVIEWS_DIR)
        
        # If not found and fetch_if_missing is True, fetch from Play Store
        if reviews_df is None and fetch_if_missing:
            print(f"Reviews not found locally. Fetching from Play Store...")
            reviews_df = self.review_fetcher.fetch_reviews_for_date(target_date)
            if reviews_df:
                reviews_df = pd.DataFrame(reviews_df)
                # Save fetched reviews
                self.review_fetcher.save_reviews(reviews_df, target_date, REVIEWS_DIR)
        
        if reviews_df is None or len(reviews_df) == 0:
            print(f"No reviews found for {target_date.date()}")
            return pd.DataFrame()
        
        # Extract topics
        reviews_df = self.topic_extractor.extract_topics_from_batch(reviews_df)
        
        # Save processed reviews with topics
        topics_file = os.path.join(TOPICS_DIR, f"topics_{target_date.date().isoformat()}.json")
        reviews_df.to_json(topics_file, orient='records', indent=2)
        
        # Save updated topic registry
        registry_path = os.path.join(TOPICS_DIR, f'topic_registry_{self.app_name}.json')
        self.topic_extractor.save_topic_registry(registry_path)
        
        print(f"Processed {len(reviews_df)} reviews")
        reviews_with_topics = reviews_df[reviews_df['topics'].apply(lambda x: len(x) > 0 if isinstance(x, list) else False)]
        print(f"Found {len(reviews_with_topics)} reviews with topics")
        
        return reviews_df
    
    def get_topic_frequencies_for_date(self, target_date: datetime) -> Dict[str, int]:
        """
        Get topic frequencies for a specific date
        
        Args:
            target_date: Date to get frequencies for
            
        Returns:
            Dictionary mapping topic names to frequencies
        """
        topics_file = os.path.join(TOPICS_DIR, f"topics_{target_date.date().isoformat()}.json")
        
        if not os.path.exists(topics_file):
            return {}
        
        reviews_df = pd.read_json(topics_file)
        
        # Count topic frequencies
        topic_counts = {}
        for _, row in reviews_df.iterrows():
            topics = row.get('topics', [])
            if isinstance(topics, list):
                for topic in topics:
                    topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        return topic_counts
    
    def get_all_topics(self) -> List[str]:
        """Get all topics from the registry"""
        return list(self.topic_extractor.get_topic_registry().keys())

