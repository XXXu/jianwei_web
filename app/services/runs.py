from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models import Persona, Run


def create_run(
    session: Session,
    *,
    job_type: str,
    persona: Persona | None,
    status: str,
    fetched_count: int,
    analyzed_count: int,
    error_message: str | None = None,
) -> Run:
    run = Run(
        job_type=job_type,
        persona=persona,
        status=status,
        fetched_count=fetched_count,
        analyzed_count=analyzed_count,
        error_message=error_message,
        finished_at=datetime.now(UTC),
    )
    session.add(run)
    session.commit()
    session.refresh(run)
    return run
