from pydantic import BaseModel, Field
from typing import Optional


class TaskRequest(BaseModel):
    task: str = Field(..., min_length=5, max_length=2000, description="Task to plan and execute")


class ExecuteRequest(BaseModel):
    plan: list[str] = Field(..., min_length=1, max_length=20)


class RunRequest(BaseModel):
    task: str = Field(..., min_length=5, max_length=2000)


class PlanResponse(BaseModel):
    plan: list[str]
    raw: str


class RunResponse(BaseModel):
    job_id: str
    status: str
    message: str


class StatusResponse(BaseModel):
    job_id: str
    task: str
    status: str
    plan: list[str]
    current_step: Optional[str] = None
    steps_completed: int = 0
    steps_total: int = 0
    error: Optional[str] = None
    created_at: str
    updated_at: str


class StepResultModel(BaseModel):
    step: str
    result: str
    status: str
    error: Optional[str] = None


class LogsResponse(BaseModel):
    job_id: str
    results: list[StepResultModel]
