from typing import List, Optional, Dict
from abc import ABC, abstractmethod
from datetime import datetime

class IPaymentRepository(ABC):
    @abstractmethod
    def create_payment(self, payment_data: Dict) -> Dict:
        pass
    
    @abstractmethod
    def get_payment_by_id(self, payment_id: str) -> Optional[Dict]:
        pass
    
    @abstractmethod
    def get_payment_by_ride_id(self, ride_id: str) -> Optional[Dict]:
        pass
    
    @abstractmethod
    def update_payment(self, payment_id: str, updates: Dict) -> Optional[Dict]:
        pass
    
    @abstractmethod
    def get_payments_by_transaction_id(self, transaction_id: str) -> List[Dict]:
        pass

class PaymentRepository(IPaymentRepository):
    def __init__(self, supabase_client):
        self.supabase = supabase_client
    
    def create_payment(self, payment_data: Dict) -> Dict:
        # Ensure updated_at is set
        if "updated_at" not in payment_data:
            payment_data["updated_at"] = datetime.now().isoformat()
            
        response = self.supabase.table('payments').insert(payment_data).execute()
        if response.data:
            return response.data[0]
        raise Exception("Failed to create payment")
    
    def get_payment_by_id(self, payment_id: str) -> Optional[Dict]:
        response = self.supabase.table('payments').select("*").eq('id', payment_id).execute()
        return response.data[0] if response.data else None
    
    def get_payment_by_ride_id(self, ride_id: str) -> Optional[Dict]:
        # Get the most recent payment for the ride
        response = self.supabase.table('payments')\
            .select("*")\
            .eq('ride_id', ride_id)\
            .order('created_at', desc=True)\
            .limit(1)\
            .execute()
        return response.data[0] if response.data else None
    
    def update_payment(self, payment_id: str, updates: Dict) -> Optional[Dict]:
        # Always update the updated_at field
        updates["updated_at"] = datetime.now().isoformat()
        
        response = self.supabase.table('payments').update(updates).eq('id', payment_id).execute()
        return response.data[0] if response.data else None
    
    def get_payments_by_transaction_id(self, transaction_id: str) -> List[Dict]:
        response = self.supabase.table('payments').select("*").eq('transaction_id', transaction_id).execute()
        return response.data
    
    def get_all_payments_by_ride_id(self, ride_id: str) -> List[Dict]:
        """Get all payment attempts for a ride"""
        response = self.supabase.table('payments')\
            .select("*")\
            .eq('ride_id', ride_id)\
            .order('created_at', desc=True)\
            .execute()
        return response.data