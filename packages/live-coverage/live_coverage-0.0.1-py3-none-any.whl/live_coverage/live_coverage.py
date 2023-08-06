import hashlib
import runpy
import sys
import time
import webbrowser
from http.server import SimpleHTTPRequestHandler
from pathlib import Path
from socketserver import TCPServer
from threading import Thread
from multiprocessing import Process

from coverage import Coverage


class RequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="htmlcov", **kwargs)

    def log_message(self, *_):
        pass


def start_server():
    def start():
        time.sleep(1)
        with TCPServer(("127.0.0.1", 0), RequestHandler) as httpd:
            port = httpd.socket.getsockname()[1]
            webbrowser.open(f"http://localhost:{port}/")
            httpd.serve_forever()

    process = Process(target=start)
    process.start()
    return process


def update_script(data_hash):
    file = Path("htmlcov/coverage_html.js")
    content = file.read_text()
    content = f"""const HASH = "{data_hash}";\n\n""" + content
    content += """
    setInterval(() => {
        fetch(location.origin + "/coverage_html.js").then(r => r.text()).then(r => {
            const new_hash = r.split('"')[1];
            if (new_hash !== HASH) location.reload();
        });
    }, 1000);
    """
    file.write_text(content)


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <file>")
        sys.exit(1)

    file = sys.argv[1]
    sys.path.insert(0, str(Path(file).parent.absolute()))

    cov = Coverage(omit=[__file__])

    def update_coverage():
        while cov._started:  # noqa
            time.sleep(1)
            cov.save()
            cov.html_report()
            update_script(hashlib.sha256(cov.get_data().dumps()).hexdigest())

    cov.start()
    thread = Thread(target=update_coverage)
    thread.start()

    server = start_server()

    try:
        runpy.run_path(file, {}, "__main__")
    except:
        pass

    cov.stop()
    thread.join()

    cov.save()
    cov.html_report()
    cov.report()

    webbrowser.open("htmlcov/index.html")

    time.sleep(3)

    server.kill()
