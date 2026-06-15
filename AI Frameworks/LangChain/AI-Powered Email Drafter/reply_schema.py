from pydantic import BaseModel


class ReplyOutput(BaseModel):

    subject: str

    tone: str

    reply: str