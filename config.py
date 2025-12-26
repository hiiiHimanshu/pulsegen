"""
Configuration file for the Play Store Review Trend Analysis System
"""
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# App configuration
APP_CONFIGS = {
    'swiggy': {
        'package_name': 'in.swiggy.android',
        'app_name': 'Swiggy'
    },
    'zomato': {
        'package_name': 'com.application.zomato',
        'app_name': 'Zomato'
    }
}

# Seed topics for initial categorization
SEED_TOPICS = {
    'swiggy': [
        'Delivery issue',
        'Food stale',
        'Delivery partner rude',
        'Maps not working properly',
        'Instamart should be open all night',
        'Bring back 10 minute bolt delivery',
        'App crash',
        'Payment issue',
        'Order cancellation',
        'Wrong order delivered',
        'Late delivery',
        'Food quality poor',
        'Customer service unresponsive',
        'Refund not processed',
        'Promo code not working'
    ],
    'zomato': [
        'Delivery issue',
        'Food stale',
        'Delivery partner rude',
        'Maps not working properly',
        'App crash',
        'Payment issue',
        'Order cancellation',
        'Wrong order delivered',
        'Late delivery',
        'Food quality poor',
        'Customer service unresponsive',
        'Refund not processed',
        'Promo code not working'
    ]
}

# AI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'  # Lightweight model for embeddings
SIMILARITY_THRESHOLD = 0.75  # Threshold for topic deduplication
MAX_TOPICS = 50  # Maximum number of topics to track

# Data storage
DATA_DIR = 'data'
REVIEWS_DIR = os.path.join(DATA_DIR, 'reviews')
TOPICS_DIR = os.path.join(DATA_DIR, 'topics')
REPORTS_DIR = 'reports'

# Date configuration
START_DATE = datetime(2024, 6, 1)
ROLLING_WINDOW_DAYS = 30

# Processing configuration
BATCH_SIZE = 100  # Number of reviews to process in each batch
MIN_REVIEW_LENGTH = 10  # Minimum characters for a review to be processed


