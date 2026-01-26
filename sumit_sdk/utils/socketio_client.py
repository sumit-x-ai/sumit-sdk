import socketio
import logging

class SocketClient():
    def __init__(self, url, ssl_verify=False):
        self.url = url
        self.connected = False
        self.sio = socketio.Client(reconnection_delay=1, reconnection_delay_max=1,
                      randomization_factor=0, logger=False, ssl_verify=ssl_verify)
        self.user_callbacks = {}
        self.callbacks()

    def connect(self):
        self.sio.connect(self.url, wait_timeout = 3)

    def send_message(self, event_name, data):
        self.sio.emit(event_name, data)

    def register_callback(self, event_name, callback_func):
        """
        Registers a user-defined callback for a specific event.

        Args:
        - event_name (str): The name of the event.
        - callback_func (function): The callback function to be executed.
        """
        self.user_callbacks[event_name] = callback_func

    def callbacks(self):
        @self.sio.event
        def connect():
            logging.info(f'Socket connected')
            if not self.connected:
                self.connected = True

        @self.sio.event
        def disconnect():
            logging.info(f'Socket disconnected')
            self.connected = False

        @self.sio.on('*')  # wildcard to capture all events
        def handle_message(event, data):
            callback = self.user_callbacks.get(event)
            if callback:
                callback(data) 
