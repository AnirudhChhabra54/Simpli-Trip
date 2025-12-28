"""
Dialog Manager - Conversation Handler for Trip Planning
Manages multi-turn chat sessions using LM Studio for natural language understanding.
"""
from typing import Dict, Any, List, Optional
from utils.logger import logger

# Import LM Studio adapter
try:
    from services.lmstudio_service import lmstudio_service, chat as lm_chat
    lm_studio_available = True
except Exception as e:
    logger.warning(f"LM Studio not available in dialog_manager: {e}")
    lm_studio_available = False
    lmstudio_service = None
    lm_chat = None


class DialogManager:
    """Manages conversational flow for trip planning using LM Studio."""
    
    def __init__(self):
        """Initialize dialog manager with session storage."""
        self.sessions: Dict[str, Dict[str, Any]] = {}
    
    def start_session(self, session_id: str, initial_message: str) -> str:
        """
        Start a new chat session and get LM Studio's response to the initial message.
        
        Args:
            session_id: Unique identifier for this chat session
            initial_message: User's opening message (e.g., "I want to visit Goa for 3 days")
        
        Returns:
            LM Studio's plain text response as a string
        """
        logger.info(f"Starting dialog session: {session_id} with message: {initial_message}")
        
        # Initialize session storage
        self.sessions[session_id] = {
            'messages': [
                {"role": "system", "content": "You are a premium AI travel concierge for SimpliTrip. Help the user plan their vacation with deeply engaging, personalized suggestions. You MUST format all responses using rich Markdown. Use **bolding** for important terms, bulleted lists for options, and 🌍 travel emojis to make your replies visually stunning and highly scannable. Never send a flat block of text. If you suggest places, bold their names."},
                {"role": "user", "content": initial_message}
            ]
        }
        
        # Get reply from LM Studio
        return self.continue_session(session_id, "")
    
    def continue_session(self, session_id: str, user_message: str) -> str:
        """
        Continue an existing chat session.
        
        Args:
            session_id: Session identifier
            user_message: User's follow-up message (can be empty for first response)
        
        Returns:
            LM Studio's plain text response as a string
        """
        if session_id not in self.sessions:
            logger.warning(f"Session {session_id} not found, starting new session")
            return self.start_session(session_id, user_message or "I want to plan a trip")
        
        session = self.sessions[session_id]
        
        # If this is a follow-up message, add it to history
        if user_message.strip():
            session['messages'].append({"role": "user", "content": user_message})
        
        # Get response from LM Studio
        try:
            if not lm_studio_available or lm_chat is None:
                logger.error("LM Studio not available")
                return "Sorry, the LLM service is not available. Please try again later."
            
            logger.info(f"Calling LM Studio with {len(session['messages'])} messages")
            
            # Call LM Studio with the conversation history
            response = lm_chat(
                messages=session['messages'],
                max_tokens=1024,
                temperature=0.7
            )
            
            logger.info(f"LM Studio response type: {type(response)}, content: {response}")
            
            # Extract the text response
            reply_text = response.get('text', '') if isinstance(response, dict) else str(response)
            
            if not reply_text or reply_text.strip() == '':
                logger.warning(f"Empty response from LM Studio: {response}")
                reply_text = "I'm here to help you plan your trip. Could you tell me more about your preferences?"
            
            # Add assistant response to history for continuity
            session['messages'].append({
                "role": "assistant",
                "content": reply_text
            })
            
            logger.info(f"Session {session_id} - LM Studio reply: {reply_text[:100]}...")
            return reply_text
            
        except Exception as e:
            import traceback
            error_msg = f"Error getting LM Studio response: {str(e)}"
            logger.error(error_msg)
            logger.error(f"Traceback: {traceback.format_exc()}")
            return error_msg
    
    def get_session_history(self, session_id: str) -> Optional[List[Dict[str, str]]]:
        """
        Retrieve the full conversation history for a session.
        
        Args:
            session_id: Session identifier
        
        Returns:
            List of message dicts or None if session doesn't exist
        """
        if session_id not in self.sessions:
            return None
        return self.sessions[session_id].get('messages', [])
    
    def clear_session(self, session_id: str):
        """
        Clear a session from memory.
        
        Args:
            session_id: Session identifier
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Cleared session: {session_id}")


# Create global instance
dialog_manager = DialogManager()
