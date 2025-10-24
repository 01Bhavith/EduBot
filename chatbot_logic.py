import json
import random
from datetime import datetime
from google import genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EduBot:
    def __init__(self):
        """Initialize the chatbot with college data and Gemini API"""
        # Load college data
        with open('data.json', 'r') as f:
            self.data = json.load(f)
        
        # Initialize Gemini client
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = 'gemini-2.0-flash-exp'
        
        self.user_name = None
        self.conversation_history = []
        
        # System instruction for Gemini
        self.system_instruction = self._create_system_instruction()
    
    def _create_system_instruction(self):
        """Create system instruction with college data context"""
        instruction = """You are EduBot, a friendly and helpful college assistant chatbot for Canara Engineering College. 
Your personality is warm, supportive, and enthusiastic about helping students.

IMPORTANT RULES:
1. Always use the student's name when you know it
2. Use emojis appropriately to make conversations engaging
3. Be concise but informative
4. If asked about information not in the college data, politely say you don't have that information
5. Always prioritize college-specific data over general knowledge
6. Format responses with proper markdown for readability
7. When asked about faculty, you can filter by department (CSE, ISE, CSBS, CSD)
8. When asked about course timings, mention both the time and the faculty member

COLLEGE DATA AVAILABLE:
"""
        
        # Add college info
        if 'college_info' in self.data:
            info = self.data['college_info']
            instruction += f"\n\nCOLLEGE: {info.get('name', 'Canara Engineering College')}\n"
            instruction += f"DEPARTMENT: {info.get('department', 'Computer Science & Engineering')}\n"
            instruction += f"YEAR: {info.get('year', '3rd Year')}, SEMESTER: {info.get('semester', '5th Semester')}\n"
        
        # Add class schedules
        instruction += "\n\n--- CLASS SCHEDULES ---\n"
        for day, schedule in self.data['class_schedules'].items():
            instruction += f"\n{day.capitalize()}:\n{schedule}\n"
        
        # Add course details if available
        if 'course_details' in self.data:
            instruction += "\n\n--- COURSE DETAILS ---\n"
            for course_code, details in self.data['course_details'].items():
                instruction += f"\n{course_code}: {details['name']}\n"
                instruction += f"Faculty: {details['faculty']}\n"
                instruction += f"Credits: {details['credits']}, Type: {details['type']}\n"
        
        # Add faculty information (UPDATED SECTION)
        instruction += "\n\n--- FACULTY DIRECTORY ---\n"
        
        # Handle faculty organized by departments
        if isinstance(self.data['faculty'], dict):
            for dept_code, faculty_list in self.data['faculty'].items():
                dept_name = dept_code.upper()
                instruction += f"\n\n{dept_name} Department:\n"
                for faculty in faculty_list:
                    instruction += f"\n{faculty['name']} - {faculty.get('designation', 'Faculty')}\n"
                    instruction += f"Subject: {faculty['subject']}\n"
                    instruction += f"Email: {faculty.get('email', 'N/A')}, Phone: {faculty.get('phone', 'N/A')}\n"
        else:
            # Fallback for old format (flat list)
            for faculty in self.data['faculty']:
                instruction += f"\n{faculty['name']} - {faculty['department']}\n"
                instruction += f"Subject: {faculty['subject']}\n"
                instruction += f"Email: {faculty['email']}, Phone: {faculty['phone']}\n"
        
        # Add exam timetable
        instruction += "\n\n--- EXAM TIMETABLE ---\n"
        for exam_type, details in self.data['exam_timetable'].items():
            instruction += f"\n{exam_type.replace('_', ' ').title()}: {details['date']}\n"
            for exam in details['exams']:
                instruction += f"  - {exam}\n"
            if 'note' in details:
                instruction += f"Note: {details['note']}\n"
        
        # Add events
        instruction += "\n\n--- UPCOMING EVENTS ---\n"
        for event in self.data['events']:
            instruction += f"\n{event['name']} - {event['date']}\n"
            instruction += f"Description: {event['description']}\n"
        
        # Add motivational quotes
        instruction += "\n\n--- MOTIVATIONAL QUOTES ---\n"
        instruction += "You have access to these motivational quotes. Share one when asked:\n"
        for i, quote in enumerate(self.data['motivational_quotes'], 1):
            instruction += f"{i}. {quote}\n"
        
        instruction += """\n
RESPONSE GUIDELINES:
- For schedules: Show the relevant day's schedule clearly with faculty names and timings
- For faculty: Display contact information in a formatted way. If asked about a specific department, show only that department's faculty
- For exams: Present dates and timings clearly
- For events: Highlight exciting details
- For motivation: Share a quote with encouraging words
- For greetings: Be warm and friendly
- For course queries: Mention faculty name, timing, and day when relevant
- Always end responses by asking if they need anything else
"""
        
        return instruction
    
    def get_response(self, user_input):
        """Generate response using Gemini API with college context"""
        try:
            # Add user message to conversation history
            self.conversation_history.append({
                'role': 'user',
                'parts': [user_input]
            })
            
            # Prepare context with user name if available
            context = self.system_instruction
            if self.user_name:
                context += f"\n\nSTUDENT'S NAME: {self.user_name}\n"
                context += "Remember to use their name in your responses!\n"
            
            # Add current date context
            today = datetime.now().strftime('%A, %B %d, %Y')
            context += f"\nTODAY'S DATE: {today}\n"
            
            # Create the prompt with full context
            full_prompt = f"{context}\n\nUser message: {user_input}"
            
            # Generate response using Gemini
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt
            )
            
            bot_response = response.text
            
            # Add bot response to conversation history
            self.conversation_history.append({
                'role': 'model',
                'parts': [bot_response]
            })
            
            return bot_response
            
        except Exception as e:
            return f"⚠️ Sorry, I encountered an error: {str(e)}\nPlease try again or rephrase your question."
    
    def get_welcome_message(self):
        """Generate personalized welcome message"""
        if self.user_name:
            return f"Welcome back, **{self.user_name}**! 😊 How can I assist you today?"
        return "Hello! 👋 I'm **EduBot**, your Canara Engineering College assistant. What's your name?"
    
    def set_user_name(self, name):
        """Set user name for personalization"""
        self.user_name = name.strip()
        welcome = f"Nice to meet you, **{self.user_name}**! 😊\n\n"
        welcome += "I can help you with:\n\n"
        welcome += "📅 **Class Schedules** - CSE 5th Semester timetables\n"
        welcome += "👨‍🏫 **Faculty Details** - Contact information by department\n"
        welcome += "📝 **Exam Timetable** - Upcoming tests and exams\n"
        welcome += "🎉 **College Events** - Festivals, workshops, and activities\n"
        welcome += "💪 **Motivation** - Inspirational quotes\n"
        welcome += "📚 **Course Information** - Faculty, timings, and credits\n\n"
        welcome += "What would you like to know?"
        return welcome
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        self.user_name = None
