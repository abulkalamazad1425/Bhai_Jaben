from typing import Optional
from decimal import Decimal
import json
import math

class FareCalculationService:
    BASE_FARE = Decimal('50.00')  # Base fare in currency units
    RATE_PER_KM = Decimal('15.00')  # Rate per kilometer
    
    @staticmethod
    def calculate_distance(pickup_coords: dict, drop_coords: dict) -> float:
        """Calculate distance between two coordinates using Haversine formula"""
        lat1, lon1 = pickup_coords['latitude'], pickup_coords['longitude']
        lat2, lon2 = drop_coords['latitude'], drop_coords['longitude']
        
        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Radius of earth in kilometers
        r = 6371
        distance = c * r
        
        return distance
    
    @classmethod
    def calculate_fare(cls, pickup_coords: dict, drop_coords: dict) -> Decimal:
        """Calculate fare based on distance"""
        try:
            distance = cls.calculate_distance(pickup_coords, drop_coords)
            fare = cls.BASE_FARE + (Decimal(str(distance)) * cls.RATE_PER_KM)
            return round(fare, 2)
        except Exception:
            return cls.BASE_FARE

class LocationService:
    @staticmethod
    def parse_location(location_string: str) -> dict:
        """Parse location string to coordinates"""
        try:
            return json.loads(location_string)
        except json.JSONDecodeError:
            return {"latitude": 0.0, "longitude": 0.0}
    
    @staticmethod
    def format_location(latitude: float, longitude: float, address: str = None) -> str:
        """Format location to JSON string"""
        location_data = {
            "latitude": latitude,
            "longitude": longitude
        }
        if address:
            location_data["address"] = address
        return json.dumps(location_data)