from fastapi import APIRouter, status
from .schemas import UserCreationSchema

router = APIRouter(tags=['Users'])



@router.post('/create', response_model=UserCreationSchema, status_code=status.HTTP_201_CREATED)
def create_user():
    pass

@router.delete('/delete', status_code=status.HTTP_204_NO_CONTENT)
def delete_user():
    pass