from typing import Optional

from sumit_sdk.base_task import BaseTask, TaskOperations


class TranslateSubtitles(BaseTask):
    def _set_op(self):
        self._operation = TaskOperations.TRANSLATE_SUBS

    def build_request(self, output_lang: str, input_blob_path: str, output_blob_path: str,
                      input_lang: Optional[str] = None, lines_num: Optional[int] = 2, max_chars: Optional[int] = 36,
                      callback: Optional[str] = None, callback_payload: Optional[dict] = None,
                      split_by_sentence: bool = False, user_instructions: str = '', ktiv_male: bool = True,
                      rephrase: bool = True):
        """

        Args:
            output_lang: Target language for translation
            input_blob_path: Path to an existing file in the bucket. Should be Sumit json format, grouped by subtitles
            output_blob_path: Path to the file to receive the translation
            input_lang: Source file language (if not given, the system will try to detect it itself)
            lines_num: Maximum lines in one subtitle
            max_chars: Maximum characters in one subtitle
            callback: URL for receiving process completion notification
            callback_payload: Other things you might want to get in a callback
            split_by_sentence:
            user_instructions: Special instructions for translation
            ktiv_male: Intended for Hebrew language only - for full spelling translation
            rephrase: In the event of an excess number of characters in the subtitle -
             whether to rephrase to obtain a subtitle without excess characters
        """
        request = {
            "output_lang": output_lang,
            "input_blob_path": input_blob_path,
            "output_blob_path": output_blob_path,
        }
        optional_params = {
            'lines_num': lines_num,
            'input_lang': input_lang,
            'max_chars': max_chars,
            'callback': callback,
            'callback_payload': callback_payload,
            'split_by_sentence': split_by_sentence,
            'user_instructions': user_instructions,
            'ktiv_male': ktiv_male,
            'rephrase': rephrase,

        }

        request.update({k: v for k, v in optional_params.items() if v is not None})

        return request
