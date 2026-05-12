from app.integrations.horizon_adapter import HorizonArtifact, parse_horizon_artifact


def test_parse_horizon_artifact() -> None:
    payload = {
        "source": {
            "type": "rss",
            "name": "Example Feed",
            "url": "https://example.com/feed.xml",
        },
        "item": {
            "external_id": "rss:demo-1",
            "title": "AI Video Agent Released",
            "url": "https://example.com/ai-video-agent",
            "content": "A new AI video agent was released.",
            "author": "Example",
            "published_at": "2026-05-12T08:00:00+00:00",
            "metadata": {"source_score": 88},
        },
        "analysis": {
            "persona_slug": "indie-maker",
            "score": 8.8,
            "summary": "AI 视频 Agent 是一个值得关注的产品信号。",
            "why_it_matters": "视频自动化工具仍在升温。",
            "opportunities": ["面向房产中介做短视频自动生成器"],
            "risks": ["版权和素材授权需要谨慎"],
            "tags": ["video", "agent"],
            "model": "deepseek-test",
        },
    }

    artifact = parse_horizon_artifact(payload)

    assert isinstance(artifact, HorizonArtifact)
    assert artifact.source.name == "Example Feed"
    assert artifact.item.external_id == "rss:demo-1"
    assert artifact.analysis.persona_slug == "indie-maker"
    assert artifact.analysis.opportunities == ["面向房产中介做短视频自动生成器"]
