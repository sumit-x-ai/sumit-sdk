import time

from sumit_sdk.api import APIClient  # API core client
from sumit_sdk.strean_stt import StreamSTT


def print_stt(data):
    # print(f"response: {data}")
    transcript = data["transcript"][0]
    print(f"{data['id']}: {transcript['segment']}\nstart:{transcript['start']}\tend:{transcript['end']}")


# initialize API
api = APIClient("api-sa-dev.json", env="dev")  # create client

stt = StreamSTT(api, print_stt)
stt.start()
stt.listen()

for i in range(10):
    stt.send_audio("/tmp/1.wav", f"audio_id_{i}")
    time.sleep(1)
    # break

time.sleep(10)
stt.stop_listening()
