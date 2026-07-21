import threading

from fastapi import APIRouter, HTTPException

from api.schemas import (
    TaskRequest,
    ExecuteRequest,
    RunRequest,
    PlanResponse,
    RunResponse,
    StatusResponse,
    LogsResponse,
    StepResultModel,
)
from state.state import store, JobStatus, StepResult
from planner.planner import create_plan
from planner.parser import parse_plan
from executor.executor import execute_step
from executor.runner import run_plan
from replanner.replanner import replan

router = APIRouter()


@router.post("/plan", response_model=PlanResponse)
def api_plan(req: TaskRequest):
    try:
        raw = create_plan(req.task)
        steps = parse_plan(raw)
        return PlanResponse(plan=steps, raw=raw)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute")
def api_execute(req: ExecuteRequest):
    try:
        results = run_plan(req.plan)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _run_background(job_id: str, task: str):
    try:
        store.update(job_id, status=JobStatus.PLANNING)
        raw = create_plan(task)
        steps = parse_plan(raw)
        store.update(job_id, plan=steps, status=JobStatus.EXECUTING)

        replanned = False

        for i, step in enumerate(steps):
            store.update(job_id, current_step=step)
            try:
                output = execute_step(step)
                store.append_result(
                    job_id, StepResult(step=step, result=output, status="completed")
                )
            except Exception as e:
                store.append_result(
                    job_id, StepResult(step=step, result="", status="failed", error=str(e))
                )
                store.update(job_id, status=JobStatus.REPLANNING)
                try:
                    new_plan = replan("\n".join(steps), step, str(e))
                    new_steps = parse_plan(new_plan)
                    store.update(
                        job_id,
                        plan=steps + ["[REPLANNED] " + s for s in new_steps],
                    )
                    for rstep in new_steps:
                        store.update(job_id, current_step=rstep)
                        try:
                            output = execute_step(rstep)
                            store.append_result(
                                job_id,
                                StepResult(step=rstep, result=output, status="completed"),
                            )
                        except Exception as e2:
                            store.append_result(
                                job_id,
                                StepResult(
                                    step=rstep, result="", status="failed", error=str(e2)
                                ),
                            )
                    replanned = True
                    break
                except Exception:
                    store.append_result(
                        job_id,
                        StepResult(
                            step=f"(replan failed for: {step})",
                            result="",
                            status="failed",
                            error="Replanning itself failed",
                        ),
                    )
                    break

        store.update(job_id, status=JobStatus.COMPLETED, current_step=None)

    except Exception as e:
        store.update(job_id, status=JobStatus.FAILED, error=str(e))


@router.post("/run", response_model=RunResponse)
def api_run(req: RunRequest):
    job = store.create(req.task)
    thread = threading.Thread(
        target=_run_background, args=(job.job_id, req.task), daemon=True
    )
    thread.start()
    return RunResponse(
        job_id=job.job_id,
        status="pending",
        message="Job started. Poll /status/{job_id} for progress.",
    )


@router.get("/status/{job_id}", response_model=StatusResponse)
def api_status(job_id: str):
    job = store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return StatusResponse(
        job_id=job.job_id,
        task=job.task,
        status=job.status.value,
        plan=job.plan,
        current_step=job.current_step,
        steps_completed=len([r for r in job.results if r.status == "completed"]),
        steps_total=len(job.plan),
        error=job.error,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


@router.get("/logs/{job_id}", response_model=LogsResponse)
def api_logs(job_id: str):
    logs = store.logs(job_id)
    if logs is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return LogsResponse(
        job_id=job_id,
        results=[StepResultModel(**log) for log in logs],
    )
