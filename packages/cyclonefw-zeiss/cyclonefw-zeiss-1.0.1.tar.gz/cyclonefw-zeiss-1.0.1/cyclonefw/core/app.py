#
# Copyright 2018-2019 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import time
from flask import Flask, request, Response
from flask_restx import Api, Namespace
from flask_cors import CORS
from .default_config import API_TITLE, API_DESC, API_VERSION
from .utils import getLogger, logHandler, WrapperDict
import logging
import json
import requests
from werkzeug.local import LocalStack
from threading import Lock
#
# if os.getenv('USE_OPENTELEMETRY') is None or os.getenv('USE_OPENTELEMETRY') != "0":
#     from opentelemetry import trace
#     from opentelemetry.instrumentation.flask import FlaskInstrumentor
#     from opentelemetry.instrumentation.requests import RequestsInstrumentor
#     from opentelemetry.sdk.trace import TracerProvider
#     from opentelemetry.exporter.jaeger.proto import grpc
#     from opentelemetry.sdk.trace.export import (BatchSpanProcessor, ConsoleSpanExporter)
#     from opentelemetry.sdk.resources import Resource
#     from opentelemetry.exporter.zipkin.proto.http import ZipkinExporter
#
#     exporter_type = os.getenv('EXPORTER_TYPE', 'console')
#     exporter_url = os.getenv('EXPORTER_URL', '')
#     service_name = os.getenv('SERVICE_NAME', 'cyclone-algorithm-component')
#     # 定义trace
#     exporter = ConsoleSpanExporter()
#     if exporter_type.lower() == 'jaeger':
#         exporter = grpc.JaegerExporter(
#             collector_endpoint=exporter_url,
#             insecure=True,
#         )
#     elif exporter_type.lower() == 'zipkin':
#         exporter = ZipkinExporter(endpoint=exporter_url)
#
#     resource = Resource(attributes={"service.name": service_name})
#
#     trace.set_tracer_provider(TracerProvider(resource=resource))
#     trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(exporter))

# 重新定义flask日志
logging.getLogger("werkzeug").addHandler(logHandler("flask"))
# 定义默认logger
getLogger().addHandler(logHandler("component"))

#contex locals
_payload_ctx_stack = LocalStack()

class MaxAPI(Namespace):
    @property
    def payload(self):
        '''Store the input payload in the current request context'''
        return _payload_ctx_stack.top

    @payload.setter
    def payload(self, value):
        if isinstance(value, dict):
            value = WrapperDict(value)

        _payload_ctx_stack.pop()
        _payload_ctx_stack.push(value)


MAX_API = MaxAPI('model', description='Model information and inference operations')


class Context(object):
    def __init__(self):
        self.app_name = None


context = Context()


class MAXApp(object):
    def __init__(self, title=API_TITLE, desc=API_DESC, version=API_VERSION):
        self.logger = getLogger()
        context.app_name = title
        self.app = Flask(title, static_url_path='')
        self.app.logger = getLogger()
        self.metrics = {}
        # load config
        if os.path.exists("config.py"):
            self.app.config.from_object("config")

        self.api = Api(
            self.app,
            title=title,
            description=desc,
            version=version,
            validate=True
        )

        self.api.namespaces.clear()
        self.api.add_namespace(MAX_API)
        self.concurrency = int(os.getenv('MAX_CONCURRENCY', 5))
        self.remaining = self.concurrency
        self.lock = Lock()

        @self.app.route("/metrics", methods=("GET",))
        def metrics():
            """
            监控接口
            :return:
            """
            resp = Response()
            resp.headers.set('Content-Type', 'text/plain')
            content = []
            for code in self.metrics.keys():
                pathData = self.metrics[code]
                for path in pathData.keys():
                    metricsData = pathData[path]
                    content.append("{}{{{}}} {}".format(
                        "count",
                        'path="{}",code="{}"'.format(path, code),
                        metricsData["count"]
                    ))
                    content.append("{}{{{}}} {}".format(
                        "total",
                        'path="{}",code="{}"'.format(path, code),
                        metricsData["total"]
                    ))
            resp.set_data("\n".join(content))
            return resp

        self.app.before_request(self.before)
        self.app.before_request(self.enter)
        self.app.after_request(self.after)
        self.app.after_request(self.exit)
        # enable cors if flag is set
        # if os.getenv('CORS_ENABLE') == 'true' and (
        #         os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or self.app.debug is not True):
        # 默认跨域
        CORS(self.app, origins='*')
        print('NOTE: MAX Model Server is currently allowing cross-origin requests - (CORS ENABLED)')

    def add_api(self, api, route):
        MAX_API.add_resource(api, route)

    def mount_static(self, route):
        @self.app.route(route)
        def index():
            return self.app.send_static_file('index.html')

    def enter(self):
        with self.lock:
            self.remaining -= 1
        if self.remaining < 0:
            return self.app.make_response(('too many requests', 429))

    def exit(self, resp):
        with self.lock:
            self.remaining += 1
        return resp

    def after(self, resp):
        ###参数错误情况下直接返回
        if resp.status_code == 400:
            print(resp.data)
            if resp.data == b'':
                return resp

            data = eval(str(resp.data, 'utf-8'))
            if isinstance(data, dict) and 'error' in data \
                    and isinstance(data['error'], dict):
                result = {'component_status': {'code': -1, 'message': ''}}
                message = ""
                for k, v in data["errors"].items():
                    if v.endswith("is a required property"):
                        message = message + "missing parameter '" + k + "'"
                    else:
                        n = v.find(" is not of type ")
                        if n >= 0:
                            message = message + "'" + k + "'" + v[n:]
                    message += "; "
                message = message[:-2]
                result['component_status']['message'] = message

                resp.data = bytes(json.dumps(result), encoding='utf-8')
            return resp
        ###

        # resp.headers["trace-id"] = getTraceId()
        if request.path == "/metrics":
            return resp
        accessTime = request.__getattr__("access_time")
        done = int(time.time() * 1000) - accessTime
        statusCode = resp.status_code
        if statusCode not in self.metrics:
            self.metrics[statusCode] = {}
        if request.path not in self.metrics[statusCode]:
            self.metrics[statusCode][request.path] = {
                "count": 0,
                "total": 0
            }
        self.metrics[statusCode][request.path]["count"] += 1
        self.metrics[statusCode][request.path]["total"] += done
        return resp

    def before(self):
        request.__setattr__('access_time', int(time.time() * 1000))
        MAX_API.payload = request.get_json()
        '''
        batch mode，支持批处理，
        1. 判断header是否有X-batch-execute
        2. for 获取req body， 调用后端API
            a. 设置MAX_API.payload
            b. 调用flask dispatch_request分发请求
            c. 获取结果
        3. 合并结果
        4. 组装response，返回
        '''
        if request.headers.has_key("X-batch-execute"):
            self.logger.info("got header X-batch-execute, enter batch mode")
            batch_req = request.get_json()
            self.logger.info("batch request is : %s" % (batch_req))
            if not isinstance(batch_req, list):
                result = {
                    "stauts": "error",
                    "result": "wrong request body in batch mode. request body must be type of list"
                }
                response = self.app.make_response(result)
                return response

            batch_rv = []
            for req in batch_req:
                self.logger.debug("single request data is : %s" % (req))
                MAX_API.payload = req
                rv = self.app.dispatch_request()
                # 从response结果中获取data，bytes
                rv = rv.data
                rv_json = json.loads(bytes.decode(rv))
                self.logger.debug("single result data is : %s" % (rv_json))
                batch_rv.append(rv_json)
            # 根据data生成response
            self.logger.info("batch result is : %s" % (batch_rv))
            # 转换为json格式
            batch_rv = json.dumps(batch_rv)
            batch_rv = self.app.make_response(batch_rv)
            return batch_rv
        else:
            pass

    def run(self, host='0.0.0.0', port=5000):
        """
        启动服务
        :param host: host, 默认为0.0.0.0
        :param port: 端口, 默认为5000
        :return:
        """
        # if os.getenv('USE_OPENTELEMETRY') is None or os.getenv('USE_OPENTELEMETRY') != "0":
        #     FlaskInstrumentor().instrument_app(self.app)
        #     RequestsInstrumentor().instrument()

        finalPort = self.app.config["PORT"] if "PORT" in self.app.config else port
        self.app.run(host=host, port=finalPort)

    def __call__(self, environ, start_response):
        return self.app(environ, start_response)
