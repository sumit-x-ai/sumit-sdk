from sumit_sdk.api import BaseWrapper 
import json
import time

class TaskOperations:
    TRANSCRIPT = 'transcript'
    GET_STATUS = 'get_status'
    TRANSLATE_API = 'translate'
    TRANSLATE_SUBS = 'translate_subtitles'
    SUMMARY_API = 'summarize'

class BaseTask(BaseWrapper):
    """
    Abstract class to implement API calls for tasks.

    Methods:
    - execute(): run new task, with custom payload.
    - build_request(**kwargs): create payload for the request.
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
        self._wait_interval = 5
        self._set_op()
    
    def _set_op(self):
        raise Exception("_set_op not implemented")

    def execute(self, payload):
        endpoint = f"{self._API_VERSION}/{self._operation}"
        try:
            ret = self.api.safe_call(endpoint, payload)
        except Exception as e:
            return {
                'status_code': -1,
                'content': str(e)
            }
        try:
            ret = ret.json()
            return ret
        except:
            return {
                'status_code': ret.status_code,
                'content': ret.content
            }

    def build_request(self, **kwargs):
        raise Exception("build_request not implemented")

    def run(self, **kwargs):
        return self.execute(self.build_request(**kwargs))

    def get_task_status(self, task_id: str):
        """
        get the status of async task, by task_id.
        task_id returned from the response: response['response']['job_id']
        """
        ret = self.api.safe_call(TaskOperations.GET_STATUS, {
            'id': task_id
        })
        ret = ret.json()
        return ret
    
    def wait_for_task(self, task_id: str):
        """
        blocking function to wait until task is done.
        alternatively, you can use `callback` to get notified when task is done
        """
        finish = False
        ret = None
        while not finish:
            try:
                ret = self.get_task_status(task_id)
                finish = ret['response']['progress'] == 100
                if finish:
                    break
            except:
                pass
            time.sleep(self._wait_interval)
        return ret
