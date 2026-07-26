import requests
import json

URL = "https://script.google.com/macros/s/AKfycbxBCLs4Coc-Ow5zV7Vzpev-qJHwIJyP3x6Yom3LbeawZGhK-vOcYamtG3ffa_DVKuDKkA/exec"

print("="*70)
print("🔍 STICKER DATA DIAGNOSTIC TOOL")
print("="*70)

# Read Stickers sheet
print("\n[1] Reading Stickers sheet...")
response = requests.get(URL, params={"sheet": "Stickers"})
print(f"Status: {response.status_code}")

if response.status_code == 200:
    stickers = response.json()
    print(f"Found {len(stickers)} stickers")
    
    if stickers:
        print("\n📋 First sticker data:")
        print(json.dumps(stickers[0], indent=2))
        
        print("\n📋 All column names in first sticker:")
        for key, value in stickers[0].items():
            print(f"  - '{key}': {value}")
        
        # Check if MemberID exists
        if "MemberID" in stickers[0]:
            print(f"\n✅ MemberID column exists: {stickers[0]['MemberID']}")
        else:
            print(f"\n❌ MemberID column NOT FOUND!")
            print("Available columns:", list(stickers[0].keys()))
else:
    print(f"Failed: {response.text}")

# Read Members sheet
print("\n" + "="*70)
print("\n[2] Reading Members sheet...")
response = requests.get(URL, params={"sheet": "Members"})
print(f"Status: {response.status_code}")

if response.status_code == 200:
    members = response.json()
    print(f"Found {len(members)} members")
    
    if members:
        print("\n📋 First member data:")
        print(json.dumps(members[0], indent=2))
        
        print("\n📋 All Member IDs:")
        for m in members:
            print(f"  - {m.get('ID')}")

print("\n" + "="*70)
print("📊 DIAGNOSIS:")
print("="*70)
print("If MemberID shows as empty/N/A in stickers,")
print("the column headers in your Google Sheet are in wrong order!")
print("="*70)