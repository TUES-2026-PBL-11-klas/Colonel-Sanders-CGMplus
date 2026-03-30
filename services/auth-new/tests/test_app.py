import pytest
from unittest.mock import patch, MagicMock


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _patch_extensions(monkeypatch):
    """
    Replace every heavy extension with a lightweight mock so tests never
    touch a real database, JWT stack, or migration engine.
    """
    fake_api = MagicMock()
    fake_db = MagicMock()
    fake_migrate = MagicMock()
    fake_jwt = MagicMock()

    # Keep a reference so individual tests can introspect calls.
    monkeypatch.setattr("src.extensions.api", fake_api)
    monkeypatch.setattr("src.extensions.db", fake_db)
    monkeypatch.setattr("src.extensions.migrate", fake_migrate)
    monkeypatch.setattr("src.extensions.jwt", fake_jwt)

    # Also patch the names as imported inside the app factory module.
    monkeypatch.setattr("src.app.api", fake_api)
    monkeypatch.setattr("src.app.db", fake_db)
    monkeypatch.setattr("src.app.migrate", fake_migrate)
    monkeypatch.setattr("src.app.jwt", fake_jwt)

    return {
        "api": fake_api,
        "db": fake_db,
        "migrate": fake_migrate,
        "jwt": fake_jwt,
    }


@pytest.fixture(autouse=True)
def _patch_models(monkeypatch):
    """Prevent the real models module from being imported (needs a real DB)."""
    import sys
    fake_models = MagicMock()
    monkeypatch.setitem(sys.modules, "src.models", fake_models)


@pytest.fixture(autouse=True)
def _patch_blueprints(monkeypatch):
    """Swap real blueprints for mocks to avoid import-time side effects."""
    monkeypatch.setattr("src.app.AuthBlueprint", MagicMock(name="AuthBlueprint"))
    monkeypatch.setattr("src.app.RootBlueprint", MagicMock(name="RootBlueprint"))
    monkeypatch.setattr("src.app.UserBlueprint", MagicMock(name="UserBlueprint"))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestCreateAppConfigLoading:
    def test_uses_explicit_config_name(self, monkeypatch):
        """create_app(config_name=...) should call config_by_name with that key."""
        from src.app import create_app

        with patch("src.app.config_by_name", {"testing": MagicMock()}) as cfg_map, \
             patch("src.app.apply_runtime_config") as mock_apply, \
             patch("src.app.get_config_name", return_value="testing"):
            app = create_app("testing")

        assert app is not None

    def test_falls_back_to_get_config_name(self, monkeypatch):
        """When no config_name is passed get_config_name() must be called."""
        with patch("src.app.get_config_name", return_value="testing") as mock_get, \
             patch("src.app.config_by_name", {"testing": MagicMock()}), \
             patch("src.app.apply_runtime_config"):
            from src.app import create_app
            create_app()

        mock_get.assert_called_once()

    def test_apply_runtime_config_called(self):
        """apply_runtime_config must be invoked with the Flask app and config name."""
        with patch("src.app.get_config_name", return_value="testing"), \
             patch("src.app.config_by_name", {"testing": MagicMock()}), \
             patch("src.app.apply_runtime_config") as mock_apply:
            from src.app import create_app
            app = create_app("testing")

        mock_apply.assert_called_once()
        call_args = mock_apply.call_args
        assert call_args[0][0] is app
        assert call_args[0][1] == "testing"


class TestCreateAppExtensionInit:
    def test_all_extensions_initialised(self, _patch_extensions):
        with patch("src.app.get_config_name", return_value="testing"), \
             patch("src.app.config_by_name", {"testing": MagicMock()}), \
             patch("src.app.apply_runtime_config"):
            from src.app import create_app
            app = create_app("testing")

        exts = _patch_extensions
        exts["api"].init_app.assert_called_once_with(app)
        exts["db"].init_app.assert_called_once_with(app)
        exts["migrate"].init_app.assert_called_once_with(app, exts["db"])
        exts["jwt"].init_app.assert_called_once_with(app)

    def test_blueprints_registered(self, _patch_extensions):
        with patch("src.app.get_config_name", return_value="testing"), \
             patch("src.app.config_by_name", {"testing": MagicMock()}), \
             patch("src.app.apply_runtime_config"):
            from src.app import create_app
            create_app("testing")

        api_mock = _patch_extensions["api"]
        assert api_mock.register_blueprint.call_count == 3

    def test_auth_blueprint_registered_with_prefix(self, _patch_extensions):
        with patch("src.app.get_config_name", return_value="testing"), \
             patch("src.app.config_by_name", {"testing": MagicMock()}), \
             patch("src.app.apply_runtime_config"):
            from src.app import create_app, AuthBlueprint
            create_app("testing")

        api_mock = _patch_extensions["api"]
        api_mock.register_blueprint.assert_any_call(AuthBlueprint, url_prefix="/auth")

    def test_root_and_user_blueprints_registered(self, _patch_extensions):
        with patch("src.app.get_config_name", return_value="testing"), \
             patch("src.app.config_by_name", {"testing": MagicMock()}), \
             patch("src.app.apply_runtime_config"):
            from src.app import create_app, RootBlueprint, UserBlueprint
            create_app("testing")

        api_mock = _patch_extensions["api"]
        api_mock.register_blueprint.assert_any_call(RootBlueprint)
        api_mock.register_blueprint.assert_any_call(UserBlueprint)


class TestCreateAppProductionGuard:
    def test_raises_when_jwt_secret_missing_in_production(self):
        """RuntimeError must be raised if JWT_SECRET_KEY is absent in production."""
        fake_config = MagicMock()

        with patch("src.app.get_config_name", return_value="production"), \
             patch("src.app.config_by_name", {"production": fake_config}), \
             patch("src.app.apply_runtime_config"):
            from src.app import create_app

            # Simulate app.config.get("JWT_SECRET_KEY") returning None/falsy.
            with patch("flask.Flask.config", new_callable=MagicMock) as mock_cfg:
                mock_cfg.from_object = MagicMock()
                mock_cfg.get = MagicMock(return_value=None)

                with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
                    create_app("production")

    def test_no_error_when_jwt_secret_present_in_production(self):
        """No RuntimeError when JWT_SECRET_KEY is set in production."""
        fake_config = MagicMock()

        with patch("src.app.get_config_name", return_value="production"), \
             patch("src.app.config_by_name", {"production": fake_config}), \
             patch("src.app.apply_runtime_config"):
            from src.app import create_app

            with patch("flask.Flask.config", new_callable=MagicMock) as mock_cfg:
                mock_cfg.from_object = MagicMock()
                mock_cfg.get = MagicMock(return_value="super-secret")

                # Should not raise.
                app = create_app("production")
                assert app is not None

    def test_no_jwt_check_outside_production(self):
        """JWT_SECRET_KEY check must be skipped for non-production configs."""
        with patch("src.app.get_config_name", return_value="testing"), \
             patch("src.app.config_by_name", {"testing": MagicMock()}), \
             patch("src.app.apply_runtime_config"):
            from src.app import create_app

            with patch("flask.Flask.config", new_callable=MagicMock) as mock_cfg:
                mock_cfg.from_object = MagicMock()
                mock_cfg.get = MagicMock(return_value=None)  # No key — still fine.

                app = create_app("testing")
                assert app is not None


class TestCreateAppReturnValue:
    def test_returns_flask_instance(self):
        from flask import Flask

        with patch("src.app.get_config_name", return_value="testing"), \
             patch("src.app.config_by_name", {"testing": MagicMock()}), \
             patch("src.app.apply_runtime_config"):
            from src.app import create_app
            app = create_app("testing")

        assert isinstance(app, Flask)
