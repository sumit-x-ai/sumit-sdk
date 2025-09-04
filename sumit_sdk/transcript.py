from sumit_sdk.base_task import BaseTask, TaskOperations


class SupportedModels:
    DEPRECAT_GENERIC_HEBREW_v2 = "he_gen_v2"
    GENERIC_HEBREW_v3 = "he_gen_v3"
    GENERIC_HEBREW_v4 = "he_gen_v4"
    GENERIC_HEBREW_v5 = "he_gen_v5"
    GENERIC_HEBREW = "he_gen_v5"
    GENERIC_HEBREW_TURBO = "he_v5_turbo"
    HEBREW_LEGAL = "he_v5_legal"
    HEBREW_PHONE = "he_v5_phone"
    GENERIC_MULTILINGUAL_v3 = "multilang_gen_v3"
    GENERIC_MULTILINGUAL_v2 = "multilang_gen"
    DEPRECAT_HEBREW_LEGAL = "hg2_legal"
    DEPRECAT_HEBREW_SUBTITLES = "hg2_subs"
    DEPRECAT_HEBREW_INTERVIEW = "hg2_interview"


class SupportedDiarization:
    UNSUPERVISED = 'unsupervised'


class Transcript(BaseTask):
    """
    Run Transcript task
    """

    def _set_op(self):
        self._operation = TaskOperations.TRANSCRIPT

    def build_request(self, file_path: str, output_path: str,
                      language: str, model: str = None,
                      flat_output_path: str = None, bucket_name: str = None, output_wav_path: str = None,
                      multichannel_diarize=False, multichannel_mix=False, group_by_speaker=False,
                      diarize=None, min_speakers=None, max_speakers=None,
                      callback=None, diarize_first=None, fine_timing=None,
                      callback_once=None, callback_payload=None,
                      signed_url_file: str=None, return_transcript_in_callback: bool=False
                      ):
        """
        Args:
            - file_path (str): the file location on the storage to transcript. Must upload the file to storage, use sumit_sdk.storage
            - output_path (str): the output file location on the storage. Here the transcription will stored.
            - language (str): language and country code of the file. e.g. en-US (English - United States), he-IL (hebrew - Israel). ISO-639 and ISO-3166
            - model (str): selected Speech-To-Text model to use. one of `SupportedModels`
            - flat_output_path (str) - the output file location on the storage. Here the transcription will stored. This is the flat version of the transcription.
            - callback (str) - URL to call when the task is done. must be valid HTTPS public url. 
            - multichannel_diarize (bool) - for multichannel audio file, use the channels for speakers separation
            - multichannel_mix (bool) - in case of multichannel audio, when using multichannel_diarize, mixdown all channels before transcription.
            - group_by_speaker (bool) - for the nested transcription format, group the segments by speaker name
            - diarize (str) - one of `SupportedDiarization` methods for speakers diarization
            - min_speakers (int) - for `SupportedDiarization.UNSUPERVISED` method, specify the minimun number of speakers in this record. leave None if unknown
            - max_speakers (int) - for `SupportedDiarization.UNSUPERVISED` method, specify the maximum number of speakers in this record. leave None if unknown
            - diarize_first (bool|None) - diarize before transcription. may improve speaker diarization but reduce transciption accuracy. leave None for system default (False)
            - fine_timing (bool|None) - use 2nd phase of forced alignment process to make words timestamps more accurate. leave None for system default (True if split_subtitles is True else False)
            - callback_once (bool|None) - notify the callback only once, when job finished. do not send updates for every stage. leave None for system default (False)
            - callback_payload (dict|None) - payload to return when calling callback endpoint
            - signed_url_file (str|None) - download the file to transcript from signed url instead of bucket. In this case path should be empty string. This option required extra permissions
            - return_transcript_in_callback - return the transcript result in the callback payload instead of upload json file to bucket. This option required extra permissions
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
        if multichannel_diarize:
            request['multichannel'] = {"diarize": True}
            if multichannel_mix:
                request['multichannel']['params'] = {'merge_type': 'mix'}
        elif diarize:
            request['diarize'] = diarize
            if min_speakers and max_speakers:
                request['diarize_param'] = {
                    'min_speakers': min_speakers,
                    'max_speakers': max_speakers,
                }
            else:
                request['diarize_param'] = {}
        if group_by_speaker:
            request['group_by'] = 'speaker'
        if diarize_first is not None:
            request['transcribe_first'] = not diarize_first
        if fine_timing is not None:
            request['fine_timing'] = fine_timing
        if callback and isinstance(callback, str) and callback.startswith("https://"):
            request['callback'] = callback
        if callback_once is not None:
            request['callback_once'] = callback_once
        if callback_payload is not None and isinstance(callback_payload, dict):
            request['callback_payload'] = callback_payload
        if signed_url_file:
            request['signed_url'] = signed_url_file
        if return_transcript_in_callback and 'callback' in request:
            request['stt_in_callback'] = return_transcript_in_callback
        return request
