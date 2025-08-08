from typing import List, Optional, Dict
from abc import ABC, abstractmethod

from ..models.entities import Ride

class IRideRepository(ABC):
    @abstractmethod
    def create_ride(self, ride: Ride) -> Ride:
        pass
    
    @abstractmethod
    def get_ride_by_id(self, ride_id: str) -> Optional[Ride]:
        pass
    
    @abstractmethod
    def get_rides_by_user_id(self, user_id: str) -> List[Ride]:
        pass
    
    @abstractmethod
    def get_rides_by_status(self, status: str) -> List[Ride]:
        pass
    
    @abstractmethod
    def update_ride(self, ride_id: str, updates: Dict) -> Optional[Ride]:
        pass

class RideRepository(IRideRepository):
    def __init__(self, supabase_client):
        self.supabase = supabase_client
    
    def create_ride(self, ride_data: Dict) -> Dict:
        response = self.supabase.table('rides').insert(ride_data).execute()
        if response.data:
            return response.data[0]
        raise Exception("Failed to create ride")
    
    def get_ride_by_id(self, ride_id: str) -> Optional[Dict]:
        response = self.supabase.table('rides').select("*").eq('ride_id', ride_id).execute()
        return response.data[0] if response.data else None
    
    def get_rides_by_user_id(self, user_id: str) -> List[Dict]:
        response = self.supabase.table('rides').select("*").eq('user_id', user_id).execute()
        return response.data
    
    def get_rides_by_status(self, status: str) -> List[Dict]:
        response = self.supabase.table('rides').select("*").eq('status', status).execute()
        return response.data
    
    def update_ride(self, ride_id: str, updates: Dict) -> Optional[Dict]:
        response = self.supabase.table('rides').update(updates).eq('ride_id', ride_id).execute()
        return response.data[0] if response.data else None

class RideApplicationRepository:
    def __init__(self, supabase_client):
        self.supabase = supabase_client
    
    def create_application(self, application_data: Dict) -> Dict:
        response = self.supabase.table('ride_applications').insert(application_data).execute()
        if response.data:
            return response.data[0]
        raise Exception("Failed to create application")
    
    def get_applications_by_ride_id(self, ride_id: str) -> List[Dict]:
        response = self.supabase.table('ride_applications')\
            .select("*, users(name, phone), driver_profiles(license, vehicle_info)")\
            .eq('ride_id', ride_id).execute()
        return response.data
    
    def check_existing_application(self, ride_id: str, driver_id: str) -> Optional[Dict]:
        response = self.supabase.table('ride_applications')\
            .select("*").eq('ride_id', ride_id).eq('driver_id', driver_id).execute()
        return response.data[0] if response.data else None