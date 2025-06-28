from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging
import traceback
from app.schemas.todo import TodoRequest, TodoResponse
from app.services.tools_service import process_todo_request
from app.models.todo import Todos
from app.db.session import get_db


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# API Endpoints
@router.post("/todo", response_model=TodoResponse)
async def process_todo(request: TodoRequest, db: Session = Depends(get_db)):
    """Process todo request via API."""
    try:
        if not request.user_input.strip():
            raise HTTPException(status_code=400, detail="User input cannot be empty")
        
        result = process_todo_request(request.user_input, db)
        
        return TodoResponse(
            message=result,
            success=True
        )
        
    except Exception as e:
        logger.error(f"API error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/todos")
async def get_todos(db: Session = Depends(get_db)):
    """Get all todos."""
    try:
        todos = Todos.get_all_todos(db)
        return {
            "todos": [{"id": todo.id, "task": todo.todo_task} for todo in todos],
            "count": len(todos)
        }
    except Exception as e:
        logger.error(f"Error getting todos: {e}")
        raise HTTPException(status_code=500, detail=str(e))