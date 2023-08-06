# -*- coding: utf-8 -*-

import json

from huaweicloudsdkcore.exceptions import exceptions

class IefError:
    def __init__(self, request_id=None, error_code=None, error_msg=None):
        self.error_msg = error_msg
        self.error_code = error_code
        self.request_id = request_id

def handle_exception(response_body):
    ief_error = IefError()
    
    ief_error_dict = json.loads(response_body)
    for key in ief_error_dict:
        if type(ief_error_dict[key]) == dict and "error_code" in ief_error_dict[key] and "error_msg" in \
                ief_error_dict[key]:
            ief_error = IefError("0a04ffbcb5db120ce371f27e078e8980",
                                       ief_error_dict[key]["error_code"], ief_error_dict[key]["error_msg"])
    return ief_error
