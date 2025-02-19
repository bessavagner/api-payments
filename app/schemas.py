from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from decimal import Decimal
from typing import Optional

class PaymentSchema(BaseModel):

    date: datetime
    document: str
    beneficiary: str
    amount: Decimal
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):

    username: str
    email: EmailStr
    password: str

    model_config = ConfigDict()
class UserPasswordUpdate(BaseModel):
   
    old_password: str
    new_password: str

    model_config = ConfigDict()

class ApiKeySchema(BaseModel):
    
    api_key: str

    model_config = ConfigDict(from_attributes=True)
