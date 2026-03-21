from src.app import create_app


class TestAppFactory:
    def test_create_app_returns_flask_instance(self):
        from flask import Flask
        app = create_app()
        assert isinstance(app, Flask)

    def test_app_is_in_testing_mode(self, app):
        assert app.config["TESTING"] is True

    def test_api_title_config(self, app):
        assert app.config["API_TITLE"] == "My Microservice"

    def test_api_version_config(self, app):
        assert app.config["API_VERSION"] == "v1"

    def test_openapi_version_config(self, app):
        assert app.config["OPENAPI_VERSION"] == "3.0.3"

    def test_health_blueprint_registered(self, app):
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        assert any("/health/" in rule for rule in rules)
