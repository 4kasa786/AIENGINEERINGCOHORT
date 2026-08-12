from pydantic import BaseModel,Field,EmailStr,field_validator

class User(BaseModel):
    id:int = Field(gt = 0 , description = "The Positive integer ID of the user")
    name:str
    username:str = Field(alias = "userName")
    email:EmailStr
    is_active:bool = True

    @field_validator("username")
    @classmethod
    def validate_username_must_be_alphanumeric(cls,v:str)->str:
        if not v.isalnum():
            raise ValueError("Username must be alphanumeric")
        return v.lower()
        


user = User(id = 1,name="user",email="user@user.com",userName = "johndoe123")
print(user)

raw_data = {
    "id":2,
    "name":"Adam",
    "email":"adam.smith@example.com",
    "userName":"adamsmith",
    "is_active":False
}

user2 = User.model_validate(raw_data)


print(user2)
print(user2.model_dump())
print(user2.model_dump_json())
print(user2.model_dump_json(by_alias = True))