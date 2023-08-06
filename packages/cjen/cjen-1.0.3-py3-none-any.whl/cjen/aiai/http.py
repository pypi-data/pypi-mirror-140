import os
from enum import unique, Enum

import requests
import yaml
from requests_toolbelt import MultipartEncoder

from cjen.mama.operate.json import factory
from cjen.bigtangerine import BigTangerine
from cjen.commons import _get_method_params
from cjen.exceptions import _check_uri, NetWorkErr, _check_instance


def _multipart_form(func):
    def __inner__(ins: BigTangerine, *args, **kwargs):
        data_form = kwargs.get("data")
        files = {}
        others = {}
        for k, v in data_form.items():
            if os.path.exists(v):
                files[k] = v
            else:
                others[k] = v
        if not files: raise Exception("there is no file!")
        for k, v in files.items():
            with open(v, 'rb') as f:
                *rest, postfix = f.name.split(".")
                files[k] = (os.path.basename(f.name), f.read(), _file_type(file_postfix=f".{postfix}"))

        kwargs["form_data"] = MultipartEncoder(fields={**files, **others})
        ins.headers["Content-Type"] = kwargs["form_data"].content_type
        return func(ins, *args, **kwargs)

    return __inner__


def _file_type(*, file_postfix):
    with open(os.path.join(os.path.dirname(__file__), "file-content-type.yaml"), "r") as f:
        content_type = yaml.load(f.read(), Loader=yaml.FullLoader).get("ContentType")
        if content_type.get(file_postfix):
            return content_type.get(file_postfix)
    raise Exception(f"{file_postfix} can not support !")


@unique
class ContentType(Enum):
    JSON = "json"
    FILE_STREAM = "stream"


def _response(func):
    def __inner__(ins: BigTangerine, *args, **kwargs):

        if kwargs.get("resp").status_code == 200:
            if "application/json" in kwargs.get("resp").headers.get("Content-Type"):
                kwargs["response_content"] = kwargs.get("resp")
                kwargs["resp"] = kwargs.get("resp").json() if kwargs.get("resp").content else None
                return func(ins, *args, **kwargs)
            kwargs["resp"] = kwargs.get("resp").content
            return func(ins, *args, **kwargs)
        else:
            raise NetWorkErr(f'{kwargs.get("url")} {kwargs.get("resp").status_code}')

    return __inner__


def _url(*, uri: str):
    def __wrapper__(func):
        def __inner__(ins: BigTangerine, *args, **kwargs):
            path_variable = kwargs.get("path_variable")
            kwargs["url"] = "/".join([ins.base_url, uri])
            if path_variable:
                kwargs["url"] = kwargs["url"].format(**path_variable)
            return func(ins, *args, **kwargs)

        return __inner__

    return __wrapper__


def base_url(*, uri: str):
    def __wrapper__(func):
        def __inner__(ins: BigTangerine, *args, **kwargs):
            ins.__setattr__("base_url", uri)
            return func(ins, *args, **kwargs)

        return __inner__

    return __wrapper__


def _delete(func):
    @_http_headers
    @_http_json(method=requests.delete)
    @_http_default(method=requests.delete)
    def __inner__(ins: BigTangerine, *args, **kwargs):
        return func(ins, *args, **kwargs)

    return __inner__


def _http_headers(func):
    def __inner__(ins: BigTangerine, *args, **kwargs):
        kwargs["headers"] = {**ins.headers, **kwargs.get("headers")} if kwargs.get("headers") else ins.headers
        return func(ins, *args, **kwargs)

    return __inner__


def _resp_is_not_none(**kwargs): return kwargs.get("resp") is None


def _have_content_type(**kwargs): return kwargs["headers"].get("Content-Type") is not None


def _is_json(**kwargs): return "json" in kwargs["headers"].get("Content-Type")


def _is_upload(**kwargs): return "multipart/form-data" in kwargs["headers"].get("Content-Type")


def _http_json(*, method):
    def __wrapper__(func):
        def __inner__(ins: BigTangerine, *args, **kwargs):
            if _resp_is_not_none(**kwargs) and _have_content_type(**kwargs) and _is_json(**kwargs):
                kwargs["resp"] = method(url=kwargs["url"], headers=kwargs["headers"], json=kwargs.get("data"))
            return func(ins, *args, **kwargs)

        return __inner__

    return __wrapper__


def _http_file(*, method):
    def __wrapper__(func):
        def __inner__(ins: BigTangerine, *args, **kwargs):
            if _resp_is_not_none(**kwargs) and _have_content_type(**kwargs) and _is_upload(**kwargs):
                kwargs["resp"] = method(url=kwargs["url"], headers=kwargs["headers"], data=kwargs.get("form_data"))
            return func(ins, *args, **kwargs)

        return __inner__

    return __wrapper__


def _http_default(*, method):
    def __wrapper__(func):
        def __inner__(ins: BigTangerine, *args, **kwargs):
            if _resp_is_not_none(**kwargs):
                kwargs["resp"] = method(url=kwargs["url"], headers=kwargs["headers"], data=kwargs.get("data"))
            return func(ins, *args, **kwargs)

        return __inner__

    return __wrapper__


def _get(func):
    def __inner__(ins: BigTangerine, *args, **kwargs):
        headers = {**ins.headers, **kwargs.get("headers")} if kwargs.get("headers") else ins.headers
        kwargs["resp"] = requests.get(url=kwargs["url"], headers=headers, params=kwargs.get("params"))
        return func(ins, *args, **kwargs)

    return __inner__


def _post(func):
    @_http_headers
    @_http_json(method=requests.post)
    @_http_file(method=requests.post)
    @_http_default(method=requests.post)
    def __inner__(ins: BigTangerine, *args, **kwargs):
        return func(ins, *args, **kwargs)

    return __inner__


def _put(func):
    @_http_headers
    @_http_json(method=requests.put)
    @_http_default(method=requests.put)
    def __inner__(ins: BigTangerine, *args, **kwargs):
        return func(ins, *args, **kwargs)

    return __inner__


def get_mapping(*, uri: str, json_clazz=None):
    """
    使用范围：BigTangerine 或其 子类对象

    位置：装饰函数的上层装饰器. 如果有使用Header装饰器，在Header装饰器之后，如果没有 则是顶层装饰器

    发送 GET 请求，并返回结果

    :param json_clazz: 如果期望返回数据直接生成MetaJson, 则指定该生成的类型
    :param uri:
    :return:
    """

    def __wrapper__(func):
        @_get_method_params(method=func)
        @_check_instance(decorator="http.get_mapping", expect=BigTangerine)
        @_check_uri(uri=uri)
        @_url(uri=uri)
        @_get
        @_response
        @factory(clazz=json_clazz)
        def __inner__(ins: BigTangerine, *args, **kwargs):
            func(ins, *args, **kwargs)
            return kwargs.get("resp")

        return __inner__

    return __wrapper__


def post_mapping(*, uri: str, json_clazz=None):
    """
    使用范围：BigTangerine 或其 子类对象

    位置：装饰函数的上层装饰器，如果有使用Header装饰器，在Header装饰器之后，如果没有 则是顶层装饰器

    发送 Post 请求，并返回结果

    :param json_clazz:
    :param uri:
    :return:
    """

    def __wrapper__(func):
        @_get_method_params(method=func)
        @_check_instance(decorator="http.post_mapping", expect=BigTangerine)
        @_check_uri(uri=uri)
        @_url(uri=uri)
        @_post
        @_response
        @factory(clazz=json_clazz)
        def __inner__(ins: BigTangerine, *args, **kwargs):
            func(ins, *args, **kwargs)
            return kwargs.get("resp")

        return __inner__

    return __wrapper__


def put_mapping(*, uri: str, json_clazz=None):
    """
    使用范围：BigTangerine 或其 子类对象

    位置：装饰函数的上层装饰器，如果有使用Header装饰器，在Header装饰器之后，如果没有 则是顶层装饰器

    发送 PUT 请求，并返回结果

    :param json_clazz:
    :param uri:
    :return:
    """

    def __wrapper__(func):
        @_get_method_params(method=func)
        @_check_instance(decorator="http.put_mapping", expect=BigTangerine)
        @_check_uri(uri=uri)
        @_url(uri=uri)
        @_put
        @_response
        @factory(clazz=json_clazz)
        def __inner__(ins: BigTangerine, *args, **kwargs):
            func(ins, *args, **kwargs)
            return kwargs.get("resp")

        return __inner__

    return __wrapper__


def upload_mapping(*, uri: str, json_clazz=None):
    """
    使用范围：BigTangerine 或其 子类对象

    位置：装饰函数的上层装饰器，如果有使用Header装饰器，在Header装饰器之后，如果没有 则是顶层装饰器

    发送 上传文件 请求，并返回结果

    :param json_clazz:
    :param uri:
    :return:
    """

    def __wrapper__(func):
        @_get_method_params(method=func)
        @_check_instance(decorator="http.upload_mapping", expect=BigTangerine)
        @_check_uri(uri=uri)
        @_url(uri=uri)
        @_multipart_form
        @_post
        @_response
        @factory(clazz=json_clazz)
        def __inner__(ins: BigTangerine, *args, **kwargs):
            func(ins, *args, **kwargs)
            return kwargs.get("resp")

        return __inner__

    return __wrapper__


def delete_mapping(*, uri: str, json_clazz=None):
    """
    使用范围：BigTangerine 或其 子类对象

    位置：位置：装饰函数的上层装饰器，如果有使用Header装饰器，在Header装饰器之后，如果没有 则是顶层装饰器

    发送 delete 请求，并返回结果

    :param json_clazz:
    :param uri:
    :return:
    """

    def __wrapper__(func):
        @_get_method_params(method=func)
        @_check_instance(decorator="http.delete_mapping", expect=BigTangerine)
        @_check_uri(uri=uri)
        @_url(uri=uri)
        @_delete
        @_response
        @factory(clazz=json_clazz)
        def __inner__(ins: BigTangerine, *args, **kwargs):
            func(ins, *args, **kwargs)
            return kwargs.get("resp")

        return __inner__

    return __wrapper__
