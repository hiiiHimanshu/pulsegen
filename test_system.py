"""
Test script to verify the system works correctly
"""
import os
import pandas as pd
from datetime import datetime, timedelta
from config import APP_CONFIGS
from topic_extractor import TopicExtractor


def test_topic_deduplication():
    """Test topic deduplication functionality"""
    print("Testing topic deduplication...")
    
    extractor = TopicExtractor('swiggy')
    
    # Test cases for deduplication
    test_reviews = [
        "Delivery guy was rude and unprofessional",
        "Delivery partner behaved badly",
        "Delivery person was impolite",
        "The delivery man was disrespectful",
        "Food was stale and tasted bad",
        "Received old food",
        "The food was not fresh",
    ]
    
    print("\nTest reviews and extracted topics:")
    print("-" * 60)
    
    for review in test_reviews:
        topics = extractor.extract_topics_from_review(review)
        print(f"\nReview: {review}")
        print(f"Topics: {topics}")
    
    print("\n" + "=" * 60)
    print("Topic Registry:")
    print("=" * 60)
    for topic in extractor.get_topic_registry().keys():
        print(f"  - {topic}")


def test_keyword_extraction():
    """Test keyword-based topic extraction"""
    print("\n\nTesting keyword-based extraction...")
    print("=" * 60)
    
    extractor = TopicExtractor('swiggy')
    
    test_cases = [
        ("App keeps crashing", ["App crash"]),
        ("Payment failed multiple times", ["Payment issue"]),
        ("Wrong order was delivered", ["Wrong order delivered"]),
        ("Delivery was very late", ["Late delivery"]),
        ("Food quality was poor", ["Food quality poor"]),
    ]
    
    for review_text, expected_topics in test_cases:
        topics = extractor.extract_topics_from_review(review_text)
        print(f"\nReview: {review_text}")
        print(f"Expected: {expected_topics}")
        print(f"Got: {topics}")
        print(f"Match: {any(t in topics for t in expected_topics)}")


if __name__ == '__main__':
    print("=" * 60)
    print("SYSTEM TEST SUITE")
    print("=" * 60)
    
    test_topic_deduplication()
    test_keyword_extraction()
    
    print("\n" + "=" * 60)
    print("Tests completed!")
    print("=" * 60)


