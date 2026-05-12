from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import Persona


DEFAULT_PERSONAS = [
    {
        "slug": "indie-maker",
        "name": "独立开发者 / AI 产品创业者",
        "description": "寻找适合小团队或个人执行的 AI 产品机会。",
        "prompt_profile": "关注 MVP、获客渠道、收费点、竞品、独立开发可行性。",
    },
    {
        "slug": "cross-border-operator",
        "name": "跨境卖家 / 出海产品人",
        "description": "关注海外增长工具、平台变化、营销自动化和出海机会。",
        "prompt_profile": "关注海外需求、平台政策、广告营销、Shopify、TikTok 和工具机会。",
    },
    {
        "slug": "funding-observer",
        "name": "投资 / 融资观察者",
        "description": "关注 AI 赛道融资、公司动态、趋势信号和竞争格局。",
        "prompt_profile": "关注融资金额、投资机构、赛道变化、公司壁垒和风险。",
    },
    {
        "slug": "enterprise-ai-lead",
        "name": "企业 AI 应用负责人",
        "description": "关注企业 AI 落地、效率工具、安全合规和采购风险。",
        "prompt_profile": "关注落地场景、团队效率、合规风险、安全风险和采购判断。",
    },
]


def seed_default_personas(session: Session) -> None:
    for item in DEFAULT_PERSONAS:
        existing = session.query(Persona).filter(Persona.slug == item["slug"]).one_or_none()
        if existing:
            continue
        session.add(Persona(**item))
    session.commit()


def main() -> None:
    with SessionLocal() as session:
        seed_default_personas(session)


if __name__ == "__main__":
    main()
