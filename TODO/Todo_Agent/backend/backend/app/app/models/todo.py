from sqlalchemy import Column, Integer, String, DateTime
from datetime import UTC,datetime
from app.db.session import Base
from sqlalchemy.orm import Session

class Todos(Base):
    __tablename__ = "Todos"
    
    id = Column(Integer, primary_key=True, index=True)
    todo_task = Column(String, nullable=False)
    created_at = Column(DateTime,default=datetime.now(UTC))
    updated_at = Column(DateTime, default=datetime.now(UTC))
  
    @classmethod
    def get_all_todos(cls,db: Session= Session):
        print("Fetching all todos...")
        result= db.query(cls).all()
        return result

    @classmethod
    def create_todos(cls,db: Session, task: str):
        print(f"Creating new task: {task}")
        new_task = cls(todo_task=task)
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        return new_task.id # Return the ID of the created task
    
    @classmethod
    def delete_todos(cls,db: Session, task: int):
        print(f"Attempting to delete task: {task}")
        task_exist = db.query(cls).filter(cls.todo_task.ilike(f"%{task}%")).first()
        if task_exist:
            db.delete(task_exist)
            db.commit()
            return True
        return False
    
    @classmethod
    def delete_todos_by_id(cls,db: Session, task_id: int):
        print(f"Attempting to delete task with ID: {task_id}")
        task_exist = db.query(cls).filter(cls.id == task_id).first()
        if task_exist:
            db.delete(task_exist)
            db.commit()
            return True
        return False