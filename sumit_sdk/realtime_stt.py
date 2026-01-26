from sumit_sdk.api import BaseWrapper 
from sumit_sdk.utils.socketio_client import SocketClient 
import time
import json

class Profiles:
    default = 'default'  # Est. latency: 3 seconds
    low_latency = 'low_latency'  # Est. latency: 2.5 seconds
    lower_latency = 'lower_latency'  # Est. latency: 1.5 seconds
    accurate = 'accurate'  # Est. latency: 5 seconds
    very_accurate = 'very_accurate'  # Est. latency: 7 seconds

class VadProfile:
    default = 'default'
    high = 'high'
    low = 'low'
    very_low = 'very_low'
    off = 'off'

class BufferMode:
    default = 'accumulate'
    switch = 'switch'

class RealtimeSTT(BaseWrapper):
    """
    Manages realtime sessions.

    Attributes:
    - sessions (dict): A dictionary to store session IDs and their corresponding data, including URLs for web socket communication.

    Methods:
    - start_session(): Starts a new session and stores its details.
    - stop_session(session_id): Stops an existing session.
    - get_active_sessions(): Returns the currently active sessions.
    """

    _START_EP = "realtime/start"
    _STOP_EP = "realtime/stop"
    _STATUS_EP = "realtime/get_status"

    def __init__(self, api_instance) -> None:
        """
        Initializes the RealtimeSTT.

        Args:
        - api_instance (APIClient): An instance of the APIClient class.
        """        
        super().__init__(api_instance)
        self.sessions = {}
        self.current_session = None
        self.transcript_callback = None

    def start_session(self, transcript_callback, language:str=None, profile:str=None, vad_profile:str=None, buffer_mode=None, _add_params=None) -> dict:
        """
        Starts a new session and stores its details.

        Args:
        - transcript_callback: callback function to notify when transcription received.
        - language (str): language code. default is he-IL (Hebrew)
        - profile (str): one of `realtime_stt.Profiles` - control the latency and accuracy of the transcription. 
            usually the higher the latency, higher the accuracy 
        - vad_profile (str): one of `realtime_stt.VadProfiles` - control the VAD thresholds to avoid non-speech transcription. 
        - buffer_mode (str): one of `realtime_stt.BufferMode` - control the buffering method for the speech context.

        Returns:
        - dict: containing the session ID and its corresponding URL.
        """      
        req = {}  
        if language:
            req['lang'] = language
        if profile:
            req['profile'] = profile
        if vad_profile:
            req['vad_profile'] = vad_profile
        if buffer_mode:
            req['buffer_mode'] = buffer_mode
        if _add_params:
            req.update(_add_params)
        data = self.api.safe_call(RealtimeSTT._START_EP, req).json()
        session_id = data.get("session_id")
        self.sessions[session_id] = data
        self.current_session = session_id
        self.transcript_callback = transcript_callback
        return data

    def _inject_session(self, session_id, url, transcript_callback) -> dict:
        """
        Starts a new session and stores its details.

        Returns:
        - dict: containing the session ID and its corresponding URL.
        """        
        # data = self.api.safe_call(RealtimeSTT._START_EP, {}).json()
        self.sessions[session_id] = {"id": session_id, "endpoint": url}
        self.current_session = session_id
        self.transcript_callback = transcript_callback
        return self.sessions[session_id]

    def stop_session(self, session_id: str=None):
        """
        Stops an existing session.

        Args:
        - session_id (str): The ID of the session to stop. if None - get the last created session
        """
        if not session_id:
            session_id = self.current_session
        ret = self.api.safe_call(RealtimeSTT._STOP_EP, {"id": session_id})
        if ret:
            ret = ret.json()
        else:
            raise Exception("failed to stop session")
        if session_id in self.sessions:
            self.sessions.pop(session_id)
        if ret.get('success') and session_id == self.current_session:
            self.current_session = None
        return ret

    def get_active_sessions(self) -> dict:
        """
        Returns the currently active sessions ids.

        Returns:
        - dict: A dictionary containing the session IDs and their corresponding URLs.
        """
        return self.sessions
    
    def _wait_ready(self, session_id: str):
        ready = False
        wait_time = 30
        while not ready:
            ret = self.api.safe_call(RealtimeSTT._STATUS_EP, {"id": session_id})
            if ret:
                ret = ret.json()
            else:
                continue
            ready = ret.get('status', {}).get('transcript')
            if not ready:
                # limit the number of calls to sumit-api to avoid `quota exceed` block
                # in future release it's will replaces with events
                time.sleep(wait_time)
                if wait_time >= 10:
                    wait_time -= 5

    def connect(self, session_id: str=None) -> SocketClient:
        """
        connect to streaming end point for realtime transcription.

        Args:
        - session_id (str): The ID of the session to stop. if None - get the last created session

        Returns:
        SocketClient instance for async streaming to the realtime server
        """
        if not session_id:
            session_id = self.current_session
        print("monitor instance state...")
        self._wait_ready(session_id)
        url = self.sessions[session_id]["endpoint"]
        print(f"ready, init socket client: {url}")
        sock = SocketClient("https://" + url)
        sock.register_callback('txt', self._parse_json)
        sock.connect()
        return sock
    
    def send(self, sock: SocketClient, data):
        """
        send audio chunk to transcript

        Args:
        - sock (SocketClient): socket instance to use. received from `connect` method
        - data: base64 bytes to send

        """        
        sock.send_message('data', data)

    def _parse_json(self, msg):
        m = json.loads(msg)
        if self.transcript_callback:
            self.transcript_callback(m)
