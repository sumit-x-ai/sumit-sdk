from sumit_sdk.base_task import BaseTask, TaskOperations 

class SupportedModels:
    GENERIC_HEBREW = "he_gen_v2"

class Transcript(BaseTask):
    """
    Run Transcript task
    """

    def _set_op(self):
        self._operation = TaskOperations.TRANSCRIPT
    
    def build_request(self, file_path: str, output_path: str,
            language:str, model:str=None, 
            flat_output_path: str=None, bucket_name: str=None, output_wav_path:str=None,
            callback=None
            ):
        """
        Args:
            - file_path (str): the file location on the storage to transcript. Must upload the file to storage, use sumit_sdk.storage
            - output_path (str): the output file location on the storage. Here the transcription will stored.
            - language (str): language and country code of the file. e.g. en-US (English - United States), he-IL (hebrew - Israel). ISO-639 and ISO-3166
            - model (str): selected Speech-To-Text model to use. one of `SupportedModels`
            - flat_output_path (str) - the output file location on the storage. Here the transcription will stored. This is the flat version of the transcription.
            - callback (str) - URL to call when the task is done. must be valid HTTPS public url. 
        """
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
        if callback and isinstance(callback, str) and callback.startswith("https://"):
            request['callback'] = callback
        return request

