class TestOpenAPISpec:
    def test_openapi_json_accessible(self, client):
        response = client.get("/docs/openapi.json")
        assert response.status_code == 200

    def test_openapi_spec_contains_health_path(self, client):
        response = client.get("/docs/openapi.json")
        spec = response.get_json()
        assert "/health/" in spec["paths"]

    def test_openapi_spec_health_has_get(self, client):
        response = client.get("/docs/openapi.json")
        spec = response.get_json()
        assert "get" in spec["paths"]["/health/"]
