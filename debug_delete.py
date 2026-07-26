import requests
import json

# Your Apps Script URL
URL = "https://script.google.com/macros/s/AKfycbxBCLs4Coc-Ow5zV7Vzpev-qJHwIJyP3x6Yom3LbeawZGhK-vOcYamtG3ffa_DVKuDKkA/exec"

print("="*70)
print("🔍 DELETION DEBUGGING TOOL")
print("="*70)

# TEST 1: Check if we can read data
print("\n[TEST 1] Reading Members from Google Sheet...")
print("-" * 70)
response = requests.get(URL, params={"sheet": "Members"})
print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    members = response.json()
    print(f"✅ Found {len(members)} members")
    
    if members:
        # Show first member's details
        print("\nFirst member details:")
        print(json.dumps(members[0], indent=2))
        
        # Check what columns exist
        print("\n📋 Available columns in first member:")
        for key in members[0].keys():
            print(f"  - '{key}': {members[0][key]}")
        
        # Get the ID to test deletion
        test_member_id = members[0].get("ID")
        print(f"\n Using Member ID for deletion test: '{test_member_id}'")
    else:
        print("❌ No members found to test deletion")
        test_member_id = None
else:
    print(f"❌ Failed to read members: {response.text}")
    test_member_id = None

# TEST 2: Test DELETE operation
if test_member_id:
    print("\n[TEST 2] Attempting to DELETE member...")
    print("-" * 70)
    
    delete_payload = {
        "action": "delete",
        "sheet": "Members",
        "idColumn": "ID",
        "idValue": test_member_id
    }
    
    print(f"Sending payload:")
    print(json.dumps(delete_payload, indent=2))
    
    response = requests.post(URL, json=delete_payload)
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Text: {response.text}")
    
    try:
        result = response.json()
        print(f"\nParsed Response:")
        print(json.dumps(result, indent=2))
        
        if result.get("success"):
            print(f"\n✅ SUCCESS! Member '{test_member_id}' deleted!")
            print("👉 CHECK YOUR GOOGLE SHEET NOW to confirm deletion")
        else:
            print(f"\n❌ DELETE FAILED!")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            
            # Try to get more info
            if "not found" in str(result.get('error', '')).lower():
                print("\n💡 TROUBLESHOOTING TIPS:")
                print("   1. The column name 'ID' might not match your sheet")
                print("   2. The value might have extra spaces or different format")
                print("   3. Check if the Apps Script has write permissions")
            
    except Exception as e:
        print(f"\n❌ Failed to parse response: {e}")
        print(f"   Raw response: {response.text}")

# TEST 3: Check Apps Script deployment
print("\n[TEST 3] Checking Apps Script Configuration...")
print("-" * 70)
print("Please verify in Google Apps Script:")
print("  1. Execute as: Me (your email)")
print("  2. Who has access: Anyone (NOT 'Anyone with Google Account')")
print("  3. Deployment is active (not disabled)")
print("  4. Script has permission to edit spreadsheet")

print("\n" + "="*70)
print("📊 DEBUG SUMMARY")
print("="*70)
print("If deletion failed, check:")
print("  ✓ Column name 'ID' exists in your Members sheet (exact spelling)")
print("  ✓ Apps Script deployment settings")
print("  ✓ Apps Script has edit permissions")
print("  ✓ No typos in the URL")
print("="*70)