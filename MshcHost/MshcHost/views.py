from flask import Response, send_file
from MshcHost import app
from os import getcwd
from os.path import join
from MshcHost import cache as path
from MshcHost.Transformations import HrefTransformation
from MshcHost.index import index

current_dir = getcwd()
transformations = [HrefTransformation(index)]


def _get_file_from_filecache(filename: str) -> str:
    return join(path, filename)


def _file_contents(path: str) -> str:
    with open(path, "rb") as f:
        text = f.read().decode("utf8", "ignore")
        return text


def _perform_transforms(contents: str) -> str:
    for transform in transformations:
        contents = transform.Transform(contents)
    return contents


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def main(path: str) -> str:
    if path == "":
        path = "topic1.html"

    if path.endswith(".html"):
        return _perform_transforms(
            _file_contents(
                _get_file_from_filecache(path)
            ))
    elif path.endswith(".css"):
        content = _file_contents(_get_file_from_filecache(path))
        return Response(content, mimetype="text/css")
    else:
        return send_file(_get_file_from_filecache(path))
