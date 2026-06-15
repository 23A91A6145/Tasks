from pydantic import BaseModel


class EmailVersion(BaseModel):
    subject: str
    body: str


class EmailOutput(BaseModel):
    tone: str

    email_a: EmailVersion
    email_b: EmailVersion
    email_c: EmailVersion