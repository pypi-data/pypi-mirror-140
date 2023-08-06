from pynosql_logger.constant import DEFAULT_SUCCESS_MESSAGE
from pynosql_logger.helper import get_uuid
from datetime import datetime

class Meta:
    @staticmethod
    def add_meta(idx, item):
        if item:
            item['_log_id'] = get_uuid(idx)
            now = datetime.now()
            item['_updated_at'] = now.strftime("%d-%m-%Y %H:%M:%S")
            # item['_updated_date'] = now.strftime("%Y-%m-%d")
        return item

class Response:
    @staticmethod
    def get_response(resp, message=DEFAULT_SUCCESS_MESSAGE):
        resp['success'] = True
        resp['message'] = message
        return resp

    @staticmethod
    def get_error(err):
        return {
            'success': False,
            'message': str(err)
        }

class LoggerException(Exception):
    pass

class SystemLog:
    @staticmethod
    def print_log(msg):
        now = datetime.now().strftime("%d-%b-%Y %I:%M %p")
        print('python_nosql_logger => {} => {}'.format(now, msg))