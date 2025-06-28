from pydantic import BaseModel

# Pydantic models
class TodoRequest(BaseModel):
    user_input: str

class TodoResponse(BaseModel):
    message: str
    success: bool = True