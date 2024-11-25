from threading import Thread, Event
from sumit_sdk.api import BaseWrapper 

API_URL = {
    "dev": "https://stream.sumit-labs-dev.com",
    "prod": "https://stream.sumit-labs.com",
}

class StreamSTT(BaseWrapper):
    _START_EP = "stream/auth"

    def __init__(self, api_instance, message_callback) -> None:
        super().__init__(api_instance)
        self.callback = message_callback
        self.session_token = None
        self._listen_event = Event()
        self._env = api_instance._env # TODO: check
    
    def start(self, rec_id, kit_id, name=None):
        req = {}
        data = self.api.safe_call(Reckit._START_EP, req).json()
        self.session_token = None # TODO: get from response
        return data

    def send_audio(self, audio, audio_id):
        req = {
            'id': audio_id,
            'token': self.session_token
            'audio': audio # TODO: base64 encoded
        }
        # TODO: send data via websocket
        # TODO: raise exception if failed


    def listen(self): # TODO: non-blocking, run in background thread
        if not self.callback:
            raise Exception("callback not defined")
        self._listen_event.clear()
        while not self._listen_event.is_set():
            pass 
            # TODO: socket.recv()
            #       call callback when message arrived
            # OR: another way to implement this async method. maybe already supported by asyncio or websocket
    
    def stop_listening(self):
        self._listen_event.set()
