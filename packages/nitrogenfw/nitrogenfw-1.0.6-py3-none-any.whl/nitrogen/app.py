# Modules
import os
import json
import random
from types import FunctionType
from base64 import b64encode, b64decode
from jinja2 import Environment, FileSystemLoader
from flask import Flask, abort, request, send_from_directory

from .kthread import KThread
from .webpage import load_page

# Flask app maker
def make_app(
    nitrogen,
    source_dir: str,
    use_jinja: bool = True,
    env_dict: dict = {}
) -> Flask:
    source_dir = os.path.abspath(source_dir)

    # Create flask app
    app = Flask("Nitrogen", template_folder = source_dir)
    env = Environment(loader = FileSystemLoader(source_dir))

    # Primary routes
    @app.route("/_/fncallback", methods = ["GET"])
    def fncallback() -> None:
        fn = request.args.get("fn", "")
        if fn not in nitrogen.functions:
            return abort(404)

        try:
            args = json.loads(b64decode(request.args.get("args")))

        except Exception:
            args = []

        return nitrogen.functions[fn](*args) or "200 OK"

    @app.route("/<path:path>")
    def get_file(path: str) -> None:
        if path.split(".")[-1] in ["html", "jinja"] and use_jinja:
            return env.get_template(path).render(env_dict)

        return send_from_directory(source_dir, path, conditional = True)

    @app.context_processor
    def send_env() -> dict:
        return env_dict

    return app

# Nitrogen class
class Nitrogen(object):
    def __init__(
        self,
        source_dir: str = "src",
        use_jinja: bool = True
    ) -> None:
        self.source_dir = source_dir
        self.use_jinja = use_jinja
        self.functions = {}

        # Create flask app
        self.app = make_app(self, source_dir, use_jinja, {
            "nitrogen": self
        })

    def call(self, fn: str, *args) -> str:
        return f"fetch('/_/fncallback?fn={fn}&args={b64encode(json.dumps(args).encode()).decode()}')"

    def route(self, rule: str, **options) -> FunctionType:
        return self.app.route(rule, **options)

    def generate_port(self) -> int:
        return random.randint(10000, 65535)

    def start(self, start_location: str = "index.html", fullscreen: bool = False) -> None:
        port = self.generate_port()
        thread = KThread(target = self.app.run, kwargs = {"host": "localhost", "port": port})
        thread.start()
        try:
            load_page(f"http://localhost:{port}/{start_location}", fullscreen)

        except Exception as err:
            self.stop()
            raise err

        thread.terminate()

    def function(self, name: str) -> FunctionType:
        def internal_cb(func: FunctionType):
            self.functions[name] = func

        return internal_cb
