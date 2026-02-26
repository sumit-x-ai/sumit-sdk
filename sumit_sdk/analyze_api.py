from typing import Optional
from sumit_sdk.base_task import BaseTask, TaskOperations


class AnalyzeOption:
    AVAILABLE_ANALYZE = {
        "meeting_name": "Identified meeting name from the content",
        "action_items": "Tasks to be completed that were discussed",
        "topic_list": "List of topics discussed",
        "keywords": "Key terms from the meeting",
        "decisions": "Decisions made during the meeting",
        "topic_for_summary": "Main topics for summary",
        "participants": "List of meeting participants",
        "general_summary": "General summary of the meeting",
        "customer_service": "Customer service call analysis including resolution status, satisfaction score, sentiment dynamics, churn risk, action items, and agent rating"
    }


class AnalyzeApi(BaseTask):

    def _set_op(self):
        self._operation = TaskOperations.ANALYZE_API

    @staticmethod
    def get_analyze_description(key=None):
        print("Please note (for clarification only):\n"
              " There may be additional options for analysis - we will update accordingly.")
        if key is None:
            return AnalyzeOption.AVAILABLE_ANALYZE
        return AnalyzeOption.AVAILABLE_ANALYZE.get(key)

    def build_request(self, requests: list, language: str = 'he-IL', 
                      input_blob_path: Optional[str] = None, output_blob_path: Optional[str] = None,
                      content: Optional[str] = None, bucket_name: Optional[str] = None,
                      callback: Optional[str] = None, callback_payload: Optional[dict] = None):
        """
        Args:
            - requests (list): list of analyze to processes
            - language (str): language and country code of the file. e.g. en-US (English - United States), he-IL (hebrew - Israel). ISO-639 and ISO-3166
            - input_blob_path (str): the file location on the storage to analyze. should be Sumit transcription json format. Must upload the file to storage, use sumit_sdk.storage
            - output_blob_path (str): the output file location on the storage. Here the summary will stored.
            - content (str): optional text content to summarize instead of summarize file in bucket.
            - callback (str) - URL to call when the task is done. must be valid HTTPS public url.

        """
        request = {
            "requests": requests,
            "language": language,
        }
        optional_params = {
            'content': content,
            'input_bucket': bucket_name,
            'input_blob_path': input_blob_path,
            'output_blob_path': output_blob_path,
            'callback': callback,
            'callback_payload': callback_payload
        }

        request.update({k: v for k, v in optional_params.items() if v is not None})

        return request
