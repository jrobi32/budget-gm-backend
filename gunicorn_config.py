import multiprocessing
import os

# Server socket
bind = "0.0.0.0:" + str(os.getenv("PORT", "10000"))
backlog = 2048

# Worker processes
workers = 2  # Reduce worker count to prevent memory issues
worker_class = 'gevent'  # Use gevent for async support
worker_connections = 100
timeout = 300  # Increase timeout to 300 seconds
keepalive = 2

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Process naming
proc_name = 'budget-gm-backend'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL
keyfile = None
certfile = None

# Memory management
max_requests = 100
max_requests_jitter = 10
preload_app = True  # Preload app to share memory between workers
max_worker_lifetime = 3600  # Restart workers every hour
worker_tmp_dir = "/dev/shm"  # Use shared memory for temporary files

# SSL
keyfile = None
certfile = None

# Memory management
max_requests = 1000
max_requests_jitter = 50 