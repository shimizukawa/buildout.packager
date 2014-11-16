import os

try:
    import _winreg as reg
except:
    import winreg as reg

import logging

logger = logging.getLogger(__name__)

BASE_KEY = r'SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall'


def get_app_key(key_name):
    pk = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, BASE_KEY)
    info = reg.QueryInfoKey(pk)

    for i in range(info[0]):
        name = reg.EnumKey(pk, i)
        if key_name in name:
            return name
    else:
        return None


def get_app_path(app_key):
    pk = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, '\\'.join([BASE_KEY, app_key]))
    info = reg.QueryInfoKey(pk)
    for i in range(info[1]):
        name, value, vtype = reg.EnumValue(pk, i)
        if 'InstallLocation' == name:
            return value
    else:
        return None


def get_prog_path(app_path, program_name):
    path = os.path.join(app_path, program_name)
    if os.path.exists(path):
        return path
    else:
        return None


def main(key_name, program_name):
    app_key = get_app_key(key_name)
    app_path = get_app_path(app_key)
    prog_path = get_prog_path(app_path, program_name)
    return prog_path


if __name__ == '__main__':
    path = main('NSIS', 'makensis.exe')
    logger.info(path)
    w, r, e = os.popen3('"%s"' % path)
    logger.info(r.read())

