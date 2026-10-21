from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import PostStatus, PostType, ResponseStatus


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    email: EmailStr
    name: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class PostCreate(BaseModel):
    type: PostType
    title: str = Field(min_length=3, max_length=180)
    description: str = Field(min_length=10)
    looking_for: str = Field(min_length=2, max_length=500)


class PostOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    author_id: str
    type: PostType
    title: str
    description: str
    looking_for: str
    status: PostStatus
    created_at: datetime


class ResponseCreate(BaseModel):
    message: str = Field(default="", max_length=2000)


class ResponseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    post_id: str
    applicant_id: str
    message: str
    status: ResponseStatus
    created_at: datetime


class ResponseDecision(BaseModel):
    status: ResponseStatus
