#!venv/bin/python

from app import create_app
import socket

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    s.close()
except OSError:
    local_ip = '127.0.0.1'
app = create_app()

app.run(host=local_ip, port=8080, debug=True)
