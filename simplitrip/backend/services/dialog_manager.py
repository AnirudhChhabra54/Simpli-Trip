"""
Dialog Manager - Smart Form-Filling Conversation Handler
Manages multi-turn conversations to collect all required trip information
"""
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
from utils.logger import logger
from services.ollama_service import ollama_service


class DialogState(Enum):
    """States in the dialog flow"""
    INITIAL = "initial"
    COLLECTING_INFO = "collecting_info"
    READY_TO_GENERATE = "ready_to_generate"
    COMPLETED = "completed"


class DialogManager:
    """
    Manages conversational flow to collect trip planning information
    Asks clarifying questions when information is missing
    """
    
    # Required fields for trip planning
    REQUIRED_FIELDS = {
        'destination': {
            'question': "Where would you like to go? (e.g., Goa, Jaipur, Kerala)",
            'validation': lambda x: x is not None and len(str(x).strip()) > 0
        },
        'duration': {
            'question': "How many days are you planning for?",
            'validation': lambda x: x is not None and isinstance(x, (int, float)) and x > 0
        },
        'travelers': {
            'question': "How many people will be traveling?",
            'validation': lambda x: x is not None and isinstance(x, (int, float)) and x > 0
        },
        'budget': {
            'question': "What's your approximate budget in rupees? (e.g., 50000)",
            'validation': lambda x: x is not None and isinstance(x, (int, float)) and x > 0
        },
        'preferences': {
            'question': "What type of trip are you looking for? (e.g., beach, adventure, historical, relaxing)",
            'validation': lambda x: x is not None and isinstance(x, list) and len(x) > 0
        }
    }
    
    def __init__(self):
        """Initialize dialog manager"""
        self.sessions: Dict[str, Dict[str, Any]] = {}
    
    def start_session(self, session_id: str, initial_message: str) -> Dict[str, Any]:
        """
        Start a new dialog session
        
        Args:
            session_id: Unique session identifier
            initial_message: User's initial message
            
        Returns:
            Response dict with next question or ready status
        """
        logger.info(f"Starting dialog session: {session_id}")
        
        # Parse initial message
        parsed = ollama_service.parse_trip_query(initial_message)
        
        # Initialize session
        self.sessions[session_id] = {
            'state': DialogState.INITIAL,
            'collected_info': parsed,
            'conversation_history': [
                {'role': 'user', 'content': initial_message}
            ],
            'missing_fields': []
        }
        
        # Check what's missing and respond
        return self._process_session(session_id)
    
    def continue_session(self, session_id: str, user_message: str) -> Dict[str, Any]:
        """
        Continue an existing dialog session
        
        Args:
            session_id: Session identifier
            user_message: User's response
            
        Returns:
            Response dict with next question or ready status
        """
        if session_id not in self.sessions:
            logger.warning(f"Session {session_id} not found, starting new session")
            return self.start_session(session_id, user_message)
        
        session = self.sessions[session_id]
        
        # Add to conversation history
        session['conversation_history'].append({
            'role': 'user',
            'content': user_message
        })
        
        # Extract information from user's response
        self._extract_info_from_response(session_id, user_message)
        
        # Process and respond
        return self._process_session(session_id)
    
    def _process_session(self, session_id: str) -> Dict[str, Any]:
        """
        Process current session state and determine next action
        
        Args:
            session_id: Session identifier
            
        Returns:
            Response dict
        """
        session = self.sessions[session_id]
        collected = session['collected_info']
        
        # Check which fields are missing
        missing_fields = self._get_missing_fields(collected)
        session['missing_fields'] = missing_fields
        
        if not missing_fields:
            # All information collected!
            session['state'] = DialogState.READY_TO_GENERATE
            return {
                'status': 'ready',
                'message': self._generate_confirmation_message(collected),
                'collected_info': collected,
                'next_action': 'generate_itinerary'
            }
        else:
            # Ask for next missing field
            session['state'] = DialogState.COLLECTING_INFO
            next_field = missing_fields[0]
            question = self.REQUIRED_FIELDS[next_field]['question']
            
            # Add context about what we already know
            context = self._build_context_message(collected, missing_fields)
            
            return {
                'status': 'collecting',
                'message': question,
                'context': context,
                'missing_fields': missing_fields,
                'collected_info': collected,
                'next_action': 'ask_question'
            }
    
    def _get_missing_fields(self, collected_info: Dict[str, Any]) -> List[str]:
        """
        Identify which required fields are missing or invalid
        
        Args:
            collected_info: Currently collected information
            
        Returns:
            List of missing field names
        """
        missing = []
        
        for field, config in self.REQUIRED_FIELDS.items():
            value = collected_info.get(field)
            if not config['validation'](value):
                missing.append(field)
        
        return missing
    
    def _extract_info_from_response(self, session_id: str, user_message: str):
        """
        Extract information from user's response and update session
        
        Args:
            session_id: Session identifier
            user_message: User's message
        """
        session = self.sessions[session_id]
        collected = session['collected_info']
        missing = session['missing_fields']
        
        if not missing:
            return
        
        # Get the field we're currently asking about
        current_field = missing[0]
        
        # Try to extract the specific field from the response
        extracted = self._extract_field_value(current_field, user_message, collected)
        
        if extracted is not None:
            collected[current_field] = extracted
            logger.info(f"Extracted {current_field}: {extracted}")
        else:
            # Try parsing the entire message again
            parsed = ollama_service.parse_trip_query(user_message)
            
            # Update any new information
            for field in self.REQUIRED_FIELDS.keys():
                if field in parsed and parsed[field] is not None:
                    if self.REQUIRED_FIELDS[field]['validation'](parsed[field]):
                        collected[field] = parsed[field]
                        logger.info(f"Updated {field}: {parsed[field]}")
    
    def _extract_field_value(
        self,
        field: str,
        user_message: str,
        context: Dict[str, Any]
    ) -> Optional[Any]:
        """
        Extract a specific field value from user message
        
        Args:
            field: Field name to extract
            user_message: User's message
            context: Current context
            
        Returns:
            Extracted value or None
        """
        import re
        
        message_lower = user_message.lower().strip()
        
        if field == 'destination':
            # Check for common destinations
            destinations = ['goa', 'jaipur', 'kerala', 'udaipur', 'manali', 'delhi', 
                          'mumbai', 'ladakh', 'shimla', 'darjeeling', 'rishikesh']
            for dest in destinations:
                if dest in message_lower:
                    return dest.title()
            # If not found, use the message as destination
            if len(message_lower) > 2 and len(message_lower) < 50:
                return user_message.strip().title()
        
        elif field == 'duration':
            # Extract numbers
            numbers = re.findall(r'\d+', user_message)
            if numbers:
                return int(numbers[0])
            # Check for word numbers
            word_to_num = {
                'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
                'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10
            }
            for word, num in word_to_num.items():
                if word in message_lower:
                    return num
        
        elif field == 'travelers':
            # Extract numbers
            numbers = re.findall(r'\d+', user_message)
            if numbers:
                return int(numbers[0])
            # Check for keywords
            if 'solo' in message_lower or 'alone' in message_lower:
                return 1
            if 'couple' in message_lower or 'two' in message_lower:
                return 2
            if 'family' in message_lower:
                return 4  # Default family size
        
        elif field == 'budget':
            # Extract numbers
            numbers = re.findall(r'\d+', user_message.replace(',', ''))
            if numbers:
                budget = int(numbers[0])
                # Handle 'k' notation
                if 'k' in message_lower:
                    budget *= 1000
                # If number is too small, assume it's in thousands
                if budget < 1000:
                    budget *= 1000
                return budget
        
        elif field == 'preferences':
            # Extract preference keywords
            prefs = []
            keywords = {
                'beach': ['beach', 'sea', 'ocean', 'coastal'],
                'adventure': ['adventure', 'trek', 'hiking', 'climbing', 'rafting'],
                'historical': ['historical', 'history', 'heritage', 'monument', 'fort'],
                'relaxing': ['relax', 'peaceful', 'calm', 'quiet', 'serene'],
                'nature': ['nature', 'wildlife', 'forest', 'mountain'],
                'cultural': ['cultural', 'culture', 'traditional', 'local'],
                'romantic': ['romantic', 'honeymoon', 'couple'],
                'family': ['family', 'kids', 'children']
            }
            
            for pref, words in keywords.items():
                if any(word in message_lower for word in words):
                    prefs.append(pref)
            
            if prefs:
                return prefs
        
        return None
    
    def _build_context_message(
        self,
        collected_info: Dict[str, Any],
        missing_fields: List[str]
    ) -> str:
        """
        Build a context message showing what information we have
        
        Args:
            collected_info: Information collected so far
            missing_fields: Fields still missing
            
        Returns:
            Context message string
        """
        parts = []
        
        if collected_info.get('destination'):
            parts.append(f"Destination: {collected_info['destination']}")
        
        if collected_info.get('duration'):
            parts.append(f"Duration: {collected_info['duration']} days")
        
        if collected_info.get('travelers'):
            parts.append(f"Travelers: {collected_info['travelers']} people")
        
        if collected_info.get('budget'):
            parts.append(f"Budget: ₹{collected_info['budget']:,}")
        
        if collected_info.get('preferences'):
            parts.append(f"Preferences: {', '.join(collected_info['preferences'])}")
        
        if parts:
            return "So far I have: " + " | ".join(parts)
        else:
            return "Let's plan your trip!"
    
    def _generate_confirmation_message(self, collected_info: Dict[str, Any]) -> str:
        """
        Generate a confirmation message with all collected information
        
        Args:
            collected_info: All collected information
            
        Returns:
            Confirmation message
        """
        msg = "Perfect! I have all the information I need:\n\n"
        msg += f"📍 Destination: {collected_info['destination']}\n"
        msg += f"📅 Duration: {collected_info['duration']} days\n"
        msg += f"👥 Travelers: {collected_info['travelers']} people\n"
        msg += f"💰 Budget: ₹{collected_info['budget']:,}\n"
        msg += f"🎯 Preferences: {', '.join(collected_info['preferences'])}\n\n"
        msg += "Let me create a personalized itinerary for you!"
        
        return msg
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current session information
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session dict or None
        """
        return self.sessions.get(session_id)
    
    def clear_session(self, session_id: str):
        """
        Clear a session
        
        Args:
            session_id: Session identifier
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Cleared session: {session_id}")
    
    def is_ready_to_generate(self, session_id: str) -> bool:
        """
        Check if session has all required information
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if ready to generate itinerary
        """
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        return session['state'] == DialogState.READY_TO_GENERATE


# Create global instance
dialog_manager = DialogManager()
