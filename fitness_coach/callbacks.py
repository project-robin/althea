import logging
import uuid
from google.adk.events import Event  # For the Event object used with session.append_event
# Updated import for compatibility with google-generativeai 0.8.5
from google.generativeai.types import ContentDict as Content, PartDict as Part # For LLM message content and parts

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

def on_before_tool_use(tool, args, tool_context):
    logger.info(f"Callback: Before Tool Use - Tool: {tool.name}, Args: {args}")
    # ... existing code ...

def on_after_tool_use(tool, args, tool_response, tool_context):
    logger.info(f"Callback: After Tool Use - Tool: {tool.name}, Result: {tool_response}")
    # ... existing code ...

def on_before_agent_run(callback_context):
    logger.info(f"Callback: Before Agent Run")
    # ... existing code ...

def on_after_agent_run(callback_context):
    logger.info(f"Callback: After Agent Run")
    # ... existing code ...

def on_before_model_sending(callback_context, llm_request):
    # Log prompt details, be mindful of prompt size
    prompt_summary = llm_request.contents[0].parts[0].text[:200] + '...' if len(llm_request.contents[0].parts[0].text) > 200 else llm_request.contents[0].parts[0].text
    logger.info(f"Callback: Before Model Sending - Prompt: {prompt_summary}")
    
    # Check if this is the first interaction based on state tracking
    is_first_interaction = callback_context.state.get('is_first_interaction', True)
    
    # If this is the first message from the user
    if is_first_interaction:
        # Mark that we've now seen the first interaction
        callback_context.state['is_first_interaction'] = False
        logger.info("First user interaction detected. Ensuring user_id is available.")
        
        # Get the user ID from the context state or create a new one if it doesn't exist
        import uuid
        user_id = callback_context.state.get('user_id')
        if not user_id:
            # Generate a new user ID if not present
            user_id = f"user_{uuid.uuid4().hex[:8]}"
            callback_context.state['user_id'] = user_id
            logger.info(f"Created new user_id: {user_id}")
        else:
            logger.info(f"Found existing user_id: {user_id}")
        
        # Add first interaction context to the prompt
        first_interaction_context = f"\nThis is the user's first interaction. Their unique user ID is {user_id}. Remember to greet them, mention you've created their user ID, display the ID, explain your capabilities, and ask about their fitness goals."
        
        # Append to the system message part of the request
        # The system message is typically the first part of the first content
        if hasattr(llm_request, 'contents') and llm_request.contents:
            # Find the system message part
            for content in llm_request.contents:
                if hasattr(content, 'parts') and content.parts:
                    for part in content.parts:
                        if hasattr(part, 'text') and 'personalized AI Fitness Manager' in part.text:
                            # This looks like our system instruction/prompt
                            part.text += first_interaction_context
                            logger.info("Added first interaction context to prompt")
                            break
    # ... existing code ...

async def on_after_model_sending(callback_context, llm_response):
    # Log response details, be mindful of response size
    response_summary = "No text response received."
    
    # Check if user_id exists in state - this is critical for all agent interactions
    user_id = callback_context.state.get('user_id')
    if not user_id:
        # If user_id doesn't exist, check if it exists in the frontend session state
        # If not, generate a new one and save it to our state
        import uuid
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        callback_context.state['user_id'] = user_id
        logger.info(f"Created new user_id in after_model callback: {user_id}")
    
    # Ensure the user_id is available in the session state for future interactions
    is_first_agent_response = callback_context.state.get('is_first_interaction', False)
    
    # If this is the first response from the agent and user_id isn't mentioned in the response,
    # we can append an event with the user ID information
    if is_first_agent_response and hasattr(llm_response, 'content') and llm_response.content:
        # Check if the response already includes the user ID
        response_text = ""
        if hasattr(llm_response.content, 'parts') and llm_response.content.parts:
            for part in llm_response.content.parts:
                if hasattr(part, 'text') and part.text:
                    response_text = part.text
                    break
        
        # If the response doesn't mention the user ID, log this information
        if user_id not in response_text:
            logger.info(f"User ID {user_id} not mentioned in response. This would be a good place to inform the user, but we don't have access to append_event directly.")
    
    
    # Check for food logging confirmation and trigger tool call
    try:
        # Access food logging confirmation flag from state
        food_logging_confirmation_pending = callback_context.state.get('food_logging_confirmation_pending', False)
        if food_logging_confirmation_pending:
            # Since we're using state-based approach, we already know the agent asked for confirmation
            # We need to check if the user confirmed - we can use the llm_response to determine this
            # This is a simplified check based on the llm_response content which contains the user's last message
            response_text = ""
            if hasattr(llm_response, 'content') and llm_response.content and hasattr(llm_response.content, 'parts'):
                for part in llm_response.content.parts:
                    if hasattr(part, 'text') and part.text:
                        response_text = part.text.lower()
                        break
            
            # Simple check for confirmation - can be enhanced
            user_confirmed = "yes" in response_text or "add it" in response_text
            agent_asked_for_food_log_confirm = True  # We know this from the state flag
            if user_confirmed:
                logger.info("Food logging confirmation detected. Attempting to trigger add_user_food_entry_tool.")
                # Reset the confirmation flag
                callback_context.state['food_logging_confirmation_pending'] = False
                # Here you would programmatically call the add_user_food_entry_tool.
                # This requires access to the tool instance and necessary arguments (user_id, food_name, etc.)
                # which need to be stored in the state or accessible via the context.
                # For now, I will just log that it *should* be triggered.
                # TODO: Ensure the agent's previous step stores food details and user_id in callback_context.state
                try:
                    # Retrieve necessary data from state - ASSUMING they are stored here
                    user_id = callback_context.state.get('user_id') # Assuming user_id is stored in state
                    food_entry_data = callback_context.state.get('pending_food_entry') # Assuming food details are stored here

                    if not user_id or not food_entry_data:
                        logger.error("Required food logging data or user_id not found in state.")
                        # Optionally add an event to inform the user
                        # await callback_context.session.append_event(...) # Need to figure out how to add event from callback
                        return # Stop processing in this callback

                    # Access the tool instance. This requires the tool to be accessible from the callback scope.
                    # A common pattern is to pass the tool instances to the callback during agent initialization
                    # or access them via a service locator pattern available in callback_context.
                    # For this example, I will assume add_user_food_entry_tool is directly accessible in this scope.
                    # TODO: Refine how to access tool instance from callback.
                    from fitness_coach.tools.database_tools import add_user_food_entry_tool_func # Import the function directly for now
                    from datetime import datetime
                    current_date = datetime.now().strftime('%Y-%m-%d') # Get current date

                    # Call the tool function directly (since it's an async function, need to await)
                    # Note: Calling the function directly bypasses ADK's normal tool execution flow (like before/after tool callbacks).
                    # A more proper way might involve signaling ADK to call the tool, but that's more complex.
                    logger.info(f"Calling add_user_food_entry_tool_func with data: {food_entry_data}")
                    tool_result = await add_user_food_entry_tool_func(
                        user_id=user_id,
                        food_name=food_entry_data.get('food_name'),
                        quantity=food_entry_data.get('quantity'),
                        calories=food_entry_data.get('calories'),
                        protein=food_entry_data.get('protein'),
                        carbs=food_entry_data.get('carbs'),
                        fat=food_entry_data.get('fat'),
                        date=current_date
                    )

                    logger.info(f"add_user_food_entry_tool_func result: {tool_result}")
                    # TODO: Add an event to the history/session state to reflect the tool_result for the user
                    # Instead of adding events, just log the result
                    if tool_result and tool_result.get("status") == "success":
                        logger.info(f"Food entry added successfully: {tool_result.get('message', 'No details available')}")
                    else:
                        error_message = tool_result.get("message", "An error occurred while logging food.") if tool_result else "An unknown error occurred while logging food."
                        logger.error(f"Error logging food: {error_message}")

                except Exception as e:
                    logger.error(f"Error calling add_user_food_entry_tool_func from callback: {e}")
                    # Just log the error instead of trying to append an event
                    logger.error(f"An unexpected error occurred during food logging: {e}")
                
    except Exception as e:
        logger.error(f"Error in on_after_model_sending callback during food log confirmation check: {e}")

    if hasattr(llm_response, 'content') and llm_response.content and hasattr(llm_response.content, 'parts') and llm_response.content.parts:
        # Assuming the first part contains text for a standard text response
        first_part = llm_response.content.parts[0]
        if hasattr(first_part, 'text') and first_part.text:
            response_text = str(first_part.text)
            response_summary = response_text[:200] + '...' if len(response_text) > 200 else response_text
        elif hasattr(first_part, 'function_call') and first_part.function_call:
            response_summary = f"Function call: {first_part.function_call.name}"
        elif hasattr(first_part, 'function_response') and first_part.function_response:
             response_summary = f"Function response: {first_part.function_response.name}"

    logger.info(f"Callback: After Model Sending - Response: {response_summary}")
    # ... existing code ... 