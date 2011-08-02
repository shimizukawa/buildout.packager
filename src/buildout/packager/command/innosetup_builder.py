# -*- coding: utf-8 -*-
import os
import sys
import subprocess
from distutils.util import get_platform
from distutils import log
from utils import get_postfix_name, to_filename


MAIN_SCRIPT = r"""
; WARNING: This script has been created by buildout.packager.
; Changes to this script will be overwritten the next time bulidout.packager is run!
[Setup]
AppName=%(self_name)s
AppVerName=%(self_name)s %(self_version)s
DefaultDirName={pf}\%(self_install_dir)s
DefaultGroupName=%(self_name)s
AllowUNCPath=no
%(app_publisher)s
%(app_publisher_url)s
%(app_support_url)s
OutputBaseFilename=%(self_installer_name)s
OutputDir=%(self_dist_dir)s
PrivilegesRequired=admin

[Languages]
Name: jp; MessagesFile: "compiler:Languages\Japanese.isl"

[Files]
%(data_files)s

%(sys_files)s

[Icons]
%(icons)s
Name: "{group}\Uninstall %(self_name)s"; Filename: "{uninstallexe}"
Name: "{group}\versions"; Filename: "{app}\versions.txt"

[Registry]
Root: HKCU; Subkey: "Software\%(self_author_name)s"; Flags: uninsdeletekeyifempty
Root: HKCU; Subkey: "Software\%(self_author_name)s\%(self_name)s"; Flags: uninsdeletekeyifempty
Root: HKCU; Subkey: "Software\%(self_author_name)s\%(self_name)s\%(self_version)s"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\%(self_author_name)s"; Flags: uninsdeletekeyifempty
Root: HKLM; Subkey: "Software\%(self_author_name)s\%(self_name)s"; Flags: uninsdeletekeyifempty
Root: HKLM; Subkey: "Software\%(self_author_name)s\%(self_name)s\%(self_version)s"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\%(self_author_name)s\%(self_name)s\%(self_version)s"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"
Root: HKLM; Subkey: "Software\%(self_author_name)s\%(self_name)s\%(self_version)s"; ValueType: string; ValueName: "Revision"; ValueData: "%(self_version)s"

[UninstallDelete]
Type: filesandordirs; Name: "{app}\parts";
Type: filesandordirs; Name: "{app}\eggs";
Type: filesandordirs; Name: "{app}\bin";
Type: filesandordirs; Name: "{app}\develop-eggs";
Type: filesandordirs; Name: "{app}\.installed.cfg";
Type: filesandordirs; Name: "{app}\versions.txt";


[Code]
var
  FinishedInstall: Boolean;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
  Python: String;
  PyScript: String;
begin
  if CurStep = ssPostInstall then begin
    Python := ExpandConstant('{app}\python\python.exe');
    PyScript := ExpandConstant('"{app}\packages\postinstall.py"');

    if FileExists(Python) then begin
      if Exec(Python , PyScript, ExpandConstant('{pf}\'), SW_SHOW, ewWaitUntilTerminated, ResultCode) then
        FinishedInstall := True;
    end else
      if ShellExec('', 'python', PyScript, ExpandConstant('{pf}\'), SW_SHOW, ewWaitUntilTerminated, ResultCode) then
        FinishedInstall := True;

    if not FinishedInstall then
      MsgBox('PostInstall:' #13#13 'Execution of python.exe failed. ' + SysErrorMessage(ResultCode) + '.', mbError, MB_OK)
  end;
end;
"""


class InnoScript(object):
    def __init__(self,
                 name,
                 installer_name,
                 install_dir,
                 src_dir,
                 dist_dir,
                 data_files = [],
                 sys_files = [],
                 exe_files = [],
                 version = "0.0.1",
                 author_name = None,
                 author_url = None,
                 postfix_name = None,
                 verbose = 1):
        self.verbose = verbose
        installer_name = to_filename(installer_name, version, postfix_name)
        self.iss_path = os.path.join(src_dir, "%s.iss" % installer_name)
        self.src_dir = src_dir
        if not self.src_dir[-1] in "\\/":
            self.src_dir += os.sep
        self.dist_dir = dist_dir
        self.name = name
        self.installer_name = installer_name
        self.install_dir = install_dir
        self.version = version
        self.author_name = author_name
        self.author_url = author_url
        self.data_files = [self.chop(p) for p in data_files]
        self.sys_files = [self.chop(p) for p in sys_files]
        self.exe_files = exe_files

    def chop(self, pathname):
        assert pathname.startswith(self.src_dir)
        return pathname[len(self.src_dir):]

    def create(self):
        datastore = dict(('self_' + k, getattr(self, k)) for k in dir(self))
        datastore['distribution_full_path'] = os.path.join(
                self.dist_dir, self.installer_name)
        datastore['app_publisher'] = ''
        datastore['app_publisher_url'] = ''
        datastore['app_support_url'] = ''

        if self.author_name:
            datastore['app_publisher'] = "AppPublisher=%s" % self.author_name
        if self.author_url:
            datastore['app_publisher_url'] = "AppPublisherURL=%s" % self.author_url
            datastore['app_support_url'] = "AppSupportURL=%s" % self.author_url

        data_files = []
        for path in self.data_files:
            dirname = os.path.dirname(path)
            data_files.append(
                r'Source: "%s"; DestDir: "{app}\%s"; Flags: ignoreversion' % (
                path, dirname))
        datastore['data_files'] = '\n'.join(data_files)

        sys_files = []
        for path in self.sys_files:
            sys_files.append(
                r'Source: "%s"; DestDir: "{sys}"; Flags: restartreplace uninsneveruninstall sharedfile comparetimestamp' % path)
        datastore['sys_files'] = '\n'.join(sys_files)

        icons = []
        for name, path in self.exe_files:
            icons.append(
                r'Name: "{group}\%s"; Filename: "{app}\%s"' %
                (name, path))
        datastore['icons'] = '\n'.join(icons)

        with open(self.iss_path, "w") as f:
            f.write(MAIN_SCRIPT % datastore)

    def compile(self):
        try:
            import win32_program_finder
            compiler = win32_program_finder.main('Inno Setup', 'ISCC.exe')
        except:
            compiler = 'ISCC.exe'

        proc = subprocess.Popen(
                [compiler, self.iss_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=sys.stderr
            )

        if self.verbose:  # displaying progress count-up
            total_count = len(self.data_files) + len(self.sys_files)
            count = -1
            last_lines = []

            for line in iter(proc.stdout.readline, ''):
                log.debug(line.rstrip())
                if count >= 0 or line.startswith('Creating setup files'):
                    count += 1
                if 0 < count <= total_count:
                    if self.verbose == 1:
                        sys.stdout.write('\r')
                    sys.stdout.write(
                        "  Files %d / %d [%d%%]" %
                        (count, total_count, 100.0 * count / total_count)
                    )
                    if self.verbose > 1:
                        sys.stdout.write('\n')
                elif count > total_count:
                    last_lines.append(line.rstrip())
            sys.stdout.write('\n')
            if self.verbose == 1:
                map(log.info, last_lines[-2:])

        else:
            for line in proc.stdout:
                pass

        proc.wait()
        return proc.returncode == 0

    def cleanup(self):
        if os.path.exists(self.iss_path):
            os.unlink(self.iss_path)


################################################################

def builder(name, installer_name, install_dir, src_dir, dist_dir,
           version='0.0.1', author_name=None, author_url=None,
           postfix_name=None, verbose=1):
    data_files = []
    sys_files = []
    exe_files = []
    for dirpath, dirnames, filenames in os.walk(src_dir):
        if 'SysFiles' in dirpath:
            for filename in filenames:
                sys_files.append(os.path.join(dirpath, filename))
        else:
            for filename in filenames:
                data_files.append(os.path.join(dirpath, filename))

    script = InnoScript(name,
                        installer_name,
                        install_dir,
                        src_dir,
                        os.path.abspath(dist_dir),
                        data_files,
                        sys_files,
                        exe_files,
                        version,
                        author_name,
                        author_url,
                        postfix_name,
                        verbose)
    log.info("Creating the inno setup script.")
    script.create()
    log.info("Compiling the inno setup script.")
    if script.compile():
        script.cleanup()

