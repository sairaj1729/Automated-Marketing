from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class LinkedInAuthRequest(BaseModel):
    code: str

class LinkedInAuthResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    member_urn: Optional[str] = None