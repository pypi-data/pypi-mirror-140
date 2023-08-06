import time
from flask import Flask, jsonify, request, Response
from threading import Thread
from werkzeug.serving import make_server
import logging.handlers


class RestServer:
    def __init__(self, host="0.0.0.0", port=443):
        self.port = port
        self.host = host
        self.base_url = "https://{}:{}".format(self.host, self.port)
        self.app = Flask(__name__)
        self.app.url_map.strict_slashes = False
        self.app.config.update(TESTING=True, TRAP_HTTP_EXCEPTIONS=True)
        self.server = make_server(self.host, self.port, self.app, ssl_context='adhoc')
        self.thread = None
        self.error_handler_callback = None

        self.log = logging.getLogger(__name__)
        logging.basicConfig(level=logging.DEBUG,
                            format='[%(asctime)s - %(levelname)s]: %(message)s',
                            datefmt='%d.%m.%Y %H:%M:%S',
                            filename="{}.log".format(__file__),
                            force=True)

        # redirect logger to stdout
        # self.log.addHandler(logging.StreamHandler())

        @self.app.after_request
        def after_request(response) -> Response:
            self.log.debug("---------- REQUEST HANDLER ----------")
            self.log.debug("REQUEST DATA \n"
                           "url: {} \n"
                           "method: {} \n"
                           "headers: {} \n"
                           "payload: {}\n"
                           .format(request.url, request.method, request.headers, request.get_data()))
            self.log.debug("RESPONSE DATA \n"
                           "code: {} \n"
                           "headers: {} \n"
                           "payload: {} \n"
                           .format(response.status_code, response.headers, response.data.decode()))
            self.log.debug("-------- REQUEST HANDLER DONE --------")
            return response

        @self.app.route('/alive', methods=['GET'])
        def alive():
            self.log.debug("Got 'is alive' request")
            return "True"

        @self.app.errorhandler(Exception)
        def add_error_handler(error):
            if self.error_handler_callback is None:
                raise error
            return self.error_handler_callback

    def _validate_server_alive(self):
        self.log.debug("Checking if server is alive")
        server_is_alive = False
        error_string = "Timed out all retries"

        for _ in range(5):
            try:
                self.log.debug("Is alive check {}".format(_))
                response = self.get_test_client().get('/alive')
                server_is_alive = response.data.decode()
                break
            except Exception as ex:
                error_string = ex
                time.sleep(0.5)

        if not server_is_alive:
            raise Exception('Failed to start and connect to mock server. error_string: {}'.format(error_string))

    def start(self):
        self.log.debug("Starting rest server")
        self.thread = Thread(target=self.server.serve_forever)
        self.thread.start()
        self._validate_server_alive()
        self.log.debug("Rest server up & running")

    def stop(self):
        self.server.shutdown()
        self.thread.join()

    def get_test_client(self):
        with self.server.app.test_client() as client:
            with self.server.app.app_context():
                return client

    def get_request(self) -> request:
        return request

    def create_json_response(self, serializable) -> Response:
        try:
            return jsonify(serializable)
        except Exception as ex:
            print("failed to create response: %s", ex)
            raise ex

    def create_xml_response(self, body, content_type='application/x-www-form-urlencoded') -> Response:
        response = Response(body)
        response.headers['Content-Type'] = content_type
        return response

    def add_callback_response(self, url, callback, methods=('GET',)):
        self.app.add_url_rule(url, endpoint=url, view_func=callback, methods=methods)

    def add_jsonify_response(self, url, serializable_object, methods=('GET',)):
        self.add_callback_response(url, lambda: jsonify(serializable_object), methods=methods)

    def set_error_handler_callback(self, error_string, http_code):
        self.error_handler_callback = error_string, http_code
