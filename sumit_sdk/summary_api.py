from typing import Optional, Union
from sumit_sdk.base_task import BaseTask, TaskOperations

class SummaryTypes:
    BULLETS = 'short_bullets'
    PARAGRAPHS = 'short_paragraphs'

class SummaryApi(BaseTask):
    pass

    def _set_op(self):
        self._operation = TaskOperations.SUMMARY_API

    def build_request(self, summary_type: str = 'short_bullets', language: str = 'he-IL',
                      input_blob_path: Optional[str] = None, output_blob_path: Optional[str] = None,
                      content: Optional[str] = None, topics: Optional[list] = None, bucket_name: Optional[str] = None,
                      callback: Optional[str] = None, callback_payload: Optional[dict] = None):
        """
        Args:
            - summary_type (str): one of SummaryTypes
            - language (str): language and country code of the file. e.g. en-US (English - United States), he-IL (hebrew - Israel). ISO-639 and ISO-3166
            - input_blob_path (str): the file location on the storage to summarize. should be Sumit transcription json format. Must upload the file to storage, use sumit_sdk.storage
            - output_blob_path (str): the output file location on the storage. Here the summary will stored.
            - content (str): optional text content to summarize instead of summarize file in bucket.
            - topics(list[str]): optional topic list to summarize instead of auto extraction of topics.
            - callback (str) - URL to call when the task is done. must be valid HTTPS public url. 
           
        """
        request = {
            "summary_type": summary_type,
            "language": language,
        }
        optional_params = {
            'content': content,
            'topics': topics,
            'input_bucket': bucket_name,
            'input_blob_path': input_blob_path,
            'output_blob_path': output_blob_path,
            'callback': callback,
            'callback_payload': callback_payload
        }

        request.update({k: v for k, v in optional_params.items() if v is not None})

        return request
