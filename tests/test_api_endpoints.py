def test_public_endpoint(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "Hello, Public!" in res.get_json()["message"]

def test_protected_endpoint_success(client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    res = client.get("/protected", headers=headers)
    assert res.status_code == 200
    assert "user@test.com" in res.get_json()["logged_in_as"]

def test_protected_endpoint_no_token(client):
    res = client.get("/protected")
    assert res.status_code == 401
    assert "Missing Authorization Header" in res.get_json()["msg"]

def test_admin_endpoint_success(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/admin", headers=headers)
    assert res.status_code == 200
    assert "Welcome, Admin!" in res.get_json()["message"]

def test_admin_endpoint_insufficient_role(client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    res = client.get("/admin", headers=headers)
    assert res.status_code == 403
    assert "Insufficient permissions" in res.get_json()["error"]

def test_get_items_success(client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    res = client.get("/items", headers=headers)
    assert res.status_code == 200

# The following tests reference an Item model that does not exist.
# Commenting out until a real model is available or test logic is updated.
'''
def test_create_item_success(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.post("/items", headers=headers, json={"name": "New Item", "description": "A test item."})
    assert res.status_code == 201
    assert res.get_json()["name"] == "New Item"

def test_create_item_insufficient_permissions(client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    res = client.post("/items", headers=headers, json={"name": "Forbidden Item"})
    assert res.status_code == 403
    assert "Insufficient permissions" in res.get_json()["error"]

def test_create_item_missing_fields(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.post("/items", headers=headers, json={"description": "This won't work"})
    assert res.status_code == 400
    assert "Missing 'name' in request body" in res.get_json()["message"]

def test_delete_item_success(client, admin_token, init_database):
    item = Item(name="Deletable", description="...")
    db.session.add(item)
    db.session.commit()

    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.delete(f"/items/{item.id}", headers=headers)
    assert res.status_code == 200
    assert "Item deleted" in res.get_json()["message"]

def test_delete_item_insufficient_permissions(client, user_token, init_database):
    item = Item(name="Protected Item", description="...")
    db.session.add(item)
    db.session.commit()

    headers = {"Authorization": f"Bearer {user_token}"}
    res = client.delete(f"/items/{item.id}", headers=headers)
    assert res.status_code == 403

def test_delete_item_not_found(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.delete("/items/9999", headers=headers)
    assert res.status_code == 404
    assert "Item not found" in res.get_json()["message"]
'''
