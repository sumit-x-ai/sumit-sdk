from typing import Optional, Union
from sumit_sdk.api import BaseWrapper 



class UsersAPI(BaseWrapper):
    USAGE_REPORT = '/users/usage_report'
    GET_QUOTA = '/users/get_quota'
    """
    Manage user keys, quota and reports
    """
    def usage_report(self, months:Optional[int]=12, days:Optional[int]=None, email:Optional[str]=None):
        req = {
            'months': months
        }
        if days and isinstance(days, int):
            req['days'] = days
        if email and isinstance(email, str):
            req['email'] = email
        data = self.api.safe_call(UsersAPI.USAGE_REPORT, req).json()
        return data

    def get_quota(self):
        req = {}
        data = self.api.safe_call(UsersAPI.GET_QUOTA, req).json()
        return data
