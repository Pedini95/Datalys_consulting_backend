module.exports = {
  apps: [{
    name: 'datalys-api',
    script: 'src/run.py',
    cwd: '/home/datalys/Datalys_consulting_backend',
    interpreter: '/home/datalys/Datalys_consulting_backend/venv/bin/python',
    env: {
      FLASK_ENV: 'production',
      PYTHONPATH: '/home/datalys/Datalys_consulting_backend/src',
      ENV: 'production'
    },
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    log_file: '/home/datalys/Datalys_consulting_backend/logs/combined.log',
    out_file: '/home/datalys/Datalys_consulting_backend/logs/out.log',
    error_file: '/home/datalys/Datalys_consulting_backend/logs/error.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    merge_logs: true,
    time: true
  }]
}; 