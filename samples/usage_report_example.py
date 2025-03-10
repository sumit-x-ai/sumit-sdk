import time

from sumit_sdk.api import APIClient  # API core client
from sumit_sdk.users import UsersAPI
import json

# initialize API
api = APIClient("api-sa.json")  # create client

users = UsersAPI(api)

print("usage report for the last 3 months:")
ret = users.usage_report(3)
print(json.dumps(ret['report'], indent=2))

print("rate limit:")
ret = users.get_quota()
print(ret['rate_limit'])