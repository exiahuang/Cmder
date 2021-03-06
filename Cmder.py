###############################################################################
# MIT License
# author: Exia.Huang
# github: https://github.com/exiahuang
###############################################################################

import sublime
import sublime_plugin
import os, re
import json
from .OsUtil import OsUtil
from .SublConsole import SublConsole

CMDER_SETTING = "cmder.sublime-settings"


class OpenCmderSettingCommand(sublime_plugin.WindowCommand):

    def run(self):
        SETTING_PATH = os.path.join(sublime.packages_path(), "User",
                                    CMDER_SETTING)
        if not os.path.exists(SETTING_PATH):
            s = sublime.load_settings(CMDER_SETTING)
            tasks = s.get("tasks")
            custom_env = s.get("custom_env")
            s.set("tasks", tasks)
            s.set("custom_env", custom_env)
            sublime.save_settings(CMDER_SETTING)
        self.window.run_command("open_file", {"file": SETTING_PATH})


class CmderCommand(sublime_plugin.WindowCommand):

    def run(self):
        self.window = sublime.active_window()
        self.sublconsole = SublConsole(window=self.window, name='Cmder')
        self.config = Config().get_config(window=self.window)
        self.window.show_quick_panel(self.config["task_keys"], self.panel_done,
                                     sublime.MONOSPACE_FONT)

    def panel_done(self, picked):
        if 0 > picked < len(self.sel_keys):
            return
        task = self.config["tasks"][picked]
        Cmder(self.window, self.config, task,
              sublconsole=self.sublconsole).run()


class Config():

    def get_config(self, window):
        s = sublime.load_settings(CMDER_SETTING)
        tasks = s.get("tasks")
        env = s.get("custom_env")
        env.update(DxEnv().get_env())
        env.update(CommandEnv(window).get_env())
        task_keys = [task["label"] for task in tasks]
        triggers = s.get("triggers") if s.has("triggers") else {}
        config = {
            "tasks":
                tasks,
            "encoding":
                s.get("encoding") if s.has("encoding") else None,
            "env":
                env,
            "task_keys":
                task_keys,
            "after_save_triggers":
                triggers["after_save_triggers"]
                if "after_save_triggers" in triggers else []
        }
        return config

    def get_task(self, window, task_label):
        config = self.get_config(window)
        for task in config["tasks"]:
            if task_label == task["label"]:
                return task
        return None


class PrintCmderCommand(sublime_plugin.WindowCommand):

    def run(self):
        self.window = sublime.active_window()
        self.sublconsole = SublConsole(window=self.window, name='Cmder')
        s = sublime.load_settings(CMDER_SETTING)
        commands = []
        commands.append("| Lable | Command | Description |")
        commands.append("| ---- | ---- | ---- |")
        for task in s.get("tasks"):
            desc = task["desc"] if "desc" in task else ""
            line = '| %s | %s | %s |' % (self.replace_special_code(
                task["label"]), self.replace_special_code(
                    task["command"]), self.replace_special_code(desc))
            commands.append(line)
        self.sublconsole.show_in_new_tab("\n".join(commands),
                                         name="cmder-help.md")

    def replace_special_code(self, str1):
        if str1 is None: return ""
        return str1.replace("|", "&#124;").replace("$", r"\$")
        # return str1.replace("|", "&#124;")


class DxEnv():

    def get_env(self):
        return {
            "SFDX_ALIAS": self.__get_alias(),
        }

    def __get_alias(self):
        return list(self.__get_alias_dict().keys())

    def __get_alias_dict(self):
        home = os.path.expanduser("~")
        dx_alias_file = os.path.join(home, ".sfdx", "alias.json")
        alias = {}
        try:
            if os.path.exists(dx_alias_file):
                f = open(dx_alias_file)
                data = json.load(f)
                alias = data["orgs"]
                f.close()
        except Exception as ex:
            pass
        return alias


class CommandEnv():

    def __init__(self, window):
        self.window = window

    def __get_executable_path(self):
        executable_path = sublime.executable_path()
        if sublime.platform() == 'osx':
            app_path = executable_path[:executable_path.rfind(".app/") + 5]
            executable_path = app_path + "Contents/SharedSupport/bin/subl"
        return executable_path

    def __get_relativeFile(self, file, workspaceFolder):
        try:
            return os.path.relpath(file, workspaceFolder)
        except Exception as e:
            pass
        return file

    def get_env(self):
        workspaceFolder = self._get_workspaceFolder()
        file = self.window.active_view().file_name()
        if file is None: file = ""
        fileBasenameNoExtension, fileExtname = os.path.splitext(
            os.path.basename(file))
        workspaceFolderDirname = os.path.dirname(workspaceFolder)
        relativeDirs = [
            os.path.join(workspaceFolderDirname, name)
            for name in os.listdir(workspaceFolderDirname)
            if os.path.isdir(os.path.join(workspaceFolderDirname, name))
        ] if os.path.exists(workspaceFolderDirname) else []
        env = {
            "cwd": workspaceFolder,
            "workspaceFolder": workspaceFolder,
            "workspaceFolderBasename": os.path.basename(workspaceFolder),
            "file": file,
            "fileBasenameNoExtension": fileBasenameNoExtension,
            "fileExtname": fileExtname,
            "relativeFile": self.__get_relativeFile(file, workspaceFolder),
            "relativeDirs": relativeDirs,
            "fileBasename": os.path.basename(file),
            "fileDirname": os.path.dirname(file),
            "selectedText": self.__get_sel_text(),
            "execPath": self.__get_executable_path(),
        }
        # print(env)
        return env

    def _get_workspaceFolder(self):
        folders = self.window.folders()
        if folders and len(folders) > 0:
            return self.window.folders()[0]
        return ''

    def __get_sel_text(self):
        try:
            view = self.window.active_view()
            sel = view.sel()
            region1 = sel[0]
            selectionText = view.substr(region1)
            return selectionText
        except Exception as ex:
            pass
            return ""


class Cmder():

    def __init__(self, window, config, task, sublconsole):
        self.index = 0
        self.window = window
        self.sublconsole = sublconsole
        self.config = config
        self.env = config["env"]
        self.encoding = task["encoding"] if "encoding" in task else self.config[
            "encoding"]
        self.is_os_termial = task[
            "os_termial"] if "os_termial" in task else False
        self.task = task
        self.command = task["command"]
        self.params = self.__get_command_params(self.command)
        self.osutil = OsUtil(platform=sublime.platform(),
                             sublconsole=self.sublconsole)

    def __validator(self):
        if "filetype" in self.task:
            if not isinstance(self.task["filetype"], list):
                return {
                    "state": False,
                    "code": 11,
                    "msg": "please check your filetype setting!"
                }
            if self.env["fileExtname"] not in self.task["filetype"]:
                return {
                    "state": False,
                    "code": 1,
                    "msg": "Type not match, Do not run command!"
                }

        if "folder_exclude" in self.task:
            if not isinstance(self.task["folder_exclude"], list):
                return {
                    "state": False,
                    "code": 11,
                    "msg": "please check your folder_exclude setting!"
                }
            file = self.env["file"]
            for ex_dir in self.task["folder_exclude"]:
                if os.path.abspath(ex_dir) in file:
                    return {
                        "state": False,
                        "code": 2,
                        "msg": "Exclude folder, Do not run command!"
                    }

        if "folder_include" in self.task:
            if not isinstance(self.task["folder_include"], list):
                return {
                    "state": False,
                    "code": 12,
                    "msg": "please check your folder_include setting!"
                }
            file = self.env["file"]
            can_run = False
            for in_dir in self.task["folder_include"]:
                if os.path.abspath(in_dir) in file:
                    can_run = True
                    break
            if not can_run:
                return {
                    "state": False,
                    "code": 3,
                    "msg": "Include folder, Do not run command!"
                }

        return {"state": True, "code": 0, "msg": "OK"}

    def run(self):
        check_result = self.__validator()
        if check_result["code"] > 10:
            self.sublconsole.showlog(check_result["msg"])
        if check_result["state"]:
            UiWizard(command_params=self.params,
                     window=self.window,
                     callback=self.on_wizard_done).run()

    def on_wizard_done(self, user_params):
        command = self.command

        for key, val in self.env.items():
            if type(val) is str:
                command = command.replace("${%s}" % key, val)

        msgs = []
        for param in self.__get_sys_env(command):
            command = command.replace(param["param"], param["value"])
            if not param["value"]:
                msgs.append("%s is null! please check it." % param["param"])
        for param in user_params:
            command = command.replace(param["param"], param["value"])
            if not param["value"]:
                msgs.append("%s is null! please check it." % param["param"])

        if "type" in self.task:
            if self.task["type"].lower() == "bash":
                command = "bash -c {}".format(self.__shellquote(command))

        if len(msgs) > 0:
            self.sublconsole.showlog("\n".join(msgs), type='error')
        else:
            self.sublconsole.showlog(command)
            cmds = [
                self.osutil.get_cd_cmd(self.env["workspaceFolder"]), command
            ]
            if self.is_os_termial:
                self.osutil.run_in_os_termial(cmds)
            else:
                self.osutil.run_in_sublime_cmd(cmds, encoding=self.encoding)

    def __shellquote(self, s):
        return "\"" + s.replace("\"", "\\\"").replace("$", r"\$") + "\""

    def __get_sys_env(self, command):
        pattern = r"\${(env)(\s)*:(\s)*([^} ]+)(\s)*}"
        matchedList = re.findall(pattern, command)
        sys_env = []
        if matchedList:
            for param in matchedList:
                key = param[3]
                sys_env.append({
                    "param": "${%s%s:%s%s%s}" % param,
                    "key": key,
                    "value": os.getenv(key, default=""),
                    "type": param[0]
                })
        return sys_env

    def __get_command_params(self, command):
        pattern = r"\${(input|select)(\s)*:(\s)*([^} ]+)(\s)*}"
        matchedList = re.findall(pattern, command)
        params = []
        if matchedList:
            for param in matchedList:
                key = param[3]
                data = {
                    "param": "${%s%s:%s%s%s}" % param,
                    "key": key,
                    "value": "",
                    "type": param[0]
                }
                if data["type"] == "input":
                    if key in self.env:
                        data["value"] = str(self.env[key])
                elif data["type"] == "select":
                    data["option"] = data["option-v"] = []
                    if key in self.env:
                        if isinstance(self.env[key], list):
                            data["option"] = data["option-v"] = self.env[key]
                    if len(data["option"]) == 0:
                        self.sublconsole.showlog("The list of %s is none!" %
                                                 (key),
                                                 type='error')
                params.append(data)
        return params


class UiWizard():

    def __init__(self, command_params, window, callback):
        self.index = 0
        self.command_params = command_params
        self.window = window
        self.callback = callback

    def run(self, args=None):
        if self.index > 0:
            pre_data = self.command_params[self.index - 1]
            ui_type = pre_data["type"]
            if ui_type == "input":
                pre_data["value"] = args
            elif ui_type == "select":
                if 0 <= args and args < len(pre_data["option-v"]):
                    pre_data["value"] = pre_data["option-v"][args]

        if self.index < len(self.command_params):
            curr_data = self.command_params[self.index]
            if curr_data["type"] == "input":
                caption = "Please Input your %s: " % curr_data["key"]
                self.window.show_input_panel(caption, curr_data["value"],
                                             self.run, None, None)
            elif curr_data["type"] == "select":
                show_opts = curr_data["option"]
                self.window.show_quick_panel(show_opts, self.run,
                                             sublime.MONOSPACE_FONT)
            self.index = self.index + 1
        else:
            self.callback(self.command_params)


#handles compiling to server on save
class SaveListener(sublime_plugin.EventListener):

    def on_post_save(self, view):
        self.window = sublime.active_window()
        self.sublconsole = SublConsole(window=self.window, name='Cmder')
        self.config = Config().get_config(window=self.window)
        for task in self.config["after_save_triggers"]:
            command = task["command"]
            if not command: continue
            Cmder(self.window, self.config, task,
                  sublconsole=self.sublconsole).run()


class RunCmderCommand(sublime_plugin.WindowCommand):

    def run(self, task, dirs=None, files=None, paths=None):
        selected_path = paths[0] if paths and len(paths) > 0 else ''
        self.window = sublime.active_window()
        self.sublconsole = SublConsole(window=self.window, name='Cmder')
        self.config = Config().get_config(window=self.window)
        self.sublconsole.showlog(paths)
        if not task: return
        if not "command" in task: return
        task["command"] = task["command"].replace("${SELECTED_PATH}",
                                                  selected_path)
        Cmder(self.window, self.config, task,
              sublconsole=self.sublconsole).run()
