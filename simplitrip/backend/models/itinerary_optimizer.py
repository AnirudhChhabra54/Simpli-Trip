"""
Itinerary Optimization using TSP-based algorithms
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
import random
from utils.logger import logger


class ItineraryOptimizer:
    """
    Optimize itinerary using Traveling Salesperson Problem (TSP) approach
    Uses Simulated Annealing for optimization
    """
    
    def __init__(self, places_df: Optional[pd.DataFrame] = None):
        self.places_df = places_df
        self.distance_matrix = None
        
    def set_places_data(self, places_df: pd.DataFrame):
        """Set places data"""
        self.places_df = places_df
        
    def calculate_distance_matrix(self, places: List[Dict]) -> np.ndarray:
        """
        Calculate distance matrix between places
        For now, uses simplified distance calculation
        In production, would use Google Maps Distance Matrix API
        
        Args:
            places: List of place dictionaries with coordinates
            
        Returns:
            Distance matrix (n x n)
        """
        n = len(places)
        matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    # Simplified distance calculation
                    # In production, use actual travel time from Google Maps API
                    matrix[i][j] = self._calculate_simple_distance(
                        places[i], places[j]
                    )
        
        return matrix
    
    def _calculate_simple_distance(self, place1: Dict, place2: Dict) -> float:
        """
        Calculate simplified distance between two places
        Returns time in minutes
        """
        # If coordinates available, use Haversine formula
        if all(k in place1 for k in ['latitude', 'longitude']) and \
           all(k in place2 for k in ['latitude', 'longitude']):
            return self._haversine_distance(
                place1['latitude'], place1['longitude'],
                place2['latitude'], place2['longitude']
            )
        
        # Otherwise, use random distance (for demo)
        return random.uniform(15, 60)  # 15-60 minutes
    
    @staticmethod
    def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two coordinates using Haversine formula
        Returns approximate travel time in minutes (assuming 40 km/h average speed)
        """
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance_km = R * c
        
        # Convert to travel time (assuming 40 km/h average speed in city)
        travel_time_minutes = (distance_km / 40) * 60
        
        return travel_time_minutes
    
    def simulated_annealing(
        self,
        distance_matrix: np.ndarray,
        initial_temp: float = 1000,
        cooling_rate: float = 0.995,
        min_temp: float = 1
    ) -> List[int]:
        """
        Solve TSP using Simulated Annealing
        
        Args:
            distance_matrix: Distance matrix between places
            initial_temp: Initial temperature
            cooling_rate: Cooling rate
            min_temp: Minimum temperature
            
        Returns:
            Optimized route (list of indices)
        """
        n = len(distance_matrix)
        
        # Initialize with random route
        current_route = list(range(n))
        random.shuffle(current_route)
        current_cost = self._calculate_route_cost(current_route, distance_matrix)
        
        best_route = current_route.copy()
        best_cost = current_cost
        
        temp = initial_temp
        
        while temp > min_temp:
            # Generate neighbor by swapping two random cities
            new_route = current_route.copy()
            i, j = random.sample(range(n), 2)
            new_route[i], new_route[j] = new_route[j], new_route[i]
            
            new_cost = self._calculate_route_cost(new_route, distance_matrix)
            
            # Accept or reject new route
            if new_cost < current_cost or random.random() < np.exp((current_cost - new_cost) / temp):
                current_route = new_route
                current_cost = new_cost
                
                if current_cost < best_cost:
                    best_route = current_route.copy()
                    best_cost = current_cost
            
            temp *= cooling_rate
        
        return best_route
    
    @staticmethod
    def _calculate_route_cost(route: List[int], distance_matrix: np.ndarray) -> float:
        """Calculate total cost of a route"""
        cost = 0
        for i in range(len(route) - 1):
            cost += distance_matrix[route[i]][route[i + 1]]
        return cost
    
    def optimize_itinerary(
        self,
        places: List[Dict],
        start_location: Optional[Dict] = None,
        num_days: int = 1,
        daily_time_budget: int = 480  # 8 hours in minutes
    ) -> Dict:
        """
        Optimize itinerary for given places
        
        Args:
            places: List of places to visit with visit_duration
            start_location: Starting location (hotel/accommodation)
            num_days: Number of days
            daily_time_budget: Available time per day in minutes
            
        Returns:
            Optimized itinerary with day-wise schedule
        """
        logger.info(f"Optimizing itinerary for {len(places)} places over {num_days} days")
        
        # Add visit duration to places if not present
        for place in places:
            if 'visit_duration' not in place:
                place['visit_duration'] = self._estimate_visit_duration(place)
        
        # Calculate distance matrix
        all_locations = [start_location] + places if start_location else places
        distance_matrix = self.calculate_distance_matrix(all_locations)
        
        # Optimize route using simulated annealing
        if start_location:
            # Start from location 0 (start_location)
            optimized_indices = [0] + [i + 1 for i in self.simulated_annealing(
                distance_matrix[1:, 1:]
            )]
        else:
            optimized_indices = self.simulated_annealing(distance_matrix)
        
        # Create day-wise schedule
        daily_schedules = []
        current_day = []
        current_time = 0
        day_num = 1
        
        start_idx = 1 if start_location else 0  # Skip start location in schedule
        
        for idx in optimized_indices[start_idx:]:
            place = all_locations[idx]
            visit_duration = place['visit_duration']
            
            # Calculate travel time from previous location
            if current_day:
                prev_idx = optimized_indices[optimized_indices.index(idx) - 1]
                travel_time = distance_matrix[prev_idx][idx]
            else:
                # Travel from start location
                if start_location:
                    travel_time = distance_matrix[0][idx]
                else:
                    travel_time = 0
            
            # Check if place fits in current day
            if current_time + travel_time + visit_duration <= daily_time_budget:
                current_day.append({
                    'place': place,
                    'travel_time': float(travel_time),
                    'visit_duration': float(visit_duration),
                    'start_time': self._minutes_to_time(current_time + travel_time)
                })
                current_time += travel_time + visit_duration
            else:
                # Start new day
                if current_day:
                    daily_schedules.append({
                        'day': day_num,
                        'places': current_day,
                        'total_time': current_time
                    })
                    day_num += 1
                    current_day = []
                    current_time = 0
                
                # Add place to new day
                travel_time = distance_matrix[0][idx] if start_location else 0
                current_day.append({
                    'place': place,
                    'travel_time': float(travel_time),
                    'visit_duration': float(visit_duration),
                    'start_time': self._minutes_to_time(travel_time)
                })
                current_time = travel_time + visit_duration
        
        # Add last day
        if current_day:
            daily_schedules.append({
                'day': day_num,
                'places': current_day,
                'total_time': current_time
            })
        
        # Calculate statistics
        total_travel_time = sum(
            sum(p['travel_time'] for p in day['places'])
            for day in daily_schedules
        )
        total_visit_time = sum(
            sum(p['visit_duration'] for p in day['places'])
            for day in daily_schedules
        )
        
        result = {
            'daily_schedules': daily_schedules,
            'num_days': len(daily_schedules),
            'total_places': len(places),
            'total_travel_time': float(total_travel_time),
            'total_visit_time': float(total_visit_time),
            'optimization_score': self._calculate_optimization_score(
                daily_schedules, distance_matrix
            )
        }
        
        logger.info(f"Itinerary optimized: {len(daily_schedules)} days, "
                   f"{len(places)} places, {total_travel_time:.0f} min travel time")
        
        return result
    
    def _estimate_visit_duration(self, place: Dict) -> int:
        """
        Estimate visit duration for a place (in minutes)
        
        Args:
            place: Place dictionary
            
        Returns:
            Estimated duration in minutes
        """
        # Check if duration is in the places database
        if self.places_df is not None and 'name' in place:
            matching = self.places_df[
                self.places_df['Place Name'].str.contains(place['name'], case=False, na=False)
            ]
            if not matching.empty and 'Visit Duration' in matching.columns:
                duration_str = matching.iloc[0]['Visit Duration']
                # Parse duration (e.g., "2-3 hours" -> 150 minutes)
                return self._parse_duration(duration_str)
        
        # Default durations based on category
        category = place.get('category', '').lower()
        
        duration_map = {
            'museum': 120,
            'temple': 60,
            'fort': 180,
            'palace': 150,
            'beach': 180,
            'park': 90,
            'market': 120,
            'monument': 90,
            'wildlife': 240,
            'adventure': 180
        }
        
        for key, duration in duration_map.items():
            if key in category:
                return duration
        
        return 120  # Default 2 hours
    
    @staticmethod
    def _parse_duration(duration_str: str) -> int:
        """Parse duration string to minutes"""
        try:
            # Handle formats like "2-3 hours", "1 hour", "30 minutes"
            duration_str = duration_str.lower()
            
            if 'hour' in duration_str:
                # Extract first number
                import re
                numbers = re.findall(r'\d+', duration_str)
                if numbers:
                    hours = int(numbers[0])
                    return hours * 60
            elif 'minute' in duration_str:
                import re
                numbers = re.findall(r'\d+', duration_str)
                if numbers:
                    return int(numbers[0])
        except:
            pass
        
        return 120  # Default 2 hours
    
    @staticmethod
    def _minutes_to_time(minutes: int, start_hour: int = 9) -> str:
        """Convert minutes from start to time string"""
        total_minutes = start_hour * 60 + minutes
        hours = (total_minutes // 60) % 24
        mins = total_minutes % 60
        return f"{hours:02d}:{mins:02d}"
    
    def _calculate_optimization_score(
        self,
        daily_schedules: List[Dict],
        distance_matrix: np.ndarray
    ) -> float:
        """
        Calculate optimization score (0-100)
        Higher is better
        """
        if not daily_schedules:
            return 0.0
        
        # Calculate average travel time per place
        total_places = sum(len(day['places']) for day in daily_schedules)
        total_travel = sum(
            sum(p['travel_time'] for p in day['places'])
            for day in daily_schedules
        )
        
        if total_places == 0:
            return 0.0
        
        avg_travel_per_place = total_travel / total_places
        
        # Score based on travel efficiency (less travel time = higher score)
        # Assume 30 minutes average is good, 60+ is poor
        if avg_travel_per_place <= 30:
            score = 100
        elif avg_travel_per_place >= 60:
            score = 50
        else:
            score = 100 - ((avg_travel_per_place - 30) / 30) * 50
        
        return float(score)
    
    def validate_itinerary(self, itinerary: Dict) -> Dict:
        """
        Validate if itinerary is feasible
        
        Args:
            itinerary: Itinerary dictionary
            
        Returns:
            Validation result
        """
        issues = []
        warnings = []
        
        for day in itinerary['daily_schedules']:
            day_num = day['day']
            total_time = day['total_time']
            
            # Check if day is too packed
            if total_time > 540:  # More than 9 hours
                warnings.append(
                    f"Day {day_num} is very packed ({total_time/60:.1f} hours). "
                    "Consider reducing activities."
                )
            
            # Check if day is too light
            if total_time < 180:  # Less than 3 hours
                warnings.append(
                    f"Day {day_num} has light schedule ({total_time/60:.1f} hours). "
                    "Consider adding more activities."
                )
            
            # Check for long travel times
            for place_info in day['places']:
                if place_info['travel_time'] > 90:  # More than 1.5 hours
                    warnings.append(
                        f"Day {day_num}: Long travel time to {place_info['place']['name']} "
                        f"({place_info['travel_time']:.0f} minutes)"
                    )
        
        return {
            'is_valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }
