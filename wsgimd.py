""" WSGI application that converts markdown file to HTML """

from functools import partial
from io import BytesIO
from pathlib import Path
from markdown import markdownFromFile

ROOT = Path("/home/julien/Public")
TEMPLATE = b"""\
<!DOCTYPE html5>
<head>
    <meta charset=utf-8>
    <style>
        body { font-family: sans-serif; }
        pre {
            background-color: #f3f3f3;
            width: 80ch;
        }
        table {
            border-collapse: collapse;
        }
        tbody tr:nth-child(odd) {
            background-color: #f2f2f2;
        }
        tr, td, th {
            padding: 0.5rem;
            border: 1px solid black;
        }
        blockquote {
            margin: 0;
            border-left: 5px solid #ddd;
            padding-left: calc(1em - 5px);
        }
    </style>
</head>
<body>
%(body)s
</body>
</html>
"""

def locate(path):
    if path.startswith('/'):
        path = path[1:]
    path = path.replace('%20', ' ')
    path = ROOT.joinpath(path).resolve()
    if all([
        str(path).startswith(str(ROOT)),
        path.is_file(),
        path.suffix == '.md'
    ]):
        return path

def application(environ, start_response):
    if environ['REQUEST_METHOD'] != 'GET':
        start_response("405 Method not allowed", [])
        return []

    path = locate(environ['PATH_INFO'])
    if not path:
        start_response("404 Not found", [])
        return []

    if 'text/html' in environ.get('HTTP_ACCEPT', ''):
        buffer = BytesIO()
        markdownFromFile(
            input=str(path),
            output=buffer,
            output_format='html5',
            encoding='utf-8'
        )

        start_response("200 OK", [
            ('Content-Type', 'text/html')
        ])
        return [TEMPLATE % {b'body': buffer.getvalue()}]

    start_response("200 OK", [
        ('Content-Type', 'text/text'),
        ('Content-Length', str(path.stat().st_size))
    ])
    return [path.read_bytes()]
