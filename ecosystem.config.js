module.exports = {
  apps: [
    {
      name: 'atlas-api',
      script: 'bin/api_gateway.py',
      interpreter: 'python3',
      cwd: '.',
      env: {
        PORT: 8000
      },
      out_file: 'logs/api_gateway.log',
      error_file: 'logs/api_gateway.log',
      log_date_format: 'YYYY-MM-DD HH:mm Z'
    },
    {
      name: 'atlas-tg-gateway',
      script: 'bin/tg_gateway.py',
      interpreter: 'python3',
      cwd: '.',
      out_file: 'logs/tg_gateway.log',
      error_file: 'logs/tg_gateway.log',
      log_date_format: 'YYYY-MM-DD HH:mm Z'
    },
    {
      name: 'atlas-heartbeat',
      script: 'bin/atlas_core.py',
      args: 'heartbeat',
      interpreter: 'python3',
      cwd: '.',
      out_file: 'logs/heartbeat.log',
      error_file: 'logs/heartbeat.log',
      log_date_format: 'YYYY-MM-DD HH:mm Z'
    }
  ]
};
