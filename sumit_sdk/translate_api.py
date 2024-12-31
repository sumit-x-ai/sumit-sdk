from typing import Optional, Union
from sumit_sdk.base_task import BaseTask, TaskOperations


class TranslateAPI(BaseTask):
    """
    Run Translate api
    """

    def _set_op(self):
        self._operation = TaskOperations.TRANSLATE_API

    def build_request(self, text: str,
                      output_lang: Optional[Union[list, str]],
                      input_lang: Optional[str] = None,
                      out_length_limit: int = None):
        """
        Args:
            text: text to translate
            output_lang: list or one code language to translate the text
            input_lang: (optional) source code language
            out_length_limit: (optional) limit number of character
        Returns:
            - dict:
         {
         'request':
            {
                'operation': 'translate_api',
                'output_lang': ['en', 'ar'],
                'text': 'אני רוצה לתרגם כל מיני משפטים.'
            },
        'results':
            {
                'ar': 'أريد ترجمة جميع أنواع الجمل.',
                'en': 'I want to translate all kinds of sentences.',
            },
            'success': True
        }
        """
        request = {
            "text": text,
            "output_lang": output_lang,
        }
        if input_lang:
            request['input_lang'] = input_lang

        if out_length_limit:
            request['out_length_limit'] = out_length_limit
        return request
