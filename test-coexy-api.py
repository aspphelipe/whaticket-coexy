import urllib.request, json, sys

api_key = sys.argv[1] if len(sys.argv) > 1 else "crt_pk_94ee020c53d392965c7ab3f161da7e85d3debaabb92decd6f9cc7179f3709297"

url = "https://api.coexy.com.br/functions/v1/api/channels"
data = json.dumps({"name": "test-vps"}).encode()
headers = {"x-api-key": api_key, "Content-Type": "application/json"}

req = urllib.request.Request(url, data, headers)
try:
    r = urllib.request.urlopen(req)
    print("Status:", r.status)
    print("Response:", r.read().decode())
except urllib.error.HTTPError as e:
    print("Error:", e.code)
    print("Response:", e.read().decode())
except Exception as e:
    print("Exception:", str(e))
