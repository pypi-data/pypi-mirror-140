# Modules
import os
import random
from .kthread import KThread
from flask import Flask, send_from_directory
from jinja2 import Environment, FileSystemLoader

from .webpage import load_page

# Flask app maker
def make_app(source_dir: str, use_jinja: bool = True) -> Flask:
    source_dir = os.path.abspath(source_dir)

    # Create flask app
    app = Flask("Nitrogen")
    env = Environment(loader = FileSystemLoader(source_dir))

    # Primary route
    @app.route("/<path:path>")
    def get_file(path: str) -> None:
        if path.split(".")[-1] in ["html", "jinja"]:
            return env.get_template(path).render()

        return send_from_directory(source_dir, path, conditional = True)

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

        # Create flask app
        self.app = make_app(source_dir, use_jinja)

    def generate_port(self) -> int:
        return random.randint(10000, 65535)

    def start(self, start_location: str = "index.html") -> None:
        port = self.generate_port()
        thread = KThread(target = self.app.run, kwargs = {"host": "localhost", "port": port})
        thread.start()
        try:
            load_page(f"http://localhost:{port}/{start_location}")

        except Exception as err:
            self.stop()
            raise err

        thread.terminate()
