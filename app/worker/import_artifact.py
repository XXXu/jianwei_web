import json
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy.orm import Session

from app.integrations.horizon_adapter import HorizonArtifact, parse_horizon_artifact
from app.models import Analysis, Item, Persona, Source
from app.services.runs import create_run


@dataclass(frozen=True)
class ImportResult:
    fetched_count: int
    analyzed_count: int


def import_artifact_file(session: Session, path: Path) -> ImportResult:
    payload = json.loads(path.read_text(encoding="utf-8"))
    artifact = parse_horizon_artifact(payload)
    persona = _get_persona(session, artifact)
    source = _get_or_create_source(session, artifact)
    item = _get_or_create_item(session, artifact, source)
    _get_or_create_analysis(session, artifact, item, persona)
    create_run(
        session,
        job_type="import_artifact",
        persona=persona,
        status="success",
        fetched_count=1,
        analyzed_count=1,
    )
    return ImportResult(fetched_count=1, analyzed_count=1)


def _get_persona(session: Session, artifact: HorizonArtifact) -> Persona:
    persona = (
        session.query(Persona)
        .filter(Persona.slug == artifact.analysis.persona_slug, Persona.enabled.is_(True))
        .one_or_none()
    )
    if persona is None:
        raise ValueError(f"Persona not found: {artifact.analysis.persona_slug}")
    return persona


def _get_or_create_source(session: Session, artifact: HorizonArtifact) -> Source:
    source = (
        session.query(Source)
        .filter(Source.type == artifact.source.type, Source.url == artifact.source.url)
        .one_or_none()
    )
    if source is None:
        source = Source(
            type=artifact.source.type,
            name=artifact.source.name,
            url=artifact.source.url,
            config=artifact.source.config,
        )
        session.add(source)
        session.flush()
    return source


def _get_or_create_item(session: Session, artifact: HorizonArtifact, source: Source) -> Item:
    item = (
        session.query(Item)
        .filter(Item.source_id == source.id, Item.external_id == artifact.item.external_id)
        .one_or_none()
    )
    if item is None:
        item = Item(
            source=source,
            external_id=artifact.item.external_id,
            title=artifact.item.title,
            url=artifact.item.url,
            content=artifact.item.content,
            author=artifact.item.author,
            published_at=artifact.item.published_at,
            metadata_json=artifact.item.metadata,
        )
        session.add(item)
        session.flush()
    return item


def _get_or_create_analysis(
    session: Session,
    artifact: HorizonArtifact,
    item: Item,
    persona: Persona,
) -> Analysis:
    analysis = (
        session.query(Analysis)
        .filter(Analysis.item_id == item.id, Analysis.persona_id == persona.id)
        .one_or_none()
    )
    if analysis is None:
        analysis = Analysis(
            item=item,
            persona=persona,
            score=artifact.analysis.score,
            summary=artifact.analysis.summary,
            why_it_matters=artifact.analysis.why_it_matters,
            opportunities=artifact.analysis.opportunities,
            risks=artifact.analysis.risks,
            tags=artifact.analysis.tags,
            model=artifact.analysis.model,
        )
        session.add(analysis)
    else:
        analysis.score = artifact.analysis.score
        analysis.summary = artifact.analysis.summary
        analysis.why_it_matters = artifact.analysis.why_it_matters
        analysis.opportunities = artifact.analysis.opportunities
        analysis.risks = artifact.analysis.risks
        analysis.tags = artifact.analysis.tags
        analysis.model = artifact.analysis.model
    session.commit()
    session.refresh(analysis)
    return analysis
