import time
from sumit_sdk.api import APIClient    # API core client
from sumit_sdk.steam_stt import StreamSTT

# initialize API
api = APIClient("api-sa-prod.json", env="dev")  # create client
stream = StreamSTT(api)

def print_stt(data):
    print(data)

stream.start()
stream.listen()

for i in range(10):
    stream.stream("/tmp/1.wav", i)
    time.sleep(1)
