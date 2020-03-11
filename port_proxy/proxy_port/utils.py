import re
import uuid
import os
from .client import is_cmd_success
from invoke.exceptions import UnexpectedExit

port_listing_patterm_pre = ".*?(?:[0-9]{1,3}\.){3}[0-9]{1,3}:"


def is_port_using(conn, port):
    check_port_cmd = f"netstat -nltp | grep {port}"
    try:
        res = conn.sudo(
            check_port_cmd, password=conn.connect_kwargs['password'])
        if not is_cmd_success(res):
            return False
        listing_port_strs = res.stdout.split("\n")
        for line in listing_port_strs:
            match = re.match(f"{port_listing_patterm_pre}({port})", line)
            if match and match.groups()[0] == str(port):
                return True
        return False
    except UnexpectedExit:
        return False


def chmod_x_to_file(conn, file_path):
    """
    给文件赋予可执行权限
    """
    cmd = f"chmod +x {file_path}"
    res = conn.sudo(cmd, password=conn.connect_kwargs['password'], warn=True)
    return is_cmd_success(res)


def kill_pid(conn, pid):
    """
    利用sudo kill
    """
    kill_cmd = f"kill -9 {pid}"
    res = conn.sudo(
        kill_cmd, password=conn.connect_kwargs['password'], warn=True)
    if not is_cmd_success(res) and "No such process" in res.stderr:
        raise ValueError(f"not pid {pid} is running")
    return is_cmd_success(res)


def upload_file(conn, source_file, des_file, replace=False, root=True):
    """
    使用sudo上传文件 ，确保文件夹存在。
    为了确保文件上传，先上传到tmp目录，然后在迁移到目标路径
    参数：
        conn: fabric connection
        source_file: 源文件路径
        des_file: 上传后的文件路径
        replace: 是否覆盖
        root: 是否使用sudo上传
    """
    try:
        temp_filename = str(uuid.uuid1())
        conn.put(source_file, f'/tmp/{temp_filename}')
        if not replace:
            cmd = f"cp -i /tmp/{temp_filename} {des_file}"
            if root:
                res = conn.sudo('''awk 'BEGIN { cmd="''' + cmd + '''"; print "n" |cmd; }' ''',
                                password=conn.connect_kwargs['password'], warn=True)
            else:
                res = conn.run(cmd, warn=True)
        else:
            if root:
                res = conn.sudo(
                    f"mv -f /tmp/{temp_filename} {des_file}", password=conn.connect_kwargs['password'])
            else:
                res = conn.run(f"mv -f /tmp/{temp_filename} {des_file}")
        return is_cmd_success(res)
    except Exception as e:
        raise RuntimeError("cannot upload cofnig file")


def install_dependence_software(conn, system_type="ubuntu", install_supervisor=False):
    """
    安装环境以来的autossh和except 以及supervisor
    默认安装autossh 和except
    """
    system_type = system_type.lower()
    if system_type == "ubuntu":
        if install_supervisor:
            install_cmd = "apt-get -y install autossh expect supervisor"
        else:
            install_cmd = "apt-get -y install autossh expect"
    else:
        if install_supervisor:
            install_cmd = "yum -y install autossh expect supervisor"
        else:
            install_cmd = "yum -y install autossh expect"
    res = conn.sudo(
        install_cmd, password=conn.connect_kwargs['password'], warn=True)
    return is_cmd_success(res)
