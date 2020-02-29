"""
提供fabric客户端
"""
from functools import wraps
from fabric import Connection


def create_connect(*,
                   host: str,
                   port: int,
                   user: str,
                   password: str
                   ):
    connect_params = {
        "host": host,
        "user": user,
        "port": port,
        "connect_kwargs": {"password": password}
    }
    return Connection(**connect_params)


def is_cmd_success(res):
    if res.exited == 0 and res.ok:
        return True
    return False


def run_bash_cmd(fun):
    @wraps(fun)
    def wrapper(*args, **kwargs):
        try:
            res = fun(*args, **kwargs)
            if is_cmd_success(res):
                return res
            if hasattr(res, "cmd"):
                raise RuntimeError(f"{res.cmd} faild")
            elif hasattr(res, "command"):
                raise RuntimeError(f"{res.command} faild error: {res.stderr}")
        except RuntimeError as e:
            raise
        except Exception:
            """
            捕获所有的执行失败之类的异常
            """
            raise
    return wrapper
