import requests
from io import BytesIO
from PIL import Image

# URL for the API endpoint
base_url = "http://127.0.0.1:8002/api/data/"

# Test data 1
data1 = {
    'custom_id': '6655443322',
    'gmail': 'user@gmail.com',
    'key': 'key_one_111',
    'message': 'Message for Key 1'
}

# Test data 2 (Same ID, different Key)
data2 = {
    'custom_id': '6655443322', # Same ID
    'gmail': 'user@gmail.com',
    'key': 'key_two_222',       # Different Key
    'message': 'Message for Key 2'
}

# Dummy image creation
file = BytesIO()
image = Image.new('RGB', size=(100, 100), color=(0, 0, 155))
image.save(file, 'png')
file.name = 'detail_test.png'
file.seek(0)
files = {'image': file}

# 1. Create Entry 1
print("Creating Entry 1...")
try:
    # Need to reset file pointer for requests
    file.seek(0)
    response = requests.post(base_url, data=data1, files={'image': file})
    print("Entry 1 Status:", response.status_code)
    try:
        print("Entry 1 Response:", response.json())
    except:
        print("Entry 1 Raw Response:", response.text)
except Exception as e:
    print(f"Entry 1 Failed: {e}")

# 2. Create Entry 2 (Same User, New Key)
print("\nCreating Entry 2 (Same ID, New Key)...")
try:
    file.seek(0) # Reset file pointer
    # We don't send image for second one just to vary it
    response = requests.post(base_url, data=data2) 
    print("Entry 2 Status:", response.status_code)
    try:
        print("Entry 2 Response:", response.json())
    except:
        print("Entry 2 Raw Response:", response.text)
except Exception as e:
    print(f"Entry 2 Failed: {e}")


# 3. Retrieve Entry 1 Message
print("\nRetrieving Entry 1 Message...")
url_1 = f"{base_url}{data1['custom_id']}/{data1['key']}/message/"
try:
    response = requests.get(url_1)
    print("Entry 1 Message:", response.json())
except Exception as e:
    print(f"Get 1 Failed: {e}")

# 4. Retrieve Entry 2 Message
print("\nRetrieving Entry 2 Message...")
url_2 = f"{base_url}{data2['custom_id']}/{data2['key']}/message/"
try:
    response = requests.get(url_2)
    print("Entry 2 Message:", response.json())
except Exception as e:
    print(f"Get 2 Failed: {e}")
    
# 5. Verify Invalid Key for this ID
print("\nVerifying Invalid Key...")
url_invalid = f"{base_url}{data1['custom_id']}/wrong_key/message/"
try:
    response = requests.get(url_invalid)
    print("Invalid Key Status:", response.status_code)
except Exception as e:
    print(f"Invalid Key Failed: {e}")
