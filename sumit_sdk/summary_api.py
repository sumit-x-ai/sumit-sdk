from typing import Optional, Union
from sumit_sdk.base_task import BaseTask, TaskOperations


class SummaryApi(BaseTask):
    pass

    def _set_op(self):
        self._operation = TaskOperations.SUMMARY_API

    def build_request(self, summary_type: str = 'short_bullets', language: str = 'he-IL', sync: bool = True,
                      content: Optional[str] = None, topics: Optional[list] = None, input_bucket: Optional[str] = None,
                      input_blob_path: Optional[str] = None, output_blob_path: Optional[str] = None,
                      flat_output_blob_path: Optional[str] = None, callback: Optional[str] = None,
                      callback_payload: Optional[dict] = None):

        request = {
            "summary_type": summary_type,
            "language": language,
            "sync": sync,
        }
        optional_params = {
            'content': content,
            'topics': topics,
            'input_bucket': input_bucket,
            'input_blob_path': input_blob_path,
            'output_blob_path': output_blob_path,
            'flat_output_blob_path': flat_output_blob_path,
            'callback': callback,
            'callback_payload': callback_payload
        }

        request.update({k: v for k, v in optional_params.items() if v is not None})

        return request
