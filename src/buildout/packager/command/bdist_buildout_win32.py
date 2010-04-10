# -*- coding: utf-8 -*-
import os, sys

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
                 author_url = None):
        installer_name = to_filename(installer_name, version)
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
        print >> ofi

        program = r'"python"'
        param = r'"""{app}\packages\postinstall.py"""'
        print >> ofi, r"[Run]"
        print >> ofi, r'Filename: %s; Parameters: %s;' % (program, param)
        print >> ofi

        #program = r'"{app}\python.exe"'
        #param = r'"""{app}\packages\preuninstall.py"""'
        #print >> ofi, r"[UninstallRun]"
        #print >> ofi, r'Filename: %s; Parameters: %s;' % (program, param)
        #print >> ofi
        ofi.close()

    def compile(self):
        #FIXME! ISCC.exe のインストール先を設定出来るようにする
        compiler = r'"C:\Program Files (x86)\Inno Setup 5\ISCC.exe"'
        os.system("%s %s" % (compiler, self.iss_path))
        #TODO! 実行状況をpipeで取得して行数等で'.'を出力する。同時に.logに保存

    def cleanup(self):
        if os.path.exists(self.iss_path):
            os.unlink(self.iss_path)

def norm(name):
    return name.replace('-','_')

def to_filename(project_name, project_version):
    filename = "%s-%s-py%d.%d" % (
        norm(project_name), norm(project_version),
        sys.version_info[0], sys.version_info[1]
    )

    if sys.platform == 'win32':
        filename += '-' + sys.platform
    return filename

################################################################

def make_package(name, installer_name, install_dir, src_dir, dist_dir,
                 version='0.0.1', author_name=None, author_url=None):
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
                        author_url)
    print "*** creating the inno setup script ***"
    script.create()
    print "*** compiling the inno setup script ***"
    script.compile()
    script.cleanup()

