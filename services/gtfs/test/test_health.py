class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        response = client.get("/health/")
        assert response.status_code == 200

    def test_health_returns_json(self, client):
        response = client.get("/health/")
        assert response.content_type == "application/json"

    def test_health_status_is_ok(self, client):
        response = client.get("/health/")
        data = response.get_json()
        assert data["status"] == "ok"

    def test_health_response_has_status_field(self, client):
        response = client.get("/health/")
        data = response.get_json()
        assert "status" in data

    def test_health_post_not_allowed(self, client):
        response = client.post("/health/")
        assert response.status_code == 405

    def test_health_put_not_allowed(self, client):
        response = client.put("/health/")
        assert response.status_code == 405

    def test_health_delete_not_allowed(self, client):
        response = client.delete("/health/")
        assert response.status_code == 405
