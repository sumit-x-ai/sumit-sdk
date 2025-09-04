import time

from sumit_sdk.api import APIClient  # API core client
from sumit_sdk.stream_stt import StreamSTT
import librosa
import numpy as np

def print_stt(data):
    # print(f"response: {data}")
    transcript = data["transcript"][0]
    print(f"{data['id']}: {transcript['segment']}\nstart:{transcript.get('start')}\tend:{transcript.get('end')}")


# initialize API
api = APIClient("api-sa-prod.json", env='frankfurt')  # create client

stt = StreamSTT(api, print_stt)
response = stt.start()
if response.get('status_code') != 0:
    print(response)
    raise Exception("failed to retrieve session token. it's probably due to: incorrect user, missing permissions or networking issue.")

stt.listen()

print("send files:")
for i in range(5):
    stt.send_audio(f"audio_id_{i}", audio_path="/tmp/1.wav")  # send short audio file
    time.sleep(1)

# example 2: 
# chunk long file:

# print("send chunks:")
# audio, _ = librosa.load("/tmp/2.wav", sr=16000, mono=True)  # for this sample, use audio file longer than 50 seconds (or change the chunk size/number of chunks)
# # librosa load data as float, convert to int16
# audio *= (2 ** 15) - 1
# audio = audio.astype(np.int16)
# chunk_size = 10 * 16000  # 10 seconds length
# for i in range(5):
#     audio_data = audio[int(i * chunk_size):int((i + 1) * chunk_size)]
#     stt.send_audio(f"audio_id2_{i}", audio_data=audio_data)
#     time.sleep(1)


time.sleep(10)
stt.stop_listening()
