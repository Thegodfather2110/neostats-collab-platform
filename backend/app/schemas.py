from pydantic import BaseModel, EmailStr, Field

class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

class ProjectIn(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    description: str = Field(default="", max_length=5000)

class TaskIn(BaseModel):
    project_id: int
    title: str = Field(min_length=2, max_length=200)
    description: str = Field(default="", max_length=5000)
    status: str = "To do"
    priority: str = "Medium"
    assignee_id: int | None = None
    due_date: str | None = None

class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    status: str | None = None
    priority: str | None = None
    assignee_id: int | None = None
    due_date: str | None = None
    version: int

class CommentIn(BaseModel):
    body: str = Field(min_length=1, max_length=3000)
