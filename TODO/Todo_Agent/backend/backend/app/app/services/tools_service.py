import logging
from app.helpers import prompt_helper as prompth
from app.helpers import ai_helper as aih
from sqlalchemy.orm import Session
from typing import Any, Tuple
from app.models.todo import Todos


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def execute_database_operation(tool: str, args: Any, db: Session) -> Tuple[bool, str]:
    """Execute database operation and return result."""
    try:
        if tool == "get_all_todos":
            todos = Todos.get_all_todos(db)
            if not todos:
                return True, "No todos found"
            todo_list = [f"ID: {todo.id} - Task: '{todo.todo_task}'" for todo in todos]
            return True, f"Current todos: {todo_list}"
        
        elif tool == "create_todos" and args:
            try:
                todo_id = Todos.create_todos(db=db, task=str(args))
                if todo_id:
                    return True, f"Successfully created todo: '{args}' (ID: {todo_id})"
                else:
                    return False, f"Failed to create todo: '{args}'"
            except Exception as e:
                return False, f"Failed to create todo '{args}': {str(e)}"
        
        elif tool == "delete_todos" and args:
            try:
                deleted = Todos.delete_todos(db=db, task=str(args))
                if deleted:
                    return True, f"Successfully deleted todo: '{args}'"
                else:
                    return False, f"Todo '{args}' not found - nothing was deleted"
            except Exception as e:
                return False, f"Failed to delete todo '{args}': {str(e)}"
        
        elif tool == "delete_todos_by_id" and args:
            try:
                if isinstance(args, list):
                    args = args[0]
                task_id = int(args)
                deleted = Todos.delete_todos_by_id(db=db, task_id=task_id)
                if deleted:
                    return True, f"Successfully deleted todo with ID: {task_id}"
                else:
                    return False, f"Todo with ID {task_id} not found - nothing was deleted"
            except ValueError:
                return False, f"Invalid task ID: {args}"
            except Exception as e:
                return False, f"Failed to delete todo with ID {args}: {str(e)}"
        
        else:
            return False, f"Invalid tool '{tool}' or missing arguments"
            
    except Exception as e:
        logger.error(f"Error executing tool {tool}: {e}")
        return False, f"Error executing {tool}: {str(e)}"
    
def process_todo_request(user_input: str, db: Session) -> str:
    """Process todo request using functional approach."""
    client = aih.create_gemini_client()
    max_iterations = 5
    iteration_count = 0
    
    # Start with initial planning
    current_prompt = prompth.build_prompt(prompth.SYSTEM_PROMPT, user_input)
    
    while iteration_count < max_iterations:
        iteration_count += 1
        
        try:
            # Get LLM response
            parsed_response = aih.call_llm(current_prompt, client)
            
            if "error" in parsed_response:
                return f"Error processing request: {parsed_response['error']}"
            
            # Handle PLAN response
            if "PLAN" in parsed_response:
                plan_data = parsed_response["PLAN"]
                tool = plan_data.get("tool")
                args = plan_data.get("args")
                
                # Execute the planned operation
                success, tool_result = execute_database_operation(tool, args, db)
                
                # Check if this is a multi-step operation
                is_multi_step = plan_data.get("is_multi_step", False)
                
                if is_multi_step and success:
                    # Prepare for next step
                    context = {
                        "type": "continue",
                        "tool": tool,
                        "args": args,
                        "success": success,
                        "result": tool_result
                    }
                    current_prompt = prompth.build_prompt(prompth.SYSTEM_PROMPT, user_input, context)
                    continue
                else:
                    # Single step operation or failed multi-step - provide output
                    context = {
                        "type": "output",
                        "plan": plan_data,
                        "success": success,
                        "result": tool_result
                    }
                    current_prompt = prompth.build_prompt(prompth.SYSTEM_PROMPT, user_input, context)
                    continue
            
            # Handle CONTINUE response 
            elif "CONTINUE" in parsed_response:
                continue_data = parsed_response["CONTINUE"]
                tool = continue_data.get("tool")
                args = continue_data.get("args")
                
                # Execute the continued operation
                success, tool_result = execute_database_operation(tool, args, db)
                
                # Check if this is the final step
                is_final_step = continue_data.get("is_final_step", True)
                
                if is_final_step or not success:
                    # Final step or failed operation - provide output
                    context = {
                        "type": "final_output",
                        "tool": tool,
                        "args": args,
                        "success": success,
                        "result": tool_result
                    }
                    current_prompt = prompth.build_prompt(prompth.SYSTEM_PROMPT, user_input, context)
                    continue
                else:
                    # More steps needed
                    context = {
                        "type": "continue",
                        "tool": tool,
                        "args": args,
                        "success": success,
                        "result": tool_result
                    }
                    current_prompt = prompth.build_prompt(prompth.SYSTEM_PROMPT, user_input, context)
                    continue
            
            # Handle OUTPUT response
            elif "OUTPUT" in parsed_response:
                output_data = parsed_response["OUTPUT"]
                return output_data.get("message", "Operation completed.")
            
            else:
                return "I'm having trouble understanding the response format. Please try again."
                
        except Exception as e:
            logger.error(f"Error processing user input: {e}")
            return f"An error occurred while processing your request: {str(e)}"
    
    return "The operation took too many steps. Please try breaking it down into simpler requests."