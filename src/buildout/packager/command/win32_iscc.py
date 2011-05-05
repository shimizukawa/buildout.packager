import _winreg as reg
import os

BASE_KEY = r'SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall'

def get_app_key():
    pk = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, BASE_KEY)
    info = reg.QueryInfoKey(pk)

    for i in range(info[0]):
        name = reg.EnumKey(pk, i)
        if 'Inno Setup' in name:
            return name
    else:
        # raise RuntimeError("Can't find Inno Setup")
        return None


def get_app_path(app_key):
    pk = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, '\\'.join([BASE_KEY, app_key]))
    info = reg.QueryInfoKey(pk)
    for i in range(info[1]):
        name, value, vtype = reg.EnumValue(pk, i)
        if 'InstallLocation' == name:
            return value
    else:
        # raise RuntimeError("Can't find Inno Setup application path")
        return None


def get_iscc_path(app_path):
    path = os.path.join(app_path, 'iscc.exe')
    if os.path.exists(path):
        return path
    else:
        # raise RuntimeError("Can't find Inno Setup iscc.exe")
        return None


def main():
    app_key = get_app_key()
    app_path = get_app_path(app_key)
    iscc_path = get_iscc_path(app_path)
    return iscc_path


if __name__ == '__main__':
    iscc_path = main()
    print iscc_path
    w,r,e = os.popen3('"%s"' % iscc_path)
    print r.read()

