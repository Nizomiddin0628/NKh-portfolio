"""Gunicorn settings, picked up automatically from the project directory.

Threads matter: an assistant answer streams for up to ~90 s and would block
a plain sync worker for that long. With threads, one worker still serves
other visitors while an answer is being written. Explicit command-line
flags in the systemd unit take precedence over these values.
"""
worker_class = "gthread"
workers = 1
threads = 6
timeout = 120
keepalive = 5
graceful_timeout = 30
