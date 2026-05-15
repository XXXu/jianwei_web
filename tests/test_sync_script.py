from pathlib import Path


def test_sync_horizon_script_contains_automation_safeguards() -> None:
    script = Path("bin/sync_horizon.sh").read_text(encoding="utf-8")

    assert "flock -n" in script
    assert "sync_horizon.log" in script
    assert "HORIZON_DIR" in script
    assert "JIANWEI_WEB_DIR" in script
    assert "PERSONA_SLUG" in script
    assert "-m src.integrations.jianwei" in script
    assert "./bin/import_artifacts.sh" in script
