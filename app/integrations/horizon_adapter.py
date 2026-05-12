from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class HorizonSourcePayload:
    type: str
    name: str
    url: str
    config: dict[str, Any]


@dataclass(frozen=True)
class HorizonItemPayload:
    external_id: str
    title: str
    url: str
    content: str | None
    author: str | None
    published_at: datetime
    metadata: dict[str, Any]


@dataclass(frozen=True)
class HorizonAnalysisPayload:
    persona_slug: str
    score: float
    summary: str
    why_it_matters: str
    opportunities: list[str]
    risks: list[str]
    tags: list[str]
    model: str


@dataclass(frozen=True)
class HorizonArtifact:
    source: HorizonSourcePayload
    item: HorizonItemPayload
    analysis: HorizonAnalysisPayload


def parse_horizon_artifact(payload: dict[str, Any]) -> HorizonArtifact:
    source = payload["source"]
    item = payload["item"]
    analysis = payload["analysis"]
    return HorizonArtifact(
        source=HorizonSourcePayload(
            type=source["type"],
            name=source["name"],
            url=source["url"],
            config=source.get("config", {}),
        ),
        item=HorizonItemPayload(
            external_id=item["external_id"],
            title=item["title"],
            url=item["url"],
            content=item.get("content"),
            author=item.get("author"),
            published_at=datetime.fromisoformat(item["published_at"]),
            metadata=item.get("metadata", {}),
        ),
        analysis=HorizonAnalysisPayload(
            persona_slug=analysis["persona_slug"],
            score=float(analysis["score"]),
            summary=analysis["summary"],
            why_it_matters=analysis["why_it_matters"],
            opportunities=list(analysis.get("opportunities", [])),
            risks=list(analysis.get("risks", [])),
            tags=list(analysis.get("tags", [])),
            model=analysis["model"],
        ),
    )
