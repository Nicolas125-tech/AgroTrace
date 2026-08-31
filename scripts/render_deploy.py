import urllib.request
import urllib.error
import json
import sys

API_KEY = "rnd_lwBck2zHTYx1WauMSiiXude3bm8F"
HEADERS = {
    "Accept": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

def get_owner_id():
    req = urllib.request.Request("https://api.render.com/v1/owners", headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if data:
                owner = data[0]['owner']
                print(f"Owner found: {owner['name']} ({owner['id']})")
                return owner['id']
    except urllib.error.URLError as e:
        print(f"Failed to fetch owners: {e}")
        if hasattr(e, 'read'):
            print(e.read().decode())
        sys.exit(1)

if __name__ == "__main__":
    get_owner_id()
