from fastapi import APIRouter, Depends
from .service import get_profile
from .schemas import UserProfile
from auth.utils import get_current_user

router = APIRouter(prefix='/user', tags=['User'])

@router.get("/profile", response_model=UserProfile)
def get_profile(user=Depends(get_current_user)):
    return get_profile(user['id'])


'''
@router.put("/profile/{id}")
def update_profile(data: UpdateProfile, response_model=UserProfile):
    return update_profile(id, data)
'''
