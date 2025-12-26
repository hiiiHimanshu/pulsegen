"""
AI Agent for topic extraction and deduplication
"""
import os
import json
import numpy as np
from typing import List, Dict, Set, Tuple, Optional
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from config import SEED_TOPICS, EMBEDDING_MODEL, SIMILARITY_THRESHOLD, MAX_TOPICS

# Optional OpenAI import
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class TopicExtractor:
    """AI agent for extracting and deduplicating topics from reviews"""
    
    def __init__(self, app_name: str, use_openai: bool = False):
        self.app_name = app_name
        self.seed_topics = SEED_TOPICS.get(app_name.lower(), [])
        self.use_openai = use_openai and os.getenv('OPENAI_API_KEY')
        
        # Initialize embedding model
        print(f"Loading embedding model: {EMBEDDING_MODEL}")
        # Use local cache directory to avoid permission issues
        cache_dir = os.path.join(os.getcwd(), '.cache', 'huggingface')
        os.makedirs(cache_dir, exist_ok=True)
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL, cache_folder=cache_dir)
        
        # Initialize OpenAI client if API key is available
        if self.use_openai and OPENAI_AVAILABLE:
            self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        elif self.use_openai and not OPENAI_AVAILABLE:
            print("Warning: OpenAI not available. Falling back to keyword-based extraction.")
            self.use_openai = False
        
        # Topic registry: maps canonical topic name to its embedding
        self.topic_registry: Dict[str, np.ndarray] = {}
        self._initialize_topic_registry()
    
    def _initialize_topic_registry(self):
        """Initialize topic registry with seed topics"""
        for topic in self.seed_topics:
            embedding = self.embedding_model.encode([topic])[0]
            self.topic_registry[topic] = embedding
        print(f"Initialized with {len(self.topic_registry)} seed topics")
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for a text"""
        return self.embedding_model.encode([text])[0]
    
    def _find_similar_topic(self, topic_text: str, threshold: float = SIMILARITY_THRESHOLD) -> Tuple[Optional[str], float]:
        """
        Find if a topic is similar to existing topics
        
        Returns:
            Tuple of (canonical_topic_name, similarity_score) or (None, 0.0)
        """
        if not self.topic_registry:
            return None, 0.0
        
        topic_embedding = self._get_embedding(topic_text)
        
        # Calculate similarity with all existing topics
        similarities = {}
        for canonical_topic, canonical_embedding in self.topic_registry.items():
            similarity = cosine_similarity(
                topic_embedding.reshape(1, -1),
                canonical_embedding.reshape(1, -1)
            )[0][0]
            similarities[canonical_topic] = similarity
        
        # Find the most similar topic
        if similarities:
            best_match = max(similarities.items(), key=lambda x: x[1])
            if best_match[1] >= threshold:
                return best_match
        
        return None, 0.0
    
    def _extract_topics_with_ai(self, review_text: str) -> List[str]:
        """Extract topics using OpenAI API"""
        if not self.use_openai:
            return []
        
        try:
            prompt = f"""Analyze the following app review and extract specific topics, issues, requests, or feedback mentioned. 
Return only the topics as a comma-separated list. Be specific and concise.

Review: "{review_text}"

Topics:"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing app reviews and extracting specific topics, issues, and feedback."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.3
            )
            
            topics_text = response.choices[0].message.content.strip()
            topics = [t.strip() for t in topics_text.split(',') if t.strip()]
            return topics
        except Exception as e:
            print(f"Error in OpenAI topic extraction: {e}")
            return []
    
    def _extract_topics_keyword_based(self, review_text: str) -> List[str]:
        """Extract topics using keyword matching and heuristics"""
        review_lower = review_text.lower()
        extracted_topics = []
        
        # Keyword-based topic detection
        topic_keywords = {
            'Delivery issue': ['delivery', 'delivered', 'deliver', 'not delivered', 'delivery problem'],
            'Food stale': ['stale', 'old food', 'expired', 'not fresh', 'spoiled'],
            'Delivery partner rude': ['rude', 'impolite', 'bad behavior', 'unprofessional', 'disrespectful', 'delivery guy', 'delivery person', 'delivery partner'],
            'Maps not working properly': ['map', 'location', 'gps', 'navigation', 'wrong location', 'map issue'],
            'Instamart should be open all night': ['instamart', 'open all night', '24 hours', 'late night'],
            'Bring back 10 minute bolt delivery': ['bolt', '10 minute', 'quick delivery', 'fast delivery'],
            'App crash': ['crash', 'freeze', 'not opening', 'app not working', 'force close'],
            'Payment issue': ['payment', 'payment failed', 'payment problem', 'transaction', 'refund'],
            'Order cancellation': ['cancel', 'cancelled', 'cancellation'],
            'Wrong order delivered': ['wrong order', 'incorrect order', 'different order'],
            'Late delivery': ['late', 'delayed', 'delay', 'taking too long'],
            'Food quality poor': ['quality', 'taste bad', 'not good', 'poor quality', 'bad food'],
            'Customer service unresponsive': ['customer service', 'support', 'not responding', 'no response'],
            'Refund not processed': ['refund', 'money back', 'not refunded'],
            'Promo code not working': ['promo', 'coupon', 'discount', 'code not working', 'offer']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in review_lower for keyword in keywords):
                extracted_topics.append(topic)
        
        return extracted_topics
    
    def extract_topics_from_review(self, review_text: str) -> List[str]:
        """
        Extract topics from a single review
        
        Returns:
            List of canonical topic names
        """
        if len(review_text.strip()) < 10:
            return []
        
        # Extract topics using keyword-based approach (faster and more reliable)
        raw_topics = self._extract_topics_keyword_based(review_text)
        
        # Optionally use AI for additional topic extraction
        if self.use_openai:
            ai_topics = self._extract_topics_with_ai(review_text)
            raw_topics.extend(ai_topics)
        
        # Deduplicate and map to canonical topics
        canonical_topics = []
        for topic in raw_topics:
            # Check if topic matches an existing canonical topic
            canonical_topic, similarity = self._find_similar_topic(topic)
            
            if canonical_topic:
                canonical_topics.append(canonical_topic)
            else:
                # New topic - add to registry if we haven't exceeded max topics
                if len(self.topic_registry) < MAX_TOPICS:
                    embedding = self._get_embedding(topic)
                    self.topic_registry[topic] = embedding
                    canonical_topics.append(topic)
                    print(f"New topic discovered: {topic}")
        
        return list(set(canonical_topics))  # Remove duplicates
    
    def extract_topics_from_batch(self, reviews_df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract topics from a batch of reviews
        
        Args:
            reviews_df: DataFrame with reviews
            
        Returns:
            DataFrame with topics added
        """
        print(f"Extracting topics from {len(reviews_df)} reviews...")
        
        all_topics = []
        for idx, row in reviews_df.iterrows():
            topics = self.extract_topics_from_review(row['content'])
            all_topics.append(topics)
        
        reviews_df['topics'] = all_topics
        return reviews_df
    
    def get_topic_registry(self) -> Dict[str, np.ndarray]:
        """Get current topic registry"""
        return self.topic_registry
    
    def save_topic_registry(self, file_path: str):
        """Save topic registry to file"""
        registry_data = {
            'topics': list(self.topic_registry.keys()),
            'app_name': self.app_name
        }
        with open(file_path, 'w') as f:
            json.dump(registry_data, f, indent=2)
    
    def load_topic_registry(self, file_path: str):
        """Load topic registry from file"""
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                registry_data = json.load(f)
            
            topics = registry_data.get('topics', [])
            for topic in topics:
                embedding = self._get_embedding(topic)
                self.topic_registry[topic] = embedding
            print(f"Loaded {len(self.topic_registry)} topics from registry")


