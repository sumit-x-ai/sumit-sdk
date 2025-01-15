from sumit_sdk.base_task import BaseTask, TaskOperations


class SupportedModels:
    DEPRECAT_GENERIC_HEBREW_v2 = "he_gen_v2"
    GENERIC_HEBREW = "he_gen_v3"
    GENERIC_HEBREW_BETA = "he_gen_v4"
    HEBREW_LEGAL = "hg2_legal"
    HEBREW_SUBTITLES = "hg2_subs"
    HEBREW_INTERVIEW = "hg2_interview"


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
                      callback=None, transcribe_first=True, fine_timing=True
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
        if callback and isinstance(callback, str) and callback.startswith("https://"):
            request['callback'] = callback
        return request
