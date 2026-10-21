from tests.conftest import login


def test_publish_respond_and_decide(client):
    author = login(client, "a@example.com")
    applicant = login(client, "b@example.com")
    post = client.post("/api/posts", headers=author, json={"type": "startup", "title": "New team", "description": "We are building a useful product.", "looking_for": "Backend engineer"})
    assert post.status_code == 201
    post_id = post.json()["id"]
    response = client.post(f"/api/posts/{post_id}/responses", headers=applicant, json={"message": "I would like to help."})
    assert response.status_code == 201
    response_id = response.json()["id"]
    assert client.post(f"/api/posts/{post_id}/responses", headers=applicant, json={}).status_code == 409
    assert client.patch(f"/api/responses/{response_id}", headers=applicant, json={"status": "accepted"}).status_code == 403
    decided = client.patch(f"/api/responses/{response_id}", headers=author, json={"status": "accepted"})
    assert decided.status_code == 200
    assert decided.json()["status"] == "accepted"


def test_cannot_respond_to_own_post(client):
    author = login(client, "a@example.com")
    post = client.post("/api/posts", headers=author, json={"type": "vacancy", "title": "Need help", "description": "Looking for a teammate for a project.", "looking_for": "Designer"})
    assert client.post(f"/api/posts/{post.json()['id']}/responses", headers=author, json={}).status_code == 400
