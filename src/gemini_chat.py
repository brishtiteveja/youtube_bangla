"""
Gemini Chat Module
Handles Q&A and chat interactions with video transcripts using Google Gemini Flash
"""

import google.generativeai as genai
from typing import List, Dict, Optional
from config import Config


class GeminiChatBot:
    """Chatbot for Q&A with video transcripts using Gemini Flash"""

    def __init__(self, api_key: str = None):
        """
        Initialize Gemini chatbot

        Args:
            api_key: Google Gemini API key (defaults to Config.GEMINI_API_KEY)
        """
        self.api_key = api_key or Config.GEMINI_API_KEY

        if not self.api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY in .env")

        # Configure Gemini
        genai.configure(api_key=self.api_key)

        # Use Gemini Flash (fast and efficient)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

        # Chat history
        self.chat = None
        self.transcript_context = None
        self.video_title = None
        self.video_id = None

    def start_chat(self, transcript_text: str, video_title: str = "", video_id: str = ""):
        """
        Start a new chat session with a transcript

        Args:
            transcript_text: Full transcript text
            video_title: Video title for context
            video_id: Video ID for reference
        """
        self.transcript_context = transcript_text
        self.video_title = video_title
        self.video_id = video_id

        # Create system prompt with transcript context
        system_prompt = f"""You are a helpful AI assistant analyzing a YouTube video transcript.

Video Title: {video_title}
Video ID: {video_id}

TRANSCRIPT:
{transcript_context}

Your role:
- Answer questions about the video content based ONLY on the transcript provided
- Provide clear, accurate, and helpful responses
- If asked about something not in the transcript, politely say it's not mentioned
- You can summarize, explain concepts, find specific topics, and answer questions
- Be conversational and friendly
- Support questions in multiple languages (Bangla, English, Hindi)

Ready to answer questions about this video!"""

        # Start chat with context
        self.chat = self.model.start_chat(history=[])

        # Send initial context (won't be shown to user)
        self.chat.send_message(system_prompt)

    def ask(self, question: str) -> Dict[str, any]:
        """
        Ask a question about the transcript

        Args:
            question: User's question

        Returns:
            Dictionary with response and metadata
        """
        if not self.chat:
            return {
                'success': False,
                'error': 'No active chat session. Start a chat first.',
                'response': None
            }

        try:
            response = self.chat.send_message(question)

            return {
                'success': True,
                'response': response.text,
                'question': question,
                'video_title': self.video_title,
                'video_id': self.video_id
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': None
            }

    def get_summary(self) -> Dict[str, any]:
        """
        Get a summary of the video

        Returns:
            Dictionary with summary
        """
        return self.ask(
            "Please provide a comprehensive summary of this video in 3-5 bullet points. "
            "Focus on the main topics and key takeaways."
        )

    def get_key_points(self) -> Dict[str, any]:
        """
        Get key points from the video

        Returns:
            Dictionary with key points
        """
        return self.ask(
            "What are the most important key points discussed in this video? "
            "List them clearly."
        )

    def find_topic(self, topic: str) -> Dict[str, any]:
        """
        Find information about a specific topic in the video

        Args:
            topic: Topic to search for

        Returns:
            Dictionary with information about the topic
        """
        return self.ask(
            f"What does the video say about '{topic}'? "
            f"Please provide relevant quotes and explanation."
        )

    def get_chat_history(self) -> List[Dict]:
        """
        Get the chat history

        Returns:
            List of messages in the conversation
        """
        if not self.chat:
            return []

        history = []
        for message in self.chat.history[1:]:  # Skip system prompt
            history.append({
                'role': message.role,
                'text': message.parts[0].text if message.parts else ''
            })

        return history

    def clear_chat(self):
        """Clear the current chat session"""
        self.chat = None
        self.transcript_context = None
        self.video_title = None
        self.video_id = None


class TranscriptAnalyzer:
    """Higher-level analyzer for transcript analysis without chat"""

    def __init__(self, api_key: str = None):
        """
        Initialize analyzer

        Args:
            api_key: Google Gemini API key
        """
        self.api_key = api_key or Config.GEMINI_API_KEY

        if not self.api_key:
            raise ValueError("Gemini API key is required")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def analyze_transcript(
        self,
        transcript_text: str,
        video_title: str = "",
        analysis_type: str = "summary"
    ) -> Dict[str, any]:
        """
        Analyze transcript without maintaining chat state

        Args:
            transcript_text: Full transcript
            video_title: Video title
            analysis_type: Type of analysis ('summary', 'key_points', 'topics', 'sentiment')

        Returns:
            Analysis results
        """
        prompts = {
            'summary': (
                f"Summarize this video transcript in 3-5 clear bullet points:\n\n"
                f"Title: {video_title}\n\n{transcript_text}"
            ),
            'key_points': (
                f"Extract the key points from this video:\n\n"
                f"Title: {video_title}\n\n{transcript_text}"
            ),
            'topics': (
                f"List the main topics discussed in this video:\n\n"
                f"Title: {video_title}\n\n{transcript_text}"
            ),
            'sentiment': (
                f"Analyze the sentiment and tone of this video:\n\n"
                f"Title: {video_title}\n\n{transcript_text}"
            )
        }

        prompt = prompts.get(analysis_type, prompts['summary'])

        try:
            response = self.model.generate_content(prompt)

            return {
                'success': True,
                'analysis': response.text,
                'type': analysis_type,
                'video_title': video_title
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'analysis': None
            }