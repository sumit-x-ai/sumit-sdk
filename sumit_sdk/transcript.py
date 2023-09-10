from sumit_sdk.base_task import BaseTask, TaskOperations 
import json

class SupportedModels:
    GENERIC_HEBREW = "he_gen"

class Transcript(BaseTask):
    """
    Manages realtime sessions.

    Attributes:
    - sessions (dict): A dictionary to store session IDs and their corresponding data, including URLs for web socket communication.

    Methods:
    - start_session(): Starts a new session and stores its details.
    - stop_session(session_id): Stops an existing session.
    - get_active_sessions(): Returns the currently active sessions.
    """

    def _set_op(self):
        self._operation = TaskOperations.TRANSCRIPT
    
    def build_request(self, file_path: str, output_path: str,
            language:str, model:str=None, 
            flat_output_path: str=None, bucket_name: str=None, output_wav_path:str=None
            ):
        request = {
            "path": file_path,
            "output_path": output_path,
            "lang": language
        }
        if model:
            request['model'] = model
        if flat_output_path:
            request['flat_output_path'] = flat_output_path
        if bucket_name:
            request['bucket_name'] = bucket_name
        if output_wav_path:
            request['output_wav_path'] = output_wav_path
        return request

