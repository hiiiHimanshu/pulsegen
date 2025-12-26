"""
Generate sample review data for testing purposes
"""
import os
import json
import random
import pandas as pd
from datetime import datetime, timedelta
from config import REVIEWS_DIR, START_DATE

# Sample review templates with topics
SAMPLE_REVIEWS = [
    ("Delivery was very late today. Had to wait for more than an hour.", ["Late delivery", "Delivery issue"]),
    ("Food was stale and tasted bad. Very disappointed.", ["Food stale", "Food quality poor"]),
    ("Delivery guy was rude and unprofessional. Very bad experience.", ["Delivery partner rude"]),
    ("App keeps crashing when I try to place an order.", ["App crash"]),
    ("Payment failed multiple times. Very frustrating.", ["Payment issue"]),
    ("Wrong order was delivered. Got someone else's food.", ["Wrong order delivered"]),
    ("Maps not working properly. Delivery partner couldn't find my location.", ["Maps not working properly"]),
    ("Food quality was poor. Not worth the money.", ["Food quality poor"]),
    ("Customer service is unresponsive. No one answers calls.", ["Customer service unresponsive"]),
    ("Refund not processed even after cancellation.", ["Refund not processed"]),
    ("Promo code not working. Tried multiple times.", ["Promo code not working"]),
    ("Order was cancelled without any reason.", ["Order cancellation"]),
    ("Instamart should be open all night. Very inconvenient.", ["Instamart should be open all night"]),
    ("Bring back 10 minute bolt delivery. It was so convenient!", ["Bring back 10 minute bolt delivery"]),
    ("Delivery partner behaved badly. Very impolite.", ["Delivery partner rude"]),
    ("The delivery person was disrespectful and rude.", ["Delivery partner rude"]),
    ("Food arrived cold and stale.", ["Food stale", "Food quality poor"]),
    ("App freezes every time I open it.", ["App crash"]),
    ("Location on map is wrong. Delivery partner went to wrong place.", ["Maps not working properly"]),
    ("Great app! Love the service.", []),
    ("Fast delivery and good food quality.", []),
    ("Best food delivery app!", []),
]


def generate_sample_reviews_for_date(target_date: datetime, num_reviews: int = 50) -> pd.DataFrame:
    """Generate sample reviews for a specific date"""
    reviews = []
    
    for i in range(num_reviews):
        # Randomly select a review template
        review_text, topics = random.choice(SAMPLE_REVIEWS)
        
        # Add some variation
        if random.random() < 0.3:
            review_text = review_text + " " + random.choice([
                "Very disappointed.",
                "Will not order again.",
                "Please fix this issue.",
                "Need improvement.",
                "Thanks for the service."
            ])
        
        # Create review entry
        review = {
            'review_id': f"sample_{target_date.date().isoformat()}_{i}",
            'content': review_text,
            'score': random.randint(1, 5),
            'thumbs_up': random.randint(0, 10),
            'date': target_date.isoformat(),
            'review_date': target_date.date().isoformat(),
            'topics': topics
        }
        reviews.append(review)
    
    return pd.DataFrame(reviews)


def generate_sample_data(start_date: datetime, end_date: datetime, reviews_per_day: int = 50):
    """Generate sample data for a date range"""
    os.makedirs(REVIEWS_DIR, exist_ok=True)
    
    current_date = start_date
    while current_date <= end_date:
        print(f"Generating sample reviews for {current_date.date()}")
        reviews_df = generate_sample_reviews_for_date(current_date, reviews_per_day)
        
        file_path = os.path.join(REVIEWS_DIR, f"reviews_{current_date.date().isoformat()}.json")
        reviews_df.to_json(file_path, orient='records', indent=2)
        print(f"  Generated {len(reviews_df)} reviews")
        
        current_date += timedelta(days=1)
    
    print(f"\nSample data generation complete!")
    print(f"Generated reviews from {start_date.date()} to {end_date.date()}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate sample review data')
    parser.add_argument('--start-date', type=str, default='2024-06-01', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, default='2024-06-30', help='End date (YYYY-MM-DD)')
    parser.add_argument('--reviews-per-day', type=int, default=50, help='Number of reviews per day')
    
    args = parser.parse_args()
    
    start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
    end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
    
    generate_sample_data(start_date, end_date, args.reviews_per_day)


