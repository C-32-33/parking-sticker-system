import requests

# Your NEW Apps Script URL
url = "https://script.google.com/macros/s/AKfycbxBCLs4Coc-Ow5zV7Vzpev-qJHwIJyP3x6Yom3LbeawZGhK-vOcYamtG3ffa_DVKuDKkA/exec"

print("="*50)
print("1. TESTING GET (Reading Data)")
print("="*50)
response = requests.get(url, params={"sheet": "Members"})
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text[:150]}...")

print("\n" + "="*50)
print("2. TESTING POST (Adding a New Member)")
print("="*50)
add_data = {
    "action": "append",
    "sheet": "Members",
    "data": [
        "C-33",           # Building
        "TEST999",        # ID
        "Script Test",    # Name
        "101",            # Flat No
        "9999999999",     # Mobile
        "script@test.com",# Email
        "Bike",           # Vehicle Type
        "MH04XY9999",     # Vehicle Number
        "Active",         # Status
        "2026-07-15",     # DateAdded
        "12 months",      # Valid Period
        "2027-07-15"      # Valid Till Date
    ]
}

response = requests.post(url, json=add_data)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200 and '"success":true' in response.text:
    print("✅ SUCCESS! Check your Google Sheet for 'Script Test' (ID: TEST999)")
else:
    print("❌ FAILED to add member.")

print("\n" + "="*50)
print("3. TESTING DELETE (Removing the Test Member)")
print("="*50)
delete_data = {
    "action": "delete",
    "sheet": "Members",
    "idColumn": "ID",
    "idValue": "TEST999"
}

response = requests.post(url, json=delete_data)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200 and '"success":true' in response.text:
    print("✅ SUCCESS! 'TEST999' should now be deleted from your Google Sheet.")
else:
    print("❌ FAILED to delete member.")