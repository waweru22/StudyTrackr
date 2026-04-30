import requests
import sys

def check_url(url, name):
    print(f"Checking {name} at {url}...")
    try:
        response = requests.get(url, timeout=5)
        print(f"PASS: {name} is reachable. Status Code: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print(f"FAIL: {name} is NOT reachable. Connection refused.")
        return False
    except Exception as e:
        print(f"FAIL: {name} error: {e}")
        return False

def check_backend_api():
    url = "http://localhost:5000/auth/onboard"
    print(f"\nTesting API Endpoint: {url} (POST)...")
    try:
        # sending empty json to trigger validation error
        response = requests.post(url, json={}, timeout=5) 
        if response.status_code in [400, 422, 200, 201]:
            print(f"PASS: Endpoint is active. Response: {response.status_code} (Expected behavior for empty payload)")
            print(f"Response Body: {response.text}")
        elif response.status_code == 404:
            print("FAIL: Endpoint not found (404).")
        elif response.status_code == 500:
            print("FAIL: Internal Server Error (500).")
        else:
            print(f"WARNING: Unexpected status code: {response.status_code}")
    except Exception as e:
        print(f"FAIL: API Request failed: {e}")

if __name__ == "__main__":
    print("=== CONNECTIVITY AUDIT ===\n")
    
    backend_up = check_url("http://localhost:5000/", "Backend Server")
    # Backend might return 404 for root, but connection means it's up.
    # Actually requests.get returns a response object even if 404, check_url prints the code.
    
    frontend_up = check_url("http://localhost:5173/", "Frontend Vite Server")
    
    if backend_up:
        check_backend_api()
        
    print("\n=== AUDIT COMPLETE ===")
