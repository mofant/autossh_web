
SUPERVISOR_CONFIG = "/etc/supervisor/supervisord.conf"
SUPERVISOR_TASK_CONFIG = "/etc/supervisor/conf.d/"
SUPERVISOR_START = "supervisord -c /etc/supervisor/supervisord.conf"

SUPERVISORCTL_PREFIX = "supervisorctl -c /etc/supervisor/supervisord.conf "
SUPERVISORCTL_RELOAD = SUPERVISORCTL_PREFIX + "reload"
SUPERVISORCTL_START = SUPERVISORCTL_PREFIX + "start "
SUPERVISORCTL_STOP = SUPERVISORCTL_PREFIX + "stop "
SUPERVISORCTL_STATUS = SUPERVISORCTL_PREFIX + "status "
