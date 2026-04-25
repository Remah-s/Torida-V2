import urllib.request
import urllib.error
import json

BASE_URL = "http://localhost:5000"

def test_endpoint(name, url, expected_status=200):
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            status = response.getcode()
            body = response.read().decode('utf-8')
            
            print(f"[{'PASS' if status == expected_status else 'FAIL'}] {name} ({url}): Status {status}")
            if status == expected_status:
                try:
                    data = json.loads(body)
                    print(f"  Response: {json.dumps(data, indent=2)[:200]}...\n")
                except:
                    print(f"  Response: {body[:200]}...\n")
            else:
                print(f"  Error: {body[:200]}\n")
    except urllib.error.HTTPError as e:
        status = e.code
        body = e.read().decode('utf-8')
        print(f"[{'PASS' if status == expected_status else 'FAIL'}] {name} ({url}): Status {status}")
        print(f"  Error Response: {body[:200]}...\n")
    except Exception as e:
        print(f"[ERROR] {name} ({url}): {str(e)}\n")

print("=== TORIDA API Tests ===\n")
test_endpoint("Root (/)", f"{BASE_URL}/")
test_endpoint("Health (/health)", f"{BASE_URL}/health")
test_endpoint("API Info (/api)", f"{BASE_URL}/api")

# Test a non-existent route to verify 404 handler
test_endpoint("Not Found (/not-exists)", f"{BASE_URL}/not-exists", 404)
