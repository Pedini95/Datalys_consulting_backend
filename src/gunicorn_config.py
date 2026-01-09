"""
Gunicorn configuration file for Datalys Consulting API
Production-ready WSGI server configuration
"""
import os
import multiprocessing

# Server Socket
# Use TCP port for Docker networking compatibility
bind = f"0.0.0.0:{os.getenv('PORT', '8082')}"


backlog = 2048

##### Worker Processes
# Utiliser 2 workers par défaut (optimisé pour VPS) au lieu de cpu_count() * 2 + 1
# Pour éviter la saturation CPU sur des serveurs à faible capacité
workers = int(os.getenv('GUNICORN_WORKERS', 2))
worker_class = 'gevent'  # Async workers for better concurrency
worker_connections = 1000
max_requests = 1000  # Restart workers after this many requests (prevents memory leaks)
max_requests_jitter = 50  # Add randomness to prevent all workers restarting at once
timeout = 120  # 2 minutes timeout (important for long-running requests)
graceful_timeout = 30  # Give workers 30s to finish after receiving SIGTERM
keepalive = 5  # Keep connections alive for 5 seconds

# Process Naming
proc_name = 'datalys-api'

# Logging
accesslog = '-'  # Log to stdout
errorlog = '-'   # Log to stderr
loglevel = os.getenv('LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# Server Mechanics
daemon = False  # Don't daemonize (Docker handles this)
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (disabled by default, use nginx/traefik for SSL termination)
keyfile = None
certfile = None

# Server Hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("Gunicorn master process starting...")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    server.log.info("Reloading Gunicorn...")

def when_ready(server):
    """Called just after the server is started."""
    server.log.info(f"Gunicorn ready. Workers: {workers}, Worker class: {worker_class}")

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    worker.log.info(f"Worker {worker.pid} received INT or QUIT signal")

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info(f"Worker spawned (pid: {worker.pid})")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    pass

def pre_exec(server):
    """Called just before a new master process is forked."""
    server.log.info("Forking new master process...")

def worker_exit(server, worker):
    """Called just after a worker has been exited."""
    server.log.info(f"Worker {worker.pid} exited")
