from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class TicketCategory(str, Enum):
    BILLING = "billing"
    TECHNICAL = "technical"
    ACCOUNT = "account"
    REFUND = "refund"
    SUBSCRIPTION = "subscription"
    SECURITY = "security"
    OTHER = "other"

class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SuggestedAgent(str, Enum):
    BILLING = "billing_agent"
    TECHNICAL = "technical_agent"
    ACCOUNT = "account_agent"
    SECURITY = "security_agent"
    HUMAN = "human_support"

class TicketResult(BaseModel):
    """
    Structured outcome of ticket classification process.
    Validated by Pydantic to ensure all fields strictly conform to specified schemas.
    """
    category: TicketCategory = Field(
        description="The primary domain category this support ticket belongs to."
    )
    secondary_category: Optional[TicketCategory] = Field(
        None,
        description="An optional secondary domain category if the ticket expresses multiple intents (e.g. payment failed and login issues)."
    )
    priority: TicketPriority = Field(
        description="The priority level of the ticket, derived from the urgency and potential impact."
    )
    suggested_agent: SuggestedAgent = Field(
        description="The recommended specialized support agent or desk for handling this ticket."
    )
    confidence: float = Field(
        description="Confidence score for this classification, from 0.0 to 1.0.",
        ge=0.0,
        le=1.0
    )
    summary: str = Field(
        description="A concise, one-sentence summary of the user's issue, cleaning up formatting and fluff."
    )
    reasoning: str = Field(
        description="Brief step-by-step logic explaining why this classification was chosen."
    )
    requires_human_review: bool = Field(
        description="Flag indicating if this ticket requires direct manual review, e.g., if priority is critical or confidence is low."
    )
