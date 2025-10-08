"""
Cost Prediction Models
Uses XGBoost for predicting flight, accommodation, and total trip costs
"""
import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from typing import Dict, List, Optional, Tuple
import joblib
from datetime import datetime
from utils.logger import logger


class FlightCostPredictor:
    """
    Predict flight costs using XGBoost
    """
    
    def __init__(self):
        self.model = XGBRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=7,
            random_state=42,
            n_jobs=-1
        )
        self.label_encoders = {}
        self.feature_columns = []
        self.is_fitted = False
        
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare features for training/prediction
        
        Args:
            df: DataFrame with flight data
            
        Returns:
            DataFrame with engineered features
        """
        df = df.copy()
        
        # Parse date if it's a string
        if 'Date' in df.columns and df['Date'].dtype == 'object':
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        # Extract date features
        if 'Date' in df.columns:
            df['day_of_week'] = df['Date'].dt.dayofweek
            df['month'] = df['Date'].dt.month
            df['day_of_month'] = df['Date'].dt.day
            df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
            
            # Season
            df['season'] = df['month'].apply(self._get_season)
        
        # Calculate booking lead time if booking date available
        if 'Booking_Date' in df.columns and 'Date' in df.columns:
            df['Booking_Date'] = pd.to_datetime(df['Booking_Date'], errors='coerce')
            df['lead_time_days'] = (df['Date'] - df['Booking_Date']).dt.days
        
        return df
    
    @staticmethod
    def _get_season(month: int) -> str:
        """Get season from month"""
        if month in [12, 1, 2]:
            return 'winter'
        elif month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        else:
            return 'autumn'
    
    def fit(self, df: pd.DataFrame, target_column: str = 'Base_Price'):
        """
        Train the flight cost prediction model
        
        Args:
            df: Training data
            target_column: Name of the target column
        """
        logger.info("Training flight cost prediction model...")
        
        # Prepare features
        df = self.prepare_features(df)
        
        # Select features
        categorical_features = ['From', 'To', 'season']
        numerical_features = ['day_of_week', 'month', 'day_of_month', 'is_weekend']
        
        if 'lead_time_days' in df.columns:
            numerical_features.append('lead_time_days')
        
        # Encode categorical features
        for col in categorical_features:
            if col in df.columns:
                le = LabelEncoder()
                df[f'{col}_encoded'] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le
        
        # Prepare feature matrix
        encoded_features = [f'{col}_encoded' for col in categorical_features if col in df.columns]
        self.feature_columns = encoded_features + numerical_features
        
        X = df[self.feature_columns]
        y = df[target_column]
        
        # Remove any NaN values
        mask = ~(X.isna().any(axis=1) | y.isna())
        X = X[mask]
        y = y[mask]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        logger.info(f"Flight cost model trained - MAE: {mae:.2f}, RMSE: {rmse:.2f}, R²: {r2:.3f}")
        
        self.is_fitted = True
        
        return {
            'mae': mae,
            'rmse': rmse,
            'r2': r2
        }
    
    def predict(
        self,
        from_city: str,
        to_city: str,
        travel_date: datetime,
        booking_date: Optional[datetime] = None
    ) -> Dict:
        """
        Predict flight cost
        
        Args:
            from_city: Origin city
            to_city: Destination city
            travel_date: Date of travel
            booking_date: Date of booking (optional)
            
        Returns:
            Dict with predicted cost and confidence
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")
        
        # Create input dataframe
        input_data = pd.DataFrame([{
            'From': from_city,
            'To': to_city,
            'Date': travel_date,
            'Booking_Date': booking_date or datetime.now()
        }])
        
        # Prepare features
        input_data = self.prepare_features(input_data)
        
        # Encode categorical features
        for col in ['From', 'To', 'season']:
            if col in self.label_encoders:
                try:
                    input_data[f'{col}_encoded'] = self.label_encoders[col].transform(
                        input_data[col].astype(str)
                    )
                except ValueError:
                    # Handle unseen categories
                    input_data[f'{col}_encoded'] = 0
        
        # Prepare feature matrix
        X = input_data[self.feature_columns]
        
        # Predict
        predicted_cost = self.model.predict(X)[0]
        
        # Calculate confidence (simplified)
        confidence = 0.85  # This could be improved with prediction intervals
        
        return {
            'predicted_cost': float(predicted_cost),
            'confidence': confidence,
            'currency': 'INR'
        }
    
    def save(self, filepath: str):
        """Save the model"""
        model_data = {
            'model': self.model,
            'label_encoders': self.label_encoders,
            'feature_columns': self.feature_columns,
            'is_fitted': self.is_fitted
        }
        joblib.dump(model_data, filepath)
        logger.info(f"Flight cost predictor saved to {filepath}")
    
    def load(self, filepath: str):
        """Load the model"""
        model_data = joblib.load(filepath)
        self.model = model_data['model']
        self.label_encoders = model_data['label_encoders']
        self.feature_columns = model_data['feature_columns']
        self.is_fitted = model_data['is_fitted']
        logger.info(f"Flight cost predictor loaded from {filepath}")


class AccommodationCostPredictor:
    """
    Predict accommodation costs
    """
    
    def __init__(self):
        self.model = XGBRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42,
            n_jobs=-1
        )
        self.label_encoders = {}
        self.feature_columns = []
        self.is_fitted = False
        
        # Default cost estimates (INR per night)
        self.default_costs = {
            'budget': {'hotel': 1000, 'hostel': 500, 'guesthouse': 800},
            'mid-range': {'hotel': 2500, 'resort': 3500, 'apartment': 2000},
            'luxury': {'hotel': 6000, 'resort': 10000, 'villa': 8000}
        }
    
    def predict(
        self,
        destination: str,
        accommodation_type: str,
        star_rating: int,
        duration_nights: int,
        travel_date: datetime,
        budget_category: str = 'mid-range'
    ) -> Dict:
        """
        Predict accommodation cost
        
        Args:
            destination: Destination city/state
            accommodation_type: Type (hotel, resort, hostel, etc.)
            star_rating: Star rating (1-5)
            duration_nights: Number of nights
            travel_date: Check-in date
            budget_category: Budget category (budget, mid-range, luxury)
            
        Returns:
            Dict with predicted cost
        """
        # Get base cost
        base_cost = self.default_costs.get(budget_category, {}).get(
            accommodation_type.lower(),
            2000  # Default
        )
        
        # Adjust for star rating
        rating_multiplier = 1 + (star_rating - 3) * 0.3
        
        # Adjust for season
        month = travel_date.month
        season_multiplier = 1.0
        if month in [12, 1, 4, 5, 10, 11]:  # Peak season
            season_multiplier = 1.3
        elif month in [6, 7, 8, 9]:  # Monsoon/off-season
            season_multiplier = 0.8
        
        # Calculate total cost
        cost_per_night = base_cost * rating_multiplier * season_multiplier
        total_cost = cost_per_night * duration_nights
        
        return {
            'predicted_cost': float(total_cost),
            'cost_per_night': float(cost_per_night),
            'duration_nights': duration_nights,
            'confidence': 0.80,
            'currency': 'INR'
        }
    
    def save(self, filepath: str):
        """Save the model"""
        model_data = {
            'default_costs': self.default_costs
        }
        joblib.dump(model_data, filepath)
        logger.info(f"Accommodation cost predictor saved to {filepath}")
    
    def load(self, filepath: str):
        """Load the model"""
        model_data = joblib.load(filepath)
        self.default_costs = model_data['default_costs']
        logger.info(f"Accommodation cost predictor loaded from {filepath}")


class TripCostPredictor:
    """
    Predict total trip cost combining all components
    """
    
    def __init__(self):
        self.flight_predictor = FlightCostPredictor()
        self.accommodation_predictor = AccommodationCostPredictor()
        
        # Default costs for other categories (INR per person per day)
        self.meal_costs = {
            'budget': 300,
            'mid-range': 600,
            'luxury': 1200
        }
        
        self.activity_costs = {
            'budget': 500,
            'mid-range': 1000,
            'luxury': 2500
        }
        
        self.transport_costs = {
            'budget': 200,
            'mid-range': 500,
            'luxury': 1000
        }
    
    def predict_total_cost(
        self,
        from_city: str,
        to_city: str,
        travel_date: datetime,
        return_date: datetime,
        num_travelers: int,
        accommodation_type: str,
        star_rating: int,
        budget_category: str = 'mid-range',
        meal_preference: str = 'veg',
        include_activities: bool = True
    ) -> Dict:
        """
        Predict total trip cost
        
        Args:
            from_city: Origin city
            to_city: Destination city
            travel_date: Start date
            return_date: End date
            num_travelers: Number of travelers
            accommodation_type: Type of accommodation
            star_rating: Star rating
            budget_category: Budget category
            meal_preference: Meal preference
            include_activities: Include activity costs
            
        Returns:
            Dict with cost breakdown
        """
        duration_days = (return_date - travel_date).days
        duration_nights = max(1, duration_days)
        
        # Predict flight costs (round trip)
        try:
            flight_cost_oneway = self.flight_predictor.predict(
                from_city, to_city, travel_date
            )['predicted_cost']
            flight_cost_return = self.flight_predictor.predict(
                to_city, from_city, return_date
            )['predicted_cost']
            total_flight_cost = (flight_cost_oneway + flight_cost_return) * num_travelers
        except Exception as e:
            logger.warning(f"Flight prediction failed: {e}. Using default.")
            # Default flight cost
            total_flight_cost = 5000 * num_travelers
        
        # Predict accommodation costs
        accommodation_result = self.accommodation_predictor.predict(
            to_city,
            accommodation_type,
            star_rating,
            duration_nights,
            travel_date,
            budget_category
        )
        total_accommodation_cost = accommodation_result['predicted_cost']
        
        # Calculate meal costs
        meal_cost_per_day = self.meal_costs.get(budget_category, 600)
        if meal_preference == 'non-veg':
            meal_cost_per_day *= 1.2
        total_meal_cost = meal_cost_per_day * duration_days * num_travelers
        
        # Calculate activity costs
        total_activity_cost = 0
        if include_activities:
            activity_cost_per_day = self.activity_costs.get(budget_category, 1000)
            total_activity_cost = activity_cost_per_day * duration_days * num_travelers
        
        # Calculate local transport costs
        transport_cost_per_day = self.transport_costs.get(budget_category, 500)
        total_transport_cost = transport_cost_per_day * duration_days * num_travelers
        
        # Calculate total
        total_cost = (
            total_flight_cost +
            total_accommodation_cost +
            total_meal_cost +
            total_activity_cost +
            total_transport_cost
        )
        
        # Add contingency (10%)
        contingency = total_cost * 0.1
        grand_total = total_cost + contingency
        
        return {
            'breakdown': {
                'flights': float(total_flight_cost),
                'accommodation': float(total_accommodation_cost),
                'meals': float(total_meal_cost),
                'activities': float(total_activity_cost),
                'local_transport': float(total_transport_cost),
                'contingency': float(contingency)
            },
            'total_cost': float(grand_total),
            'cost_per_person': float(grand_total / num_travelers),
            'duration_days': duration_days,
            'num_travelers': num_travelers,
            'currency': 'INR',
            'confidence': 0.82
        }
    
    def optimize_budget(
        self,
        current_cost: Dict,
        target_budget: float,
        flexibility: Dict[str, bool]
    ) -> Dict:
        """
        Suggest budget optimizations
        
        Args:
            current_cost: Current cost breakdown
            target_budget: Target budget
            flexibility: Dict indicating which components can be adjusted
            
        Returns:
            Dict with optimization suggestions
        """
        suggestions = []
        potential_savings = 0
        
        breakdown = current_cost['breakdown']
        total = current_cost['total_cost']
        difference = total - target_budget
        
        if difference <= 0:
            return {
                'within_budget': True,
                'suggestions': [],
                'potential_savings': 0
            }
        
        # Suggest accommodation downgrade
        if flexibility.get('accommodation', True):
            savings = breakdown['accommodation'] * 0.3
            suggestions.append({
                'category': 'accommodation',
                'suggestion': 'Consider downgrading to a budget hotel or hostel',
                'potential_savings': float(savings)
            })
            potential_savings += savings
        
        # Suggest meal optimization
        if flexibility.get('meals', True):
            savings = breakdown['meals'] * 0.25
            suggestions.append({
                'category': 'meals',
                'suggestion': 'Try local eateries instead of restaurants',
                'potential_savings': float(savings)
            })
            potential_savings += savings
        
        # Suggest activity reduction
        if flexibility.get('activities', True) and breakdown['activities'] > 0:
            savings = breakdown['activities'] * 0.4
            suggestions.append({
                'category': 'activities',
                'suggestion': 'Reduce paid activities and explore free attractions',
                'potential_savings': float(savings)
            })
            potential_savings += savings
        
        # Suggest transport optimization
        if flexibility.get('transport', True):
            savings = breakdown['local_transport'] * 0.3
            suggestions.append({
                'category': 'transport',
                'suggestion': 'Use public transport instead of taxis',
                'potential_savings': float(savings)
            })
            potential_savings += savings
        
        return {
            'within_budget': False,
            'over_budget_by': float(difference),
            'suggestions': suggestions,
            'potential_savings': float(potential_savings),
            'optimized_total': float(total - potential_savings)
        }
    
    def save(self, directory: str):
        """Save all predictors"""
        from pathlib import Path
        Path(directory).mkdir(parents=True, exist_ok=True)
        
        self.flight_predictor.save(f"{directory}/flight_predictor.joblib")
        self.accommodation_predictor.save(f"{directory}/accommodation_predictor.joblib")
        
        logger.info(f"Trip cost predictor saved to {directory}")
    
    def load(self, directory: str):
        """Load all predictors"""
        self.flight_predictor.load(f"{directory}/flight_predictor.joblib")
        self.accommodation_predictor.load(f"{directory}/accommodation_predictor.joblib")
        
        logger.info(f"Trip cost predictor loaded from {directory}")
