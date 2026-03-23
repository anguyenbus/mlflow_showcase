"""Conversation memory management utilities.

Provides utilities for managing conversation state and history
with LangChain chat history components for multi-turn conversations.
"""

from beartype import beartype
from langchain_core.chat_history import InMemoryChatMessageHistory, BaseChatMessageHistory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from typing import List, Dict, Any, Optional


@beartype
class ConversationManager:
    """Manager for multi-turn conversations with tracing.

    Wraps LangChain's InMemoryChatMessageHistory to provide a clean
    interface for managing conversation history in MLflow tracing examples.

    Attributes:
        history: LangChain InMemoryChatMessageHistory for storing messages
        max_history: Maximum number of message pairs to store (for tracking)

    Example:
        >>> manager = ConversationManager(max_history=5)
        >>> manager.add_user_message("Hello!")
        >>> manager.add_ai_message("Hi there! How can I help?")
        >>> history = manager.get_conversation_history()
        >>> len(history)
        2
    """

    __slots__ = ("history", "max_history")

    def __init__(self, max_history: int = 5) -> None:
        """Initialize conversation manager.

        Args:
            max_history: Maximum message pairs to store (default: 5).
                Note: This is for tracking purposes only. The history
                grows until manually cleared or trimmed.
        """
        self.history = InMemoryChatMessageHistory()
        self.max_history = max_history

    def add_user_message(self, message: str) -> None:
        """Add user message to conversation history.

        Args:
            message: User message text to add to history
        """
        self.history.add_message(HumanMessage(content=message))

    def add_ai_message(self, message: str) -> None:
        """Add AI message to conversation history.

        Args:
            message: AI message text to add to history
        """
        self.history.add_message(AIMessage(content=message))

    def get_conversation_history(self) -> List[BaseMessage]:
        """Get full conversation history.

        Returns:
            List of messages in chronological order (oldest to newest).
            Each message is either a HumanMessage or AIMessage.
        """
        return self.history.messages

    def get_history_summary(self) -> Dict[str, int]:
        """Get conversation statistics.

        Useful for logging metrics to MLflow.

        Returns:
            Dictionary with message counts:
            - total_messages: Total number of messages in history
            - user_messages: Number of user messages
            - ai_messages: Number of AI responses
        """
        messages = self.history.messages
        return {
            "total_messages": len(messages),
            "user_messages": sum(1 for m in messages if isinstance(m, HumanMessage)),
            "ai_messages": sum(1 for m in messages if isinstance(m, AIMessage))
        }

    def clear_history(self) -> None:
        """Clear conversation history.

        Useful for starting a fresh conversation or testing.
        """
        self.history.clear()

    def trim_history(self, keep_last: int) -> None:
        """Trim conversation history to keep only the last N messages.

        Args:
            keep_last: Number of most recent messages to keep
        """
        messages = self.history.messages
        if len(messages) > keep_last:
            # Clear and re-add only the last N messages
            self.history.clear()
            for msg in messages[-keep_last:]:
                self.history.add_message(msg)
