from sumit_sdk.api import BaseWrapper 

class Reckit(BaseWrapper):
    _START_EP = "reckit/start"
    _STOP_EP = "reckit/stop"
    _HB_EP = "reckit/heartbeat"
    _PLAT_PROC_EP = "reckit/platform_process"

    def __init__(self, api_instance) -> None:
        super().__init__(api_instance)
    
    def start(self, rec_id, kit_id, name=None):
        req = {
            'id': rec_id,
            'kit_id': kit_id,
        }
        if name:
            req['name'] = name
        data = self.api.safe_call(Reckit._START_EP, req).json()
        return data

    def stop(self, rec_id, kit_id, name=None):
        req = {
            'id': rec_id,
            'kit_id': kit_id,
        }
        if name:
            req['name'] = name
        data = self.api.safe_call(Reckit._START_EP, req).json()
        return data

    def platform_process(self, rec_id, kit_id, wav_files:list[str], duration=None, part_ix:int=0, 
        name:str=None, lang='he-IL', out_lang=None, offset:float=0, is_last=False):
        req = {
            'id': rec_id,
            'kit_id': kit_id,
            'part_ix': part_ix,
            'samplerate': 16000,
            'offset': offset,
            'wav_files': wav_files,
            'input_lang': lang,
            'output_lang': out_lang if out_lang else [lang],
            'last': is_last, 
            'duration': duration
        }
        if name:
            req['name'] = name
        data = self.api.safe_call(Reckit._PLAT_PROC_EP, req).json()
        return data
