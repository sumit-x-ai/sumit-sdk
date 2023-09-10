from sumit_sdk.api import BaseWrapper 
import json
import time

class TaskOperations:
    TRANSCRIPT = 'transcript'
    GET_STATUS = 'get_status'

class BaseTask(BaseWrapper):
    """
    Abstract class to implement API calls for tasks.

    Methods:
    - start_session(): Starts a new session and stores its details.
    - stop_session(session_id): Stops an existing session.
    - get_active_sessions(): Returns the currently active sessions.
    """
    _API_VERSION = 'v3'

    def __init__(self, api_instance) -> None:
        """
        Initializes the BaseTask.

        Args:
        - api_instance (APIClient): An instance of the APIClient class.
        """        
        super().__init__(api_instance)
        self._operation = None
        self._set_op()
        self._wait_interval = 3
    
    def _set_op(self):
        raise Exception("_set_op not implemented")

    def execute(self, payload):
        endpoint = f"{self._API_VERSION}/{self._operation}"
        ret = self.api.safe_call(endpoint, payload)
        ret = ret.json()
        return ret

    def build_request(self, **kwargs):
        raise Exception("build_request not implemented")

    def run(self, **kwargs):
        return self.execute(self.build_request(**kwargs))

    def get_task_status(self, task_id: str):
        ret = self.api.safe_call(TaskOperations.GET_STATUS, {
            'id': task_id
        })
        ret = ret.json()
        return ret
    
    def wait_for_task(self, task_id: str):
        finish = False
        ret = None
        while not finish:
            try:
                ret = self.get_task_status(task_id)
                finish = ret['progress'] == 100
                if finish:
                    break
            except:
                pass
            time.sleep(self._wait_interval)
        return ret
