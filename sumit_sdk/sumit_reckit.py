from sumit_sdk.api import BaseWrapper 
from sumit_sdk.storage import Storage

class Reckit(BaseWrapper):
    _START_EP = "reckit/start"
    _STOP_EP = "reckit/stop"
    _HB_EP = "reckit/heartbeat"
    _PLAT_PROC_EP = "reckit/platform_process"
    _DOWNLOAD_EP = "reckit/download_version"
    _VERSION_EP = "reckit/get_version"

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
        data = self.api.safe_call(Reckit._STOP_EP, req).json()
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

    def heartbeat(self, kit_id, sync=False, status=None):
        req = {
            'id': kit_id,
            'sync': sync
        }
        if status:
            req['status'] = status
        data = self.api.safe_call(Reckit._HB_EP, req).json()
        return data

    def download_update(self, kit_id, path):
        req = {
            'id': kit_id,
        }
        data = self.api.safe_call(Reckit._DOWNLOAD_EP, req).json()
        if not data.get('success'):
            return False
        su = data.get('download_url')
        if not su:
            return False
        s = Storage(self.api)
        s._download(su, path, mode='b')
    
    def get_version(self, kit_id):
        req = {
            'id': kit_id,
        }
        data = self.api.safe_call(Reckit._VERSION_EP, req).json()
        if not data.get('success'):
            return None
        return data['version']
