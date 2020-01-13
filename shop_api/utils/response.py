from rest_framework.response import Response

class APIResponse(Response):
    def __init__(self, status=0, msg='ok', results=None, http_status=None, headers=None, exception=False, **kwargs):
        data = {
            'status': status,
            'msg': msg,
        }
        if results:
            data['results'] = results
        data.update(**kwargs)

        super().__init__(data=data, status=http_status, headers=headers, exception=exception)