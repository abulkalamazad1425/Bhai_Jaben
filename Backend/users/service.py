from fastapi import HTTPException, status, Request
from .schemas import UserProfile, UserProfileUpdate
from typing import Dict, Optional
from datetime import datetime

class UserService:

    def __init__(self, supabase_client):
        self.supabase = supabase_client

    def view_profile(self, current_user_id) -> UserProfile:
        try:
            response = self.supabase.table('users') \
                .select("*") \
                .eq('id', current_user_id) \
                .execute()

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Profile not found"
                )

            user_data = response.data[0]  
            return UserProfile(
                id=user_data["id"],          
                name=user_data["name"],
                email=user_data["email"],
                phone=user_data["phone"],
                role=user_data["role"],
                created_at=user_data["created_at"]
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    def update_profile(self, current_user_id: str, update_data: UserProfileUpdate) -> Dict[str, str]:
        try:
            # Check if user exists
            existing_user = self.get_user_data(current_user_id)
            
            # Prepare update data - only include fields that are being updated
            updates = {}
            
            if update_data.name is not None:
                updates["name"] = update_data.name
            
            if update_data.email is not None:
                # Check if email is already taken by another user
                if update_data.email != existing_user["email"]:
                    email_check = self.supabase.table('users') \
                        .select("id") \
                        .eq('email', update_data.email) \
                        .neq('id', current_user_id) \
                        .execute()
                    
                    if email_check.data:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email is already taken by another user"
                        )
                
                updates["email"] = update_data.email
            
            if update_data.phone is not None:
                # Check if phone is already taken by another user
                if update_data.phone != existing_user["phone"]:
                    phone_check = self.supabase.table('users') \
                        .select("id") \
                        .eq('phone', update_data.phone) \
                        .neq('id', current_user_id) \
                        .execute()
                    
                    if phone_check.data:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Phone number is already taken by another user"
                        )
                
                updates["phone"] = update_data.phone
            
            # If no updates provided
            if not updates:
                return {"message": "No changes to update"}
            
            # Perform the update
            response = self.supabase.table('users') \
                .update(updates) \
                .eq('id', current_user_id) \
                .execute()

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to update profile"
                )

            return {"message": "Profile updated successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    # Method for other modules to get user data
    def get_user_data(self, user_id) -> Dict:
        try:
            response = self.supabase.table('users') \
                .select("*") \
                .eq('id', user_id) \
                .execute()

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            return response.data[0]
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    # Method to update user data (for other modules like driver service)
    def update_user_data(self, user_id, updates: Dict) -> Dict:
        try:
            if not updates:
                return {"message": "No updates provided"}

            # Validate email uniqueness if email is being updated
            if "email" in updates:
                existing_user = self.get_user_data(user_id)
                if updates["email"] != existing_user["email"]:
                    email_check = self.supabase.table('users') \
                        .select("id") \
                        .eq('email', updates["email"]) \
                        .neq('id', user_id) \
                        .execute()
                    
                    if email_check.data:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email is already taken by another user"
                        )

            # Validate phone uniqueness if phone is being updated
            if "phone" in updates:
                existing_user = self.get_user_data(user_id)
                if updates["phone"] != existing_user["phone"]:
                    phone_check = self.supabase.table('users') \
                        .select("id") \
                        .eq('phone', updates["phone"]) \
                        .neq('id', user_id) \
                        .execute()
                    
                    if phone_check.data:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Phone number is already taken by another user"
                        )

            response = self.supabase.table('users') \
                .update(updates) \
                .eq('id', user_id) \
                .execute()

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to update user information"
                )

            return {"message": "User data updated successfully"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    # Method to verify user role
    def verify_user_role(self, user_id, expected_role: str) -> bool:
        try:
            response = self.supabase.table('users') \
                .select("role") \
                .eq('id', user_id) \
                .execute()

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            return response.data[0]["role"] == expected_role
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    # Method to get user profile by user_id (for internal use)
    def get_user_profile_by_id(self, user_id: str) -> UserProfile:
        try:
            user_data = self.get_user_data(user_id)
            return UserProfile(
                id=user_data["id"],          
                name=user_data["name"],
                email=user_data["email"],
                phone=user_data["phone"],
                role=user_data["role"],
                created_at=user_data["created_at"]
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    def get_all_users_admin(self, page: int = 1, limit: int = 50) -> Dict:
        """Get all users for admin with pagination"""
        try:
            offset = (page - 1) * limit
            
            # Get total count
            count_response = self.supabase.table('users').select('*', count='exact').execute()
            total_count = count_response.count
            
            # Get users with pagination
            response = self.supabase.table('users')\
                .select('*')\
                .range(offset, offset + limit - 1)\
                .order('created_at', desc=True)\
                .execute()
            
            users = []
            for user in response.data:
                # Get ride count and total spent for each user
                ride_stats = self._get_user_ride_stats(user['user_id'])
                
                user_data = {
                    "user_id": user['user_id'],
                    "name": user['name'],
                    "email": user['email'],
                    "phone": user['phone'],
                    "role": user.get('role', 'user'),
                    "is_active": user.get('is_active', True),
                    "created_at": user['created_at'],
                    "last_login": user.get('last_login'),
                    "total_rides": ride_stats.get('total_rides', 0),
                    "total_spent": ride_stats.get('total_spent', 0.0)
                }
                users.append(user_data)
            
            return {
                "users": users,
                "total_count": total_count
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching users: {str(e)}"
            )
    
    def _get_user_ride_stats(self, user_id: str) -> Dict:
        """Get ride statistics for a user"""
        try:
            # Get ride count
            rides_response = self.supabase.table('rides')\
                .select('*', count='exact')\
                .eq('user_id', user_id)\
                .execute()
            
            total_rides = rides_response.count
            
            # Get total spent from payments
            payments_response = self.supabase.table('payments')\
                .select('amount')\
                .in_('ride_id', [ride['ride_id'] for ride in rides_response.data])\
                .eq('status', 'completed')\
                .execute()
            
            total_spent = sum(payment['amount'] for payment in payments_response.data)
            
            return {
                "total_rides": total_rides,
                "total_spent": total_spent
            }
            
        except Exception:
            return {"total_rides": 0, "total_spent": 0.0}
    
    def deactivate_user_admin(self, user_id: str, admin_id: str, reason: Optional[str] = None) -> Dict:
        """Deactivate user by admin"""
        try:
            # Update user status
            response = self.supabase.table('users')\
                .update({
                    'is_active': False,
                    'deactivated_by': admin_id,
                    'deactivated_at': datetime.now().isoformat(),
                    'deactivation_reason': reason,
                    'updated_at': datetime.now().isoformat()
                })\
                .eq('user_id', user_id)\
                .execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            return {"message": "User deactivated successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deactivating user: {str(e)}"
            )
    
    def activate_user_admin(self, user_id: str, admin_id: str) -> Dict:
        """Activate user by admin"""
        try:
            # Update user status
            response = self.supabase.table('users')\
                .update({
                    'is_active': True,
                    'activated_by': admin_id,
                    'activated_at': datetime.now().isoformat(),
                    'deactivation_reason': None,
                    'updated_at': datetime.now().isoformat()
                })\
                .eq('user_id', user_id)\
                .execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            return {"message": "User activated successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error activating user: {str(e)}"
            )
    
    def get_user_stats_admin(self) -> Dict:
        """Get user statistics for admin dashboard"""
        try:
            # Total users
            total_response = self.supabase.table('users').select('*', count='exact').execute()
            total_users = total_response.count
            
            # Active users
            active_response = self.supabase.table('users')\
                .select('*', count='exact')\
                .eq('is_active', True)\
                .execute()
            active_users = active_response.count
            
            # Users registered today
            today = datetime.now().date().isoformat()
            today_response = self.supabase.table('users')\
                .select('*', count='exact')\
                .gte('created_at', today)\
                .execute()
            today_users = today_response.count
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "today_users": today_users
            }
            
        except Exception as e:
            return {
                "total_users": 0,
                "active_users": 0,
                "today_users": 0
            }