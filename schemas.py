from pydantic import BaseModel, EmailStr

class Message(BaseModel):
    message: str

class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserDB(UserSchema):
    id: int

class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr

class UserList(BaseModel):
    users: list[UserPublic]

class UserPG(BaseModel):
    username: str
    email: str
    password: str

class UserUpdatePG(BaseModel):
    username: str = None
    email: str = None
    password: str = None
