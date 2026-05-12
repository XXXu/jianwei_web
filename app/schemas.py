from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field


class PersonaOut(BaseModel):
    id: int
    slug: str
    name: str
    description: str


class PersonaListOut(BaseModel):
    items: list[PersonaOut]


class IntelligenceItemOut(BaseModel):
    id: int
    title: str
    url: str
    score: float
    summary: str
    why_it_matters: str
    opportunities: list[str]
    risks: list[str]
    tags: list[str]
    published_at: datetime


class PersonaFeedOut(BaseModel):
    persona: PersonaOut
    items: list[IntelligenceItemOut]


class SubscriptionIn(BaseModel):
    email: EmailStr
    persona_slug: str
    keywords: list[str] = Field(default_factory=list)


class SubscriptionOut(BaseModel):
    email: EmailStr
    persona_slug: str
    status: str


class BriefingOut(BaseModel):
    id: int
    persona_slug: str
    persona_name: str
    date: date
    title: str
    summary: str


class BriefingListOut(BaseModel):
    items: list[BriefingOut]
