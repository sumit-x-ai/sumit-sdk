import json
from threading import Thread, Event
from sumit_sdk.api import BaseWrapper
import base64
import websocket
from typing import Callable
import librosa
import numpy as np
import logging


class StreamSTT(BaseWrapper):
    # Endpoint for stream authentication
    _START_EP = "stream/auth"
    _URL = {
        "prod": "wss://stream.sumit-labs.com:443",
        "tenants": "wss://stream.{tenant}.sumit-labs.com",
    }
    _SR = 16000

    def __init__(self, api_instance, message_callback: Callable[[dict], None]) -> None:
        """
        Initialize the StreamSTT instance.

        Args:
            api_instance : An instance of the API wrapper (usually Sumit API).
            message_callback (function): A callback function to handle incoming messages from the WebSocket.
        """
        super().__init__(api_instance)
        self.callback = message_callback  # Callback function to handle incoming messages
        self.session_token = None  # Token for session authentication
        self._listen_event = Event()  # Event to signal when WebSocket connection is open
        self._env = api_instance._env  # Environment (e.g., 'dev' or 'prod')
        self.ws = None  # WebSocket instance
        self._listener_thread = None  # Thread for running WebSocket
        self.url = None 
        if self._env not in StreamSTT._URL:
            if self._env.startswith('http'):
                self.stream_url = f"wss://stream.{self._env.split('api.')[1]}:443"
            else:
                self.stream_url = StreamSTT._URL["tenants"].format(tenant=self._env)
        else:
            self.stream_url = StreamSTT._URL[self._env]

    @staticmethod
    def _encode_audio(audio_path: str) -> str:
        """
        Decode the audio file into a base64 encoded string.

        Args:
            audio_path (str): The file path of the audio file to be encoded.

        Returns:
            str: Base64 encoded string of the audio file.

        Raises:
            Exception: If there is an error while decoding the audio file.
        """
        try:
            audio_data, _ = librosa.load(audio_path, sr=StreamSTT._SR, mono=True)
            audio_data *= (2 ** 15) - 1
            audio_data = audio_data.astype(np.int16)
            return base64.b64encode(audio_data.tobytes())
        except Exception as e:
            raise Exception(f"Error decoding audio: {e}")

    @staticmethod
    def _on_error(ws, error) -> None:
        """
        Callback for handling WebSocket errors.

        Args:
            ws (WebSocketApp): The WebSocket application instance.
            error (str): Error message received from WebSocket.
        """
        logging.error(f"WebSocket error: {error}")

    @staticmethod
    def _on_close(ws, close_status_code, close_msg) -> None:
        """
        Callback for when the WebSocket connection is closed.

        Args:
            ws (WebSocketApp): The WebSocket application instance.
            close_status_code (int): The status code for closing the connection.
            close_msg (str): The closing message from WebSocket.
        """
        logging.info(f"WebSocket closed: {close_status_code}, {close_msg}")

    def _on_message(self, ws, message) -> None:
        """
         Callback for receiving messages from the WebSocket server.

         Args:
             ws (WebSocketApp): The WebSocket application instance.
             message (str): The message received from the WebSocket server.
         """
        if self.callback:
            try:
                self.callback(json.loads(message))
            except Exception as e:
                logging.error(f"Error in callback: {e}")

    def _on_open(self, ws) -> None:
        """
        Callback for when the WebSocket connection is opened.

        Args:
            ws (WebSocketApp): The WebSocket application instance.
        """
        logging.info("WebSocket connection opened")
        self._listen_event.set()  # Signal that the connection is open

    def start(self, reconnect: bool = False) -> str:
        """
        Start a session and retrieve a session token if not already initialized.

        Args:
            reconnect (bool): Flag to indicate whether to attempt to reconnect and get a new session token. Default is False.

        Returns:
            str: The session token for authentication.

        Raises:
            Exception: If the session token could not be retrieved.
        """
        if not self.session_token or reconnect:
            req = {}
            try:
                response = self.api.safe_call(StreamSTT._START_EP, req)
                if response.status_code != 200:
                    return {
                        "status_code": response.status_code,
                        "content": response.content
                    }
                response = response.json()
                self.session_token = response.get("token")
            except Exception as e:
                return {
                        "status_code": -1,
                        "content": str(e)
                    }
            if not self.session_token:
                raise Exception("Failed to retrieve session token")
            if not self.url:
                self.url = response.get("url", self.stream_url)
        response['status_code'] = 0
        return response

    def send_audio(self, audio_id: str, audio_data=None, audio_path: str=None, audio_byte_buffer=None, lid=False) -> None:
        """
        Send an audio file through the WebSocket connection.

        Args:
            audio_id (str): The unique identifier for the audio file.
            audio_path (str): The file path of the audio to be sent.
            audio_data (np.array): The audio buffer to be sent. should be 16bps, 16kHz, mono audio

        Raises:
            Exception: If the WebSocket is not connected or if there is an error sending the audio.
        """
        if not self.ws or not self.ws.sock.connected:
            raise Exception("WebSocket is not connected")
        encoded_audio = None
        if audio_path:
            encoded_audio = self._encode_audio(audio_path)
        elif audio_data is not None:
            encoded_audio = base64.b64encode(audio_data.tobytes())
        elif audio_byte_buffer is not None:
            encoded_audio = base64.b64encode(audio_byte_buffer)
        else:
            raise Exception("must provide one of: audio_path, audio_data, audio_byte_buffer")
        req = {
            "id": audio_id,
            "token": self.session_token,
            "data": encoded_audio.decode(),
        }
        if lid:
            req['lid'] = True
        try:
            self.ws.send(json.dumps(req))
        except Exception as e:
            raise Exception(f"Error sending audio: {e}")
    
    def listen(self) -> None:
        """
        Start listening to a WebSocket server.

        Raises:
            Exception: If the session token is not initialized.
        """
        if not self.session_token:
            raise Exception("Session token is not initialized")
        self._listen_event.clear()
        self.ws = websocket.WebSocketApp(
            self.url,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
            on_open=self._on_open,
        )
        self._listener_thread = Thread(target=self.ws.run_forever, daemon=True)
        self._listener_thread.start()
        self._listen_event.wait()  # Wait for WebSocket connection to open

    def stop_listening(self) -> None:
        """
        Stop listening to the WebSocket server and close the connection.

        This will close the WebSocket and join the listener thread to ensure clean shutdown.
        """
        self._listen_event.set()
        if self.ws:
            self.ws.close()
        if self._listener_thread and self._listener_thread.is_alive():
            self._listener_thread.join()
        self.session_token = None
