from typing import List, Optional, Dict
from abc import ABC, abstractmethod
from datetime import datetime

class IRatingRepository(ABC):
    @abstractmethod
    def create_rating(self, rating_data: Dict) -> Dict:
        pass
    
    @abstractmethod
    def get_rating_by_id(self, rating_id: str) -> Optional[Dict]:
        pass
    
    @abstractmethod
    def get_ratings_by_ride_id(self, ride_id: str) -> List[Dict]:
        pass
    
    @abstractmethod
    def get_rating_by_ride_and_rater(self, ride_id: str, rater_id: str) -> Optional[Dict]:
        pass
    
    @abstractmethod
    def get_ratings_for_user(self, user_id: str) -> List[Dict]:
        pass
    
    @abstractmethod
    def get_ratings_for_driver(self, driver_id: str) -> List[Dict]:
        pass
    
    @abstractmethod
    def update_rating(self, rating_id: str, updates: Dict) -> Optional[Dict]:
        pass

class RatingRepository(IRatingRepository):
    def __init__(self, supabase_client):
        self.supabase = supabase_client
    
    def create_rating(self, rating_data: Dict) -> Dict:
        response = self.supabase.table('ride_ratings').insert(rating_data).execute()
        if response.data:
            return response.data[0]
        raise Exception("Failed to create rating")
    
    def get_rating_by_id(self, rating_id: str) -> Optional[Dict]:
        response = self.supabase.table('ride_ratings').select("*").eq('rating_id', rating_id).execute()
        return response.data[0] if response.data else None
    
    def get_ratings_by_ride_id(self, ride_id: str) -> List[Dict]:
        response = self.supabase.table('ride_ratings').select("*").eq('ride_id', ride_id).execute()
        return response.data
    
    def get_rating_by_ride_and_rater(self, ride_id: str, rater_id: str) -> Optional[Dict]:
        response = self.supabase.table('ride_ratings')\
            .select("*")\
            .eq('ride_id', ride_id)\
            .eq('rater_id', rater_id)\
            .execute()
        return response.data[0] if response.data else None
    
    def get_ratings_for_user(self, user_id: str) -> List[Dict]:
        """Get all ratings received by a user (as a rider)"""
        response = self.supabase.table('ride_ratings')\
            .select("*")\
            .eq('rated_user_id', user_id)\
            .eq('rater_type', 'driver')\
            .execute()
        return response.data
    
    def get_ratings_for_driver(self, driver_id: str) -> List[Dict]:
        """Get all ratings received by a driver"""
        response = self.supabase.table('ride_ratings')\
            .select("*")\
            .eq('rated_user_id', driver_id)\
            .eq('rater_type', 'user')\
            .execute()
        return response.data
    
    def update_rating(self, rating_id: str, updates: Dict) -> Optional[Dict]:
        updates["updated_at"] = datetime.now().isoformat()
        response = self.supabase.table('ride_ratings').update(updates).eq('rating_id', rating_id).execute()
        return response.data[0] if response.data else None