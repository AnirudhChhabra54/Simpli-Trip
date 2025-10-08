"""
Recommendation System Models
Implements hybrid recommendation (Content-Based + Collaborative Filtering)
"""
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Optional, Tuple
import joblib
from pathlib import Path
from utils.logger import logger
from config.settings import settings


class ContentBasedRecommender:
    """
    Content-based filtering for destination recommendations
    Uses TF-IDF and cosine similarity on destination features
    """
    
    def __init__(self):
        self.destinations_df: Optional[pd.DataFrame] = None
        self.vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.feature_matrix = None
        self.destination_features = None
        
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare destination features for recommendation
        
        Args:
            df: DataFrame with destination data
            
        Returns:
            DataFrame with prepared features
        """
        df = df.copy()
        
        # Combine text features
        text_columns = ['Category', 'State', 'Best Time to Visit']
        df['combined_features'] = df[text_columns].fillna('').agg(' '.join, axis=1)
        
        # Normalize rating if exists
        if 'Rating' in df.columns:
            df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce').fillna(3.0)
        
        return df
    
    def fit(self, destinations_df: pd.DataFrame):
        """
        Fit the content-based recommender
        
        Args:
            destinations_df: DataFrame with destination information
        """
        logger.info("Fitting content-based recommender...")
        
        self.destinations_df = self.prepare_features(destinations_df)
        
        # Create TF-IDF matrix
        self.feature_matrix = self.vectorizer.fit_transform(
            self.destinations_df['combined_features']
        )
        
        logger.info(f"Content-based recommender fitted with {len(self.destinations_df)} destinations")
    
    def recommend(
        self,
        preferences: Dict[str, any],
        top_n: int = 10,
        exclude_destinations: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Recommend destinations based on user preferences
        
        Args:
            preferences: Dict with keys like 'category', 'state', 'best_time', 'budget'
            top_n: Number of recommendations to return
            exclude_destinations: List of destination names to exclude
            
        Returns:
            List of recommended destinations with scores
        """
        if self.destinations_df is None:
            raise ValueError("Model not fitted. Call fit() first.")
        
        # Create query from preferences
        query_parts = []
        if 'category' in preferences and preferences['category']:
            query_parts.append(preferences['category'])
        if 'state' in preferences and preferences['state']:
            query_parts.append(preferences['state'])
        if 'best_time' in preferences and preferences['best_time']:
            query_parts.append(preferences['best_time'])
        
        query = ' '.join(query_parts)
        
        # Transform query
        query_vector = self.vectorizer.transform([query])
        
        # Calculate similarity scores
        similarity_scores = cosine_similarity(query_vector, self.feature_matrix).flatten()
        
        # Add to dataframe
        results_df = self.destinations_df.copy()
        results_df['similarity_score'] = similarity_scores
        
        # Apply filters
        if 'category' in preferences and preferences['category']:
            results_df = results_df[
                results_df['Category'].str.contains(preferences['category'], case=False, na=False)
            ]
        
        if 'state' in preferences and preferences['state']:
            results_df = results_df[
                results_df['State'].str.contains(preferences['state'], case=False, na=False)
            ]
        
        # Exclude destinations
        if exclude_destinations:
            results_df = results_df[
                ~results_df['Destination Name'].isin(exclude_destinations)
            ]
        
        # Sort by similarity and rating
        if 'Rating' in results_df.columns:
            results_df['final_score'] = (
                results_df['similarity_score'] * 0.7 + 
                results_df['Rating'] / 5.0 * 0.3
            )
        else:
            results_df['final_score'] = results_df['similarity_score']
        
        results_df = results_df.sort_values('final_score', ascending=False)
        
        # Get top N
        top_destinations = results_df.head(top_n)
        
        # Format results
        recommendations = []
        for _, row in top_destinations.iterrows():
            recommendations.append({
                'destination_name': row['Destination Name'],
                'state': row.get('State', 'Unknown'),
                'category': row.get('Category', 'Unknown'),
                'rating': float(row.get('Rating', 0)),
                'best_time': row.get('Best Time to Visit', 'Anytime'),
                'score': float(row['final_score']),
                'description': row.get('Description', '')
            })
        
        logger.info(f"Generated {len(recommendations)} content-based recommendations")
        return recommendations
    
    def save(self, filepath: str):
        """Save the model"""
        model_data = {
            'destinations_df': self.destinations_df,
            'vectorizer': self.vectorizer,
            'feature_matrix': self.feature_matrix
        }
        joblib.dump(model_data, filepath)
        logger.info(f"Content-based recommender saved to {filepath}")
    
    def load(self, filepath: str):
        """Load the model"""
        model_data = joblib.load(filepath)
        self.destinations_df = model_data['destinations_df']
        self.vectorizer = model_data['vectorizer']
        self.feature_matrix = model_data['feature_matrix']
        logger.info(f"Content-based recommender loaded from {filepath}")


class CollaborativeFilteringRecommender:
    """
    Collaborative filtering for destination recommendations
    Uses user-destination interaction matrix
    """
    
    def __init__(self):
        self.user_item_matrix: Optional[pd.DataFrame] = None
        self.similarity_matrix: Optional[np.ndarray] = None
        self.destinations: Optional[List[str]] = None
        
    def fit(self, interactions_df: pd.DataFrame):
        """
        Fit collaborative filtering model
        
        Args:
            interactions_df: DataFrame with columns ['user_id', 'destination_id', 'rating']
        """
        logger.info("Fitting collaborative filtering recommender...")
        
        # Create user-item matrix
        self.user_item_matrix = interactions_df.pivot_table(
            index='user_id',
            columns='destination_id',
            values='rating',
            fill_value=0
        )
        
        # Calculate item-item similarity
        self.similarity_matrix = cosine_similarity(self.user_item_matrix.T)
        self.destinations = list(self.user_item_matrix.columns)
        
        logger.info(f"Collaborative filtering fitted with {len(self.user_item_matrix)} users "
                   f"and {len(self.destinations)} destinations")
    
    def recommend(
        self,
        user_id: str,
        top_n: int = 10,
        exclude_destinations: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Recommend destinations for a user
        
        Args:
            user_id: User identifier
            top_n: Number of recommendations
            exclude_destinations: Destinations to exclude
            
        Returns:
            List of recommended destinations with scores
        """
        if self.user_item_matrix is None:
            raise ValueError("Model not fitted. Call fit() first.")
        
        # Check if user exists
        if user_id not in self.user_item_matrix.index:
            logger.warning(f"User {user_id} not found in training data")
            return []
        
        # Get user's ratings
        user_ratings = self.user_item_matrix.loc[user_id]
        
        # Calculate predicted ratings
        rated_destinations = user_ratings[user_ratings > 0].index
        predictions = {}
        
        for dest in self.destinations:
            if dest in rated_destinations:
                continue  # Skip already rated
            
            if exclude_destinations and dest in exclude_destinations:
                continue
            
            # Calculate weighted average of similar items
            dest_idx = self.destinations.index(dest)
            similarities = self.similarity_matrix[dest_idx]
            
            weighted_sum = 0
            similarity_sum = 0
            
            for rated_dest in rated_destinations:
                rated_idx = self.destinations.index(rated_dest)
                sim = similarities[rated_idx]
                if sim > 0:
                    weighted_sum += sim * user_ratings[rated_dest]
                    similarity_sum += sim
            
            if similarity_sum > 0:
                predictions[dest] = weighted_sum / similarity_sum
        
        # Sort and get top N
        sorted_predictions = sorted(
            predictions.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_n]
        
        recommendations = [
            {
                'destination_id': dest_id,
                'predicted_rating': float(score),
                'score': float(score)
            }
            for dest_id, score in sorted_predictions
        ]
        
        logger.info(f"Generated {len(recommendations)} collaborative filtering recommendations")
        return recommendations
    
    def save(self, filepath: str):
        """Save the model"""
        model_data = {
            'user_item_matrix': self.user_item_matrix,
            'similarity_matrix': self.similarity_matrix,
            'destinations': self.destinations
        }
        joblib.dump(model_data, filepath)
        logger.info(f"Collaborative filtering recommender saved to {filepath}")
    
    def load(self, filepath: str):
        """Load the model"""
        model_data = joblib.load(filepath)
        self.user_item_matrix = model_data['user_item_matrix']
        self.similarity_matrix = model_data['similarity_matrix']
        self.destinations = model_data['destinations']
        logger.info(f"Collaborative filtering recommender loaded from {filepath}")


class HybridRecommender:
    """
    Hybrid recommendation system combining content-based and collaborative filtering
    """
    
    def __init__(self, content_weight: float = 0.7, collab_weight: float = 0.3):
        self.content_recommender = ContentBasedRecommender()
        self.collab_recommender = CollaborativeFilteringRecommender()
        self.content_weight = content_weight
        self.collab_weight = collab_weight
        
    def fit(
        self,
        destinations_df: pd.DataFrame,
        interactions_df: Optional[pd.DataFrame] = None
    ):
        """
        Fit both recommenders
        
        Args:
            destinations_df: Destination information
            interactions_df: User-destination interactions (optional)
        """
        # Always fit content-based
        self.content_recommender.fit(destinations_df)
        
        # Fit collaborative if data available
        if interactions_df is not None and len(interactions_df) > 0:
            self.collab_recommender.fit(interactions_df)
            logger.info("Hybrid recommender fitted with both models")
        else:
            logger.info("Hybrid recommender fitted with content-based only")
    
    def recommend(
        self,
        preferences: Dict[str, any],
        user_id: Optional[str] = None,
        top_n: int = 10,
        exclude_destinations: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Generate hybrid recommendations
        
        Args:
            preferences: User preferences for content-based filtering
            user_id: User ID for collaborative filtering (optional)
            top_n: Number of recommendations
            exclude_destinations: Destinations to exclude
            
        Returns:
            List of recommended destinations
        """
        # Get content-based recommendations
        content_recs = self.content_recommender.recommend(
            preferences,
            top_n=top_n * 2,  # Get more to merge
            exclude_destinations=exclude_destinations
        )
        
        # If no user_id or no collaborative data, return content-based only
        if user_id is None or self.collab_recommender.user_item_matrix is None:
            return content_recs[:top_n]
        
        # Get collaborative recommendations
        try:
            collab_recs = self.collab_recommender.recommend(
                user_id,
                top_n=top_n * 2,
                exclude_destinations=exclude_destinations
            )
        except Exception as e:
            logger.warning(f"Collaborative filtering failed: {e}")
            return content_recs[:top_n]
        
        # Merge recommendations
        merged_scores = {}
        
        # Add content-based scores
        for rec in content_recs:
            dest_name = rec['destination_name']
            merged_scores[dest_name] = {
                **rec,
                'content_score': rec['score'] * self.content_weight,
                'collab_score': 0
            }
        
        # Add collaborative scores
        for rec in collab_recs:
            dest_id = rec['destination_id']
            if dest_id in merged_scores:
                merged_scores[dest_id]['collab_score'] = rec['score'] * self.collab_weight
        
        # Calculate final scores
        for dest_name in merged_scores:
            merged_scores[dest_name]['final_score'] = (
                merged_scores[dest_name]['content_score'] +
                merged_scores[dest_name]['collab_score']
            )
        
        # Sort and return top N
        final_recommendations = sorted(
            merged_scores.values(),
            key=lambda x: x['final_score'],
            reverse=True
        )[:top_n]
        
        logger.info(f"Generated {len(final_recommendations)} hybrid recommendations")
        return final_recommendations
    
    def save(self, directory: str):
        """Save both models"""
        Path(directory).mkdir(parents=True, exist_ok=True)
        self.content_recommender.save(f"{directory}/content_recommender.joblib")
        if self.collab_recommender.user_item_matrix is not None:
            self.collab_recommender.save(f"{directory}/collab_recommender.joblib")
        logger.info(f"Hybrid recommender saved to {directory}")
    
    def load(self, directory: str):
        """Load both models"""
        self.content_recommender.load(f"{directory}/content_recommender.joblib")
        collab_path = f"{directory}/collab_recommender.joblib"
        if Path(collab_path).exists():
            self.collab_recommender.load(collab_path)
        logger.info(f"Hybrid recommender loaded from {directory}")
