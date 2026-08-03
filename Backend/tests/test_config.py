from Backend.app.core.config import Settings, get_settings


def test_settings_defaults_are_usable_for_local_development():
    settings = Settings()

    assert settings.app_name
    assert settings.api_version == "v1"
    assert settings.api_prefix == "/api/v1"
    assert settings.database_url
    assert settings.ml_saved_models_dir.exists()


def test_get_settings_is_cached():
    assert get_settings() is get_settings()


def test_settings_reads_environment_overrides(monkeypatch):
    monkeypatch.setenv("APP_NAME", "Overridden Name")
    monkeypatch.setenv("ENVIRONMENT", "production")

    settings = Settings()

    assert settings.app_name == "Overridden Name"
    assert settings.environment == "production"
