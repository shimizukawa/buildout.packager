# -*- coding: utf-8 -*-
import os
import sys
import subprocess
from distutils.util import get_platform
from distutils import log
from utils import get_postfix_name, to_filename


# function IsNeedsAddPath(Param: string): boolean;
# var
#   OrigPath: string;
# begin
#   if not RegQueryStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', OrigPath)
#   then begin
#     Result := True;
#     exit;
#   end;
#   // look for the path with leading and trailing semicolon
#   // Pos() returns 0 if not found
#   Result := Pos(';' + Param + ';', ';' + OrigPath + ';') = 0;
# end;


class NSISScript(object):
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
        installer_name += '.exe'
        self.script_path = os.path.join(src_dir, "%s.nsi" % installer_name)
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
        ofi = open(self.script_path, "w")
        name = self.name
        print >> ofi, "; WARNING: This script has been created by buildout.packager."
        print >> ofi, "; Changes to this script will be overwritten the next time buildout.packager is run!"
        print >> ofi, r'Name "%s"' % name
        #print >> ofi, r"AppVerName=%s" % name + ' ' + self.version
        print >> ofi, r'InstallDir $PROGRAMFILES\%s' % (self.install_dir)
        #print >> ofi, r"DefaultGroupName=%s" % name
        #print >> ofi, r"PrivilegesRequired=admin"
        print >> ofi, r'RequestExecutionLevel user'
        #if self.author_name:
        #    print >> ofi, r"AppPublisher=%s" % self.author_name
        #if self.author_url:
        #    print >> ofi, r"AppPublisherURL=%s" % self.author_url
        #    print >> ofi, r"AppSupportURL=%s" % self.author_url
        print >> ofi, r'OutFile "%s"' % os.path.join(self.dist_dir, self.installer_name)
        print >> ofi, r'SetCompressor lzma'
        print >> ofi

        print >> ofi, r'; Languages'
        for lang in (
                'English.nlf', 'Japanese.nlf', 'Dutch.nlf', 'French.nlf',
                'German.nlf', 'Korean.nlf', 'Russian.nlf', 'Spanish.nlf',
                'Swedish.nlf', 'TradChinese.nlf', 'SimpChinese.nlf',
                'Slovak.nlf',):
            print >> ofi, r'LoadLanguageFile "${NSISDIR}\Contrib\Language files\%s"' % lang
        print >> ofi

        print >> ofi, r'; pages'
        print >> ofi, r'Page directory'
        print >> ofi, r'Page instfiles'
        print >> ofi

        if self.data_files:
            print >> ofi, r'Section "files"'
            for path in self.data_files:
                dirname = os.path.join('$INSTDIR', os.path.dirname(path)).rstrip(os.sep)
                print >> ofi, r'SetOutPath ' + dirname
                print >> ofi, r'File "%s"' % (path,)
            print >> ofi, 'SectionEnd'
            print >> ofi

        if self.sys_files:
            print >> ofi, r'Section "sysfiles"'
            print >> ofi, r'SetOutPath $SYSDIR'
            for path in self.sys_files:
                print >> ofi, r'File "%s"' % (path,)
            print >> ofi, 'SectionEnd'
            print >> ofi

        #print >> ofi, r"[Icons]"
        #for name, path in self.exe_files:
        #    print >> ofi, r'Name: "{group}\%s"; Filename: "{app}\%s"' % \
        #          (name, path)
        #print >> ofi, 'Name: "{group}\Uninstall %s"; Filename: "{uninstallexe}"' % self.name
        #print >> ofi

        ## TODO: when using pre-installed python interpreter, this code will stuck.
        ## TODO: check return code $0
        print >> ofi, r'Section "postinstall"'
        print >> ofi, r'''nsExec::ExecToLog  '"$INSTDIR\python\python.exe" "$INSTDIR\packages\postinstall.py"' '''
        print >> ofi, r'Pop $0'
        print >> ofi, r'SectionEnd'
        print >> ofi

        print >> ofi, r'Section "registry"'
        d = dict(name=self.name, version=self.version, author_name=self.author_name)
        #print >> ofi, r'InstallDirRegKey HKLM "Software\%(author_name)s\%(name)s" "Install_Dir"' % d
        print >> ofi, r'WriteRegStr HKLM SOFTWARE\%(author_name)s\%(name)s "Install_Dir" "$INSTDIR"' % d
        #print >> ofi, r'Root: HKCU; Subkey: "Software\%(author_name)s\%(name)s\%(version)s"; Flags: uninsdeletekey' % d

        # add path
        #print >> ofi, r'''Root: HKCU; Subkey: "Environment"; ValueName: "Path"; ValueType: "expandsz"; ValueData: "{olddata};{app}\bin;";'''  # Check: IsNeedsAddPath("{app}\bin;");

        # registry
        # FIXME: if user want to install on local-user-mode, below config prevent installation.
        #print >> ofi, r'Root: HKLM; Subkey: "Software\%(author_name)s"; Flags: uninsdeletekeyifempty' % d
        #print >> ofi, r'Root: HKLM; Subkey: "Software\%(author_name)s\%(name)s"; Flags: uninsdeletekeyifempty' % d
        #print >> ofi, r'Root: HKLM; Subkey: "Software\%(author_name)s\%(name)s\%(version)s"; Flags: uninsdeletekey' % d
        #print >> ofi, r'Root: HKLM; Subkey: "Software\%(author_name)s\%(name)s\%(version)s"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"' % d
        #print >> ofi, r'Root: HKLM; Subkey: "Software\%(author_name)s\%(name)s\%(version)s"; ValueType: string; ValueName: "Revision"; ValueData: "%(version)s"' % d
        print >> ofi

        # registry for windows uninstall menu
        print >> ofi, r'WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\%(name)s" "DisplayName" "%(name)s"'
        print >> ofi, r'WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\%(name)s" "UninstallString" \'"$INSTDIR\uninstall.exe"\''
        print >> ofi, r'WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\%(name)s" "NoModify" 1'
        print >> ofi, r'WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\%(name)s" "NoRepair" 1'
        print >> ofi, r'WriteUninstaller "uninstall.exe"'
        print >> ofi, r'SectionEnd'
        print >> ofi

        # uninstall
        print >> ofi, r'UninstPage uninstConfirm'
        print >> ofi, r'UninstPage instfiles'
        print >> ofi
        print >> ofi, r'Section "Uninstall"'

#  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Example2"
#  DeleteRegKey HKLM SOFTWARE\NSIS_Example2

        print >> ofi, r'RMDir /r $INSTDIR\bin'
        print >> ofi, r'RMDir /r $INSTDIR\cache'
        print >> ofi, r'RMDir /r $INSTDIR\develop-eggs'
        print >> ofi, r'RMDir /r $INSTDIR\packages'
        print >> ofi, r'RMDir /r $INSTDIR\parts'
        print >> ofi, r'RMDir /r $INSTDIR\python'
        print >> ofi, r'Delete $INSTDIR\.installed.cfg'
        print >> ofi, r'Delete $INSTDIR\uninstall.exe'
        print >> ofi, r'Delete $INSTDIR\buildout.cfg'
        print >> ofi, r'Delete $INSTDIR\buildout_post.cfg'
        print >> ofi, r'Delete $INSTDIR\uninstall.exe'
        print >> ofi, r'SectionEnd'
        print >> ofi

        ofi.close()

    def compile(self):
        import win32_program_finder
        compiler = win32_program_finder.main('NSIS', 'makensis.exe')
        if compiler is None:
            compiler = 'makensis.exe'

        proc = subprocess.Popen(
                [compiler, self.script_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=sys.stderr
            )

        if 0: #self.verbose:  # displaying progress count-up
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
                print line,
                pass

        proc.wait()
        return proc.returncode == 0

    def cleanup(self):
        if os.path.exists(self.script_path):
            os.unlink(self.script_path)


################################################################

def builder(name, installer_name, install_dir, src_dir, dist_dir,
           version='0.0.1', author_name=None, author_url=None,
           postfix_name=None, verbose=1):
    data_files = []
    sys_files = []
    exe_files = []

    for dirpath, dirnames, filenames in os.walk(src_dir):
        if filenames:
            data_files.append(os.path.join(dirpath, '*'))

    script = NSISScript(name,
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
    log.info("Creating the NSIS script.")
    script.create()
    log.info("Compiling the NSIS script.")
    if script.compile():
        script.cleanup()

