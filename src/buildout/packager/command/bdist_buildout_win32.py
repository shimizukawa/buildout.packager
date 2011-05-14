# -*- coding: utf-8 -*-
import os
import sys
import subprocess
from distutils.util import get_platform
from distutils import log
from utils import get_postfix_name


inno_setup_code_section = """
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
        ofi = open(self.iss_path, "w")
        name = self.name
        print >> ofi, "; WARNING: This script has been created by py2exe. Changes to this script"
        print >> ofi, "; will be overwritten the next time py2exe is run!"
        print >> ofi, r"[Setup]"
        print >> ofi, r"AppName=%s" % name
        print >> ofi, r"AppVerName=%s" % name + ' ' + self.version
        print >> ofi, r"DefaultDirName={pf}\%s" % (self.install_dir)
        print >> ofi, r"DefaultGroupName=%s" % name
        print >> ofi, r"AllowUNCPath=no"
        if self.author_name:
            print >> ofi, r"AppPublisher=%s" % self.author_name
        if self.author_url:
            print >> ofi, r"AppPublisherURL=%s" % self.author_url
            print >> ofi, r"AppSupportURL=%s" % self.author_url
        print >> ofi, r"OutputBaseFilename=%s" % self.installer_name
        print >> ofi, r"OutputDir=%s" % self.dist_dir
        print >> ofi, r"PrivilegesRequired=admin"

        print >> ofi
        print >> ofi, r"[Languages]"
        print >> ofi, r'Name: jp; MessagesFile: "compiler:Languages\Japanese.isl"'
        print >> ofi

        print >> ofi, r"[Files]"
        for path in self.data_files:
            print >> ofi, r'Source: "%s"; DestDir: "{app}\%s"; Flags: ignoreversion' % (path, os.path.dirname(path))
        print >> ofi
        for path in self.sys_files:
            print >> ofi, r'Source: "%s"; DestDir: "{sys}"; Flags: restartreplace uninsneveruninstall sharedfile comparetimestamp' % (path)
        print >> ofi

        print >> ofi, r"[Icons]"
        for name, path in self.exe_files:
            print >> ofi, r'Name: "{group}\%s"; Filename: "{app}\%s"' % \
                  (name, path)
        print >> ofi, 'Name: "{group}\Uninstall %s"; Filename: "{uninstallexe}"' % self.name
        print >> ofi

        d = dict(name=self.name, version=self.version, author_name=self.author_name)
        print >> ofi, r'[Registry]'
        print >> ofi, r'Root: HKCU; Subkey: "Software\%(author_name)s"; Flags: uninsdeletekeyifempty' % d
        print >> ofi, r'Root: HKCU; Subkey: "Software\%(author_name)s\%(name)s"; Flags: uninsdeletekeyifempty' % d
        print >> ofi, r'Root: HKCU; Subkey: "Software\%(author_name)s\%(name)s\%(version)s"; Flags: uninsdeletekey' % d
        print >> ofi, r'Root: HKLM; Subkey: "Software\%(author_name)s"; Flags: uninsdeletekeyifempty' % d
        print >> ofi, r'Root: HKLM; Subkey: "Software\%(author_name)s\%(name)s"; Flags: uninsdeletekeyifempty' % d
        print >> ofi, r'Root: HKLM; Subkey: "Software\%(author_name)s\%(name)s\%(version)s"; Flags: uninsdeletekey' % d
        print >> ofi, r'Root: HKLM; Subkey: "Software\%(author_name)s\%(name)s\%(version)s"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"' % d
        print >> ofi, r'Root: HKLM; Subkey: "Software\%(author_name)s\%(name)s\%(version)s"; ValueType: string; ValueName: "Revision"; ValueData: "%(version)s"' % d
        print >> ofi

        print >> ofi, r"[UninstallDelete]"
        print >> ofi, r'Type: filesandordirs; Name: "{app}\parts";'
        print >> ofi, r'Type: filesandordirs; Name: "{app}\bin";'
        print >> ofi, r'Type: filesandordirs; Name: "{app}\develop-eggs";'
        print >> ofi, r'Type: filesandordirs; Name: "{app}\.installed.cfg";'
        print >> ofi

        print >> ofi, inno_setup_code_section
        print >> ofi

        ofi.close()

    def compile(self):
        try:
            import win32_iscc
            compiler = win32_iscc.main()
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


    def cleanup(self):
        if os.path.exists(self.iss_path):
            os.unlink(self.iss_path)


def norm(name):
    return name.replace('-','_')


def to_filename(project_name, project_version, postfix_name=None):
    filename = "%s-%s" % (norm(project_name), norm(project_version))
    if postfix_name:
        filename += '-' + postfix_name
    return filename

################################################################

def make_package(name, installer_name, install_dir, src_dir, dist_dir,
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
    script.compile()
    script.cleanup()

