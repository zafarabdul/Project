import requests
import time
from io import BytesIO
from PIL import Image

BASE_URL = "http://127.0.0.1:8002/api/data"
CUSTOM_ID = "TESTUSER01"  # Must be 10 chars
GMAIL = "user01@test.com"
KEY = "KEY000000000001" # Max 15 chars
MESSAGE_INIT = "Initial Message"
MESSAGE_UPDATED = "Updated Message contents"

def create_dummy_image():
    file = BytesIO()
    image = Image.new('RGB', size=(50, 50), color=(100, 150, 200))
    image.save(file, 'png')
    file.name = 'test_image.png'
    file.seek(0)
    return file

def run_tests():
    print(f"--- Starting API Tests on {BASE_URL} ---\n")

    # 1. Test Registration Endpoint
    print(f"1. Testing Registration: POST /register/{CUSTOM_ID}/{GMAIL}/")
    reg_url = f"{BASE_URL}/register/{CUSTOM_ID}/{GMAIL}/"
    try:
        resp = requests.post(reg_url)
        print(f"   Status: {resp.status_code}")
        print(f"   Response: {resp.json()}")
        if resp.status_code not in [200, 201]:
            print("   [FAILED] Registration failed")
    except Exception as e:
        print(f"   [ERROR] {e}")

    # 2. Test Create Data Entry (Standard Path)
    print(f"\n2. Testing Create Data: POST /")
    create_data = {
        'custom_id': CUSTOM_ID,
        'gmail': GMAIL,
        'key': KEY,
        'message': MESSAGE_INIT
    }
    try:
        # We assume this endpoint is at /api/data/ (BASE_URL + "/")
        resp = requests.post(f"{BASE_URL}/", data=create_data)
        print(f"   Status: {resp.status_code}")
        print(f"   Response: {resp.json()}")
    except Exception as e:
        print(f"   [ERROR] {e}")

    # 3. Test GET Message
    print(f"\n3. Testing Get Message: GET /{CUSTOM_ID}/{KEY}/message/")
    msg_url = f"{BASE_URL}/{CUSTOM_ID}/{KEY}/message/"
    try:
        resp = requests.get(msg_url)
        print(f"   Status: {resp.status_code}")
        print(f"   Response: {resp.json()}")
        if resp.json().get('message') == MESSAGE_INIT:
            print("   [SUCCESS] Message matches")
        else:
            print(f"   [WARNING] Expected '{MESSAGE_INIT}', got '{resp.json().get('message')}'")
    except Exception as e:
        print(f"   [ERROR] {e}")

    # 4. Test Update Message (POST)
    print(f"\n4. Testing Update Message: POST /{CUSTOM_ID}/{KEY}/message/")
    try:
        resp = requests.post(msg_url, data={'message': MESSAGE_UPDATED})
        print(f"   Status: {resp.status_code}")
        print(f"   Response: {resp.json()}")
    except Exception as e:
        print(f"   [ERROR] {e}")

    # 5. Verify Update
    print(f"\n5. Verifying Message Update...")
    try:
        resp = requests.get(msg_url)
        print(f"   Response: {resp.json()}")
    except Exception as e:
        print(f"   [ERROR] {e}")

    # 6. Test Update Photo (POST)
    print(f"\n6. Testing Update Photo: POST /{CUSTOM_ID}/{KEY}/photo/")
    photo_url = f"{BASE_URL}/{CUSTOM_ID}/{KEY}/photo/"
    try:
        img_file = create_dummy_image()
        files = {'image': img_file}
        resp = requests.post(photo_url, files=files)
        print(f"   Status: {resp.status_code}")
        print(f"   Response: {resp.json()}")
    except Exception as e:
        print(f"   [ERROR] {e}")

    # 7. Test Get Photo
    print(f"\n7. Testing Get Photo: GET /{CUSTOM_ID}/{KEY}/photo/")
    try:
        resp = requests.get(photo_url)
        print(f"   Status: {resp.status_code}")
        print(f"   Response: {resp.json()}")
    except Exception as e:
        print(f"   [ERROR] {e}")

    print("\n--- Test Suite Completed ---")

if __name__ == "__main__":
    run_tests()
