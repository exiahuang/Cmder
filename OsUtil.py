###############################################################################
# MIT License
# author: Exia.Huang
# github: https://github.com/exiahuang
###############################################################################

import os,sys, subprocess,threading

class OsUtil():
    def __init__(self, platform, sublconsole):
        self.platform = platform
        self.sublconsole = sublconsole
        self.sys_encoding = sys.getfilesystemencoding()

    def run_in_sublime_cmd(self, cmd_list, encoding=None):
        if not encoding: encoding = self.sys_encoding
        print("*" * 80)
        print("encoding: " + encoding)
        self.sublconsole.thread_run(target=self._run_cmd, args=(cmd_list, encoding,))
    
    def _run_cmd(self, cmd_list, encoding):
        self.sublconsole.showlog("*" * 80)
        cmd_str = self._get_cmd_str(cmd_list)
        process = subprocess.Popen(cmd_str, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while True:
            line = process.stdout.readline()
            if line != '' and line != b'' :
                #the real code does filtering here
                try:
                    msg = line.rstrip().decode(encoding)
                except UnicodeDecodeError as ex:
                    msg = line.rstrip().decode(self.sys_encoding)
                except UnicodeDecodeError as ex:
                    msg = line.rstrip().decode('UTF-8')
                except Exception as ex:
                    msg = line.rstrip()
                self.sublconsole.showlog(msg, show_time=False)
            else:
                break
        self.sublconsole.showlog("*" * 80)

    def os_run(self, cmd_list):
        if self.sf_basic_config.is_use_os_terminal():
            self.run_in_os_termial(cmd_list)
        else:
            self.run_in_sublime_cmd(cmd_list)

    def run_in_os_termial(self, cmd_list):
        if self.platform == "windows":
            cmd_list.append("pause")
        cmd_str = self._get_cmd_str(cmd_list)
        thread = threading.Thread(target=os.system, args=(cmd_str,))
        thread.start()
    
    def _get_cmd_str(self, cmd_list):
        cmd_str = " & ".join(cmd_list)
        return cmd_str

    def get_cd_cmd(self, path):
        if self.platform == "windows":
            return "cd /d \"%s\"" % (path)
        else:
            return "cd \"%s\"" % (path)