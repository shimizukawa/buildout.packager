# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import tempfile
import shutil
from distutils import log
from utils import to_filename

NSIS_BULIDER_DIR = os.path.dirname(os.path.abspath(__file__))


MAIN_SCRIPT = r"""\
; WARNING: This script has been created by buildout.packager.
; Changes to this script will be overwritten the next time buildout.packager is run!

!include "MUI2.nsh"
!addincludedir "%(nsis_builder_dir)s"
!include "EnvVarUpdate.nsh"

Name "%(self_name)s"
InstallDir $PROGRAMFILES\%(self_install_dir)s
OutFile "%(distribution_full_path)s"
SetCompressor lzma
RequestExecutionLevel user

;; AppVerName=%(name_version)s
;; DefaultGroupName=%(self_name)s
;; if self.author_name:
;;     AppPublisher=%(self_author_name)s
;; if self.author_url:
;;     AppPublisherURL=%(self_author_url)s
;;     AppSupportURL=%(self_author_url)s

; start menu
Var StartMenuFolder

; pages
Page directory
!insertmacro MUI_PAGE_STARTMENU Application $StartMenuFolder
Page instfiles


; Languages
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "Japanese"
!insertmacro MUI_LANGUAGE "Dutch"
!insertmacro MUI_LANGUAGE "French"
!insertmacro MUI_LANGUAGE "German"
!insertmacro MUI_LANGUAGE "Korean"
!insertmacro MUI_LANGUAGE "Russian"
!insertmacro MUI_LANGUAGE "Spanish"
!insertmacro MUI_LANGUAGE "Swedish"
!insertmacro MUI_LANGUAGE "TradChinese"
!insertmacro MUI_LANGUAGE "SimpChinese"
!insertmacro MUI_LANGUAGE "Slovak"

Section "files"

    %(data_files)s

SectionEnd

Section "sysfiles"

    SetOutPath $SYSDIR
    %(sys_files)s

SectionEnd


Section "postinstall"

    ; TODO: when using pre-installed python interpreter, this code will stuck.
    ; TODO: check return code $0

    nsExec::ExecToLog '"$INSTDIR\python\python.exe" "$INSTDIR\packages\postinstall.py"'
    Pop $0

SectionEnd


Section "registry"

    WriteRegStr HKLM SOFTWARE\%(self_author_name)s\%(self_name)s "Install_Dir" "$INSTDIR"

    ;InstallDirRegKey HKLM "Software\%(self_author_name)s\%(self_name)s" "Install_Dir"
    ;Root: HKCU; Subkey: "Software\%(self_author_name)s\%(self_name)s\%(self_version)s"; Flags: uninsdeletekey

    ; add bin to PATH environment variable.
    ${EnvVarUpdate} $0 "PATH" "A" "HKCU" "$INSTDIR\bin"

    ;# FIXME: if user want to install on local-user-mode, below config prevent installation.
    ;;Root: HKLM; Subkey: "Software\%(self_author_name)s"; Flags: uninsdeletekeyifempty
    ;;Root: HKLM; Subkey: "Software\%(self_author_name)s\%(self_name)s"; Flags: uninsdeletekeyifempty
    ;;Root: HKLM; Subkey: "Software\%(self_author_name)s\%(self_name)s\%(self_version)s"; Flags: uninsdeletekey
    ;;Root: HKLM; Subkey: "Software\%(self_author_name)s\%(self_name)s\%(self_version)s"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"
    ;;Root: HKLM; Subkey: "Software\%(self_author_name)s\%(self_name)s\%(self_version)s"; ValueType: string; ValueName: "Revision"; ValueData: "%(self_version)s"


    # registry for windows uninstall menu
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\%(self_name)s" "DisplayName" "%(self_name)s"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\%(self_name)s" "UninstallString" \'"$INSTDIR\uninstall.exe"\'
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\%(self_name)s" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\%(self_name)s" "NoRepair" 1
    WriteUninstaller "uninstall.exe"

    !insertmacro MUI_STARTMENU_WRITE_BEGIN Application

      ;Create shortcuts
      CreateDirectory "$SMPROGRAMS\$StartMenuFolder"
      CreateShortCut "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
      CreateShortCut "$SMPROGRAMS\$StartMenuFolder\versions.lnk" "$INSTDIR\versions.txt"

    !insertmacro MUI_STARTMENU_WRITE_END

SectionEnd


; uninstall
UninstPage uninstConfirm
UninstPage instfiles

Section "Uninstall"

    ;;  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Example2"
    ;;  DeleteRegKey HKLM SOFTWARE\NSIS_Example2

    RMDir /r $INSTDIR\bin
    RMDir /r $INSTDIR\cache
    RMDir /r $INSTDIR\develop-eggs
    RMDir /r $INSTDIR\packages
    RMDir /r $INSTDIR\parts
    RMDir /r $INSTDIR\python
    Delete $INSTDIR\.installed.cfg
    Delete $INSTDIR\uninstall.exe
    Delete $INSTDIR\buildout.cfg
    Delete $INSTDIR\buildout_post.cfg
    Delete $INSTDIR\uninstall.exe

    !insertmacro MUI_STARTMENU_GETFOLDER Application $StartMenuFolder

    Delete "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk"
    Delete "$SMPROGRAMS\$StartMenuFolder\versions.lnk"
    RMDir "$SMPROGRAMS\$StartMenuFolder"
    ${un.EnvVarUpdate} $0 "PATH" "R" "HKCU" "$INSTDIR\bin"

SectionEnd

"""


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

        self.temp_path = tempfile.mkdtemp('.nsis', 'buildout.packager-')
        self.script_path = os.path.join(
                self.temp_path, "%s.nsi" % installer_name)
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
        datastore['nsis_builder_dir'] = NSIS_BULIDER_DIR
        datastore['name_version'] = self.name + ' ' + self.version
        datastore['distribution_full_path'] = os.path.join(
                self.dist_dir, self.installer_name)

        data_files = []
        for path in self.data_files:
            dirname = os.path.join('$INSTDIR', os.path.dirname(path)).rstrip(os.sep)
            filename = os.path.join(os.path.abspath(self.src_dir), path)
            data_files.append(r'SetOutPath %s' % dirname)
            data_files.append(r'File "%s"' % filename)
        datastore['data_files'] = '\n'.join(data_files)

        sys_files = []
        for path in self.sys_files:
            sys_files.append(r'File "%s"' % path)
        datastore['sys_files'] = '\n'.join(sys_files)

        with open(self.script_path, "w") as f:
            f.write(MAIN_SCRIPT % datastore)


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
        if os.path.exists(self.temp_path):
            shutil.rmtree(self.temp_path)


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

