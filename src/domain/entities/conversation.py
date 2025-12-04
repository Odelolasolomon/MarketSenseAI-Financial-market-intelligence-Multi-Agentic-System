"""
Conversation Entity - Stores user conversations and context for memory
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum


class MessageRole(str, Enum):
    """Message sender role"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class ConversationMessage:
    """Individual message in a conversation"""
    
    id: str
    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class ConversationContext:
    """Maintains conversation state and context"""
    
    conversation_id: str
    user_id: str
    asset_symbol: str
    messages: List[ConversationMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    # Context tracking
    previous_outlook: Optional[str] = None  # Last analysis outlook
    previous_confidence: Optional[float] = None
    previous_action: Optional[str] = None
    
    # Session metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, role: MessageRole, content: str, metadata: Optional[Dict] = None) -> ConversationMessage:
        """Add a message to conversation"""
        import uuid
        msg = ConversationMessage(
            id=str(uuid.uuid4()),
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(msg)
        self.last_updated = datetime.now()
        return msg
    
    def get_recent_messages(self, limit: int = 10) -> List[ConversationMessage]:
        """Get most recent messages"""
        return self.messages[-limit:]
    
    def get_context_summary(self) -> str:
        """Generate summary of conversation context for agent injection"""
        if not self.messages:
            return ""
        
        recent = self.get_recent_messages(5)
        summary_parts = [
            f"Previous analysis on {self.asset_symbol}:",
            f"  - Last outlook: {self.previous_outlook}",
            f"  - Confidence: {self.previous_confidence}",
            f"  - Action: {self.previous_action}",
            "\nRecent conversation:",
        ]
        
        for msg in recent:
            role = "You" if msg.role == MessageRole.USER else "Assistant"
            # Truncate long messages
            content = msg.content[:200] + "..." if len(msg.content) > 200 else msg.content
            summary_parts.append(f"  {role}: {content}")
        
        return "\n".join(summary_parts)
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "conversation_id": self.conversation_id,
            "user_id": self.user_id,
            "asset_symbol": self.asset_symbol,
            "messages": [msg.to_dict() for msg in self.messages],
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "previous_outlook": self.previous_outlook,
            "previous_confidence": self.previous_confidence,
            "previous_action": self.previous_action,
            "metadata": self.metadata
        }


@dataclass
class ConversationSession:
    """User session for conversation tracking"""
    
    session_id: str
    user_id: str
    conversations: Dict[str, ConversationContext] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    
    def get_or_create_conversation(
        self, 
        conversation_id: str, 
        asset_symbol: str
    ) -> ConversationContext:
        """Get existing conversation or create new one"""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = ConversationContext(
                conversation_id=conversation_id,
                user_id=self.user_id,
                asset_symbol=asset_symbol
            )
        self.last_accessed = datetime.now()
        return self.conversations[conversation_id]
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "conversations": {
                cid: ctx.to_dict() 
                for cid, ctx in self.conversations.items()
            },
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat()
        }
