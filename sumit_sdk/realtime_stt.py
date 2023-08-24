from sumit_sdk.api import BaseWrapper 

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

    def __init__(self, api_instance) -> None:
        """
        Initializes the RealtimeSTT.

        Args:
        - api_instance (APIClient): An instance of the APIClient class.
        """        
        super().__init__(api_instance)
        self.sessions = {}

    def start_session(self) -> dict:
        """
        Starts a new session and stores its details.

        Returns:
        - dict: containing the session ID and its corresponding URL.
        """        
        data = self.api.safe_call(RealtimeSTT._START_EP, {}).json()
        session_id = data.get("session_id")
        self.sessions[session_id] = data
        return data

    def stop_session(self, session_id: str):
        """
        Stops an existing session.

        Args:
        - session_id (str): The ID of the session to stop.
        """
        ret = self.api.safe_call(RealtimeSTT._STOP_EP, {"id": session_id}).json()
        if session_id in self.sessions:
            self.sessions.pop(session_id)

    def get_active_sessions(self) -> dict:
        """
        Returns the currently active sessions ids.

        Returns:
        - dict: A dictionary containing the session IDs and their corresponding URLs.
        """
        return self.sessions