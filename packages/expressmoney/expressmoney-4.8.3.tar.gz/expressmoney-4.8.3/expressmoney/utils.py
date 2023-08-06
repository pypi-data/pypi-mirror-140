import datetime
import enum
import json
import re
import time
from contextlib import suppress
from enum import Enum
from typing import Union

import requests
from google.protobuf import timestamp_pb2
from google.cloud import pubsub_v1
from google.cloud import tasks_v2
from google.cloud import error_reporting

report = error_reporting.Client()


class ViewFlowStatus(Enum):
    """Process result statuses for ViewFlow framework"""
    EMPTY = 'EMPTY'
    NEW = 'NEW'
    IN_PROCESS = 'INPR'
    SUCCESS = 'SCS'
    ERROR = 'ERR'
    FAILURE = 'FAIL'
    CANCEL = 'CANCEL'
    RETRY = 'RETRY'


@enum.unique
class HttpStatus(enum.IntEnum):
    """
    Descriptive HTTP status codes, for code readability.

    See RFC 2616 - https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
    And RFC 6585 - https://tools.ietf.org/html/rfc6585
    And RFC 4918 - https://tools.ietf.org/html/rfc4918
    """
    HTTP_100_CONTINUE = 100
    HTTP_101_SWITCHING_PROTOCOLS = 101
    HTTP_200_OK = 200
    HTTP_201_CREATED = 201
    HTTP_202_ACCEPTED = 202
    HTTP_203_NON_AUTHORITATIVE_INFORMATION = 203
    HTTP_204_NO_CONTENT = 204
    HTTP_205_RESET_CONTENT = 205
    HTTP_206_PARTIAL_CONTENT = 206
    HTTP_207_MULTI_STATUS = 207
    HTTP_208_ALREADY_REPORTED = 208
    HTTP_226_IM_USED = 226
    HTTP_300_MULTIPLE_CHOICES = 300
    HTTP_301_MOVED_PERMANENTLY = 301
    HTTP_302_FOUND = 302
    HTTP_303_SEE_OTHER = 303
    HTTP_304_NOT_MODIFIED = 304
    HTTP_305_USE_PROXY = 305
    HTTP_306_RESERVED = 306
    HTTP_307_TEMPORARY_REDIRECT = 307
    HTTP_308_PERMANENT_REDIRECT = 308
    HTTP_400_BAD_REQUEST = 400
    HTTP_401_UNAUTHORIZED = 401
    HTTP_402_PAYMENT_REQUIRED = 402
    HTTP_403_FORBIDDEN = 403
    HTTP_404_NOT_FOUND = 404
    HTTP_405_METHOD_NOT_ALLOWED = 405
    HTTP_406_NOT_ACCEPTABLE = 406
    HTTP_407_PROXY_AUTHENTICATION_REQUIRED = 407
    HTTP_408_REQUEST_TIMEOUT = 408
    HTTP_409_CONFLICT = 409
    HTTP_410_GONE = 410
    HTTP_411_LENGTH_REQUIRED = 411
    HTTP_412_PRECONDITION_FAILED = 412
    HTTP_413_REQUEST_ENTITY_TOO_LARGE = 413
    HTTP_414_REQUEST_URI_TOO_LONG = 414
    HTTP_415_UNSUPPORTED_MEDIA_TYPE = 415
    HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE = 416
    HTTP_417_EXPECTATION_FAILED = 417
    HTTP_418_IM_A_TEAPOT = 418
    HTTP_422_UNPROCESSABLE_ENTITY = 422
    HTTP_423_LOCKED = 423
    HTTP_424_FAILED_DEPENDENCY = 424
    HTTP_426_UPGRADE_REQUIRED = 426
    HTTP_428_PRECONDITION_REQUIRED = 428
    HTTP_429_TOO_MANY_REQUESTS = 429
    HTTP_431_REQUEST_HEADER_FIELDS_TOO_LARGE = 431
    HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS = 451
    HTTP_500_INTERNAL_SERVER_ERROR = 500
    HTTP_501_NOT_IMPLEMENTED = 501
    HTTP_502_BAD_GATEWAY = 502
    HTTP_503_SERVICE_UNAVAILABLE = 503
    HTTP_504_GATEWAY_TIMEOUT = 504
    HTTP_505_HTTP_VERSION_NOT_SUPPORTED = 505
    HTTP_506_VARIANT_ALSO_NEGOTIATES = 506
    HTTP_507_INSUFFICIENT_STORAGE = 507
    HTTP_508_LOOP_DETECTED = 508
    HTTP_509_BANDWIDTH_LIMIT_EXCEEDED = 509
    HTTP_510_NOT_EXTENDED = 510
    HTTP_511_NETWORK_AUTHENTICATION_REQUIRED = 511

    @staticmethod
    def is_informational(code):
        return 100 <= code <= 199

    @staticmethod
    def is_success(code):
        return 200 <= code <= 299

    @staticmethod
    def is_redirect(code):
        return 300 <= code <= 399

    @staticmethod
    def is_client_error(code):
        return 400 <= code <= 499

    @staticmethod
    def is_server_error(code):
        return 500 <= code <= 599

    @staticmethod
    def is_not_found(code):
        return code == HttpStatus.HTTP_404_NOT_FOUND


def fix_flow_signal(func):
    def _wrapper_fix_signal(self, **kwargs):
        kwargs.update({'self': self})
        func(**kwargs)

    return _wrapper_fix_signal


def report_exception(func):
    """Decorator for exceptions. Send error in Google Error Reporting and cancel exception."""

    def exception_wrapper(**kwargs):
        try:
            result = func(**kwargs)
            return result
        except Exception as exc:
            report.report(str(exc)[:2048])

    return exception_wrapper


class PubSub:
    """ Google Cloud PubSub Adapter"""

    __publisher = pubsub_v1.PublisherClient()

    def __init__(self, topic_id: str, access_token: str = None, project='expressmoney'):
        self.__topic_path = self.__publisher.topic_path(project, topic_id)
        self.__access_token = str(access_token)

    def publish(self, payload: dict = None):
        attrs = {'topic': self.__topic_path, }

        if payload and not isinstance(payload, dict):
            raise TypeError('Payload should be dict type')

        if payload:
            if self.__access_token:
                payload.update({'access_token': self.__access_token})
        else:
            if self.__access_token:
                payload = {'access_token': self.__access_token}
        if payload:
            attrs.update({'data': json.dumps(payload, ensure_ascii=False).encode('UTF-8')})

        self.__publisher.publish(**attrs)


class Tasks:
    """ Google Cloud Tasks Adapter"""

    def __init__(self,
                 service: str = 'default',
                 path: str = '/',
                 access_token: str = None,
                 project: str = 'expressmoney',
                 queue: str = 'attempts-1',
                 location: str = 'europe-west1',
                 in_seconds: int = None,
                 ):
        """
        CloudTasks adapter
        Args:
            project: 'expressmoney'
            service: 'default'
            path: '/user'
            access_token: 'Bearer DFD4345345D'
            queue: 'my-appengine-queue'
            location: 'europe-west1'
            in_seconds: None
        """
        self._project = project
        self._service = service
        self._path = path
        self._access_token = access_token
        self._update = None
        self._in_seconds = in_seconds

        self._payload = None
        self._parent = self._client.queue_path(project, location, queue)

    _client = tasks_v2.CloudTasksClient()

    def create(self, payload: dict = None, update: bool = False):
        """
        Execution
        Args:
            payload: {'param': 'value'}
            update: tasks_v2.HttpMethod.PUT
        """
        self._update = update
        self._payload = payload
        task = self._create_task()
        task = self._add_payload(task)
        task = self._convert_in_seconds(task)
        task = self._add_authorization(task)
        task = self._remove_empty_headers(task)
        self._client.create_task(parent=self._parent, task=task)

    def _create_task(self):
        task = {
            'app_engine_http_request': {
                'http_method': self._http_method,
                'relative_uri': self._path,
                'headers': {},
                'app_engine_routing': {
                    'service': self._service,
                    'version': '',
                    'instance': '',
                    'host': '',

                }
            },
        }

        return task

    def _add_authorization(self, task):
        if self._access_token:
            task["app_engine_http_request"]["headers"]['X-Forwarded-Authorization'] = f'Bearer {self._access_token}'
        return task

    def _add_payload(self, task):
        if self._payload is not None:
            if not isinstance(self._payload, dict):
                raise TypeError('Payload should be dict type')
            payload = json.dumps(self._payload, ensure_ascii=False).encode('utf-8')
            task["app_engine_http_request"]["body"] = payload
            task["app_engine_http_request"]["headers"]['Content-Type'] = 'application/json'
        return task

    def _convert_in_seconds(self, task):
        if self._in_seconds is not None:
            d = datetime.datetime.utcnow() + datetime.timedelta(seconds=self._in_seconds)
            timestamp = timestamp_pb2.Timestamp()
            timestamp.FromDatetime(d)
            task['schedule_time'] = timestamp
        return task

    @staticmethod
    def _remove_empty_headers(task):
        if len(task['app_engine_http_request']['headers']) == 0:
            del task['app_engine_http_request']['headers']
        return task

    @property
    def _http_method(self):
        if self._update:
            return tasks_v2.HttpMethod.PUT
        else:
            return tasks_v2.HttpMethod.GET if self._payload is None else tasks_v2.HttpMethod.POST


class Request:
    """Sync http request"""

    def __init__(self,
                 service: str = None,
                 path: str = '/',
                 access_token: Union[str, None] = None,
                 project: str = 'expressmoney',
                 timeout: tuple = (30, 30),
                 ):
        self._project = project
        self.__service = service
        self.__path = path
        self.__access_token = access_token
        self._timeout = timeout

    def get(self):
        response = requests.get(self._uri, headers=self._headers, timeout=self._timeout)
        return response

    def put(self, payload=None):
        payload = {} if payload is None else payload
        response = requests.put(self._uri, json=payload, headers=self._headers, timeout=self._timeout)
        return response

    def post(self, payload: dict):
        response = requests.post(self._uri, json=payload, headers=self._headers, timeout=self._timeout)
        return response

    def post_file(self, file, file_name: str, type_: int = 1, is_public=False):
        """
        Save file in Google Storage
        Args:
            file: BytesIO file
            file_name: "name_file.pdf"
            type_: 1 - other files. All types see in storage service
            is_public: True - access to file without auth.

        Returns:

        """
        if len(file_name.split('.')) == 0:
            raise Exception('File name in format "name_file.pdf"')

        name, ext = file_name.split('.')
        name = f'{name}_{datetime.datetime.now().timestamp()}'
        name = re.sub('[^0-9a-zA-Z_]', '', name)
        new_file_name = f'{name}.{ext}'

        if re.match('^_[0-9]{16}$', name):
            raise Exception('File name incorrect. Example correct "name_file.pdf"')

        data = {
            'name': name,
            'type': type_,
            'is_public': is_public,

        }

        with suppress(Exception):
            file = getattr(file, 'file')

        response = requests.post(
            url=self._uri,
            data=data,
            files={"file": (new_file_name, file)},
            headers=self._headers,
            timeout=self._timeout
        )
        if not any((HttpStatus.is_success(response.status_code), HttpStatus.is_client_error(response.status_code))):
            try:
                raise Exception(f'{response.status_code}:{response.url}:{response.json()}')
            except Exception:
                raise Exception(f'{response.status_code}:{response.url}:{response.text}')
        return response

    @property
    def _uri(self):
        local_url = 'http://127.0.0.1:8000'
        url = f'https://{self.__service}-dot-{self._project}.appspot.com' if self.__service else local_url
        return f'{url}{self.__path}'

    @property
    def _headers(self):
        headers = dict()
        headers.update(self._get_authorization())
        return headers

    def _get_authorization(self) -> dict:
        return {'X-Forwarded-Authorization': f'Bearer {self.__access_token}'} if self.__access_token else {}


def timeit(method):
    def wrapper(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%r  %2.2f ms' % (method.__name__, (te - ts) * 1000))
        return result

    return wrapper
