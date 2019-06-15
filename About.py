###############################################################################
# MIT License
# author: Exia.Huang
# github: https://github.com/exiahuang
###############################################################################

import sublime_plugin
import webbrowser

class ExiaOpenUrlCommand(sublime_plugin.ApplicationCommand):
    def run(command, url):
        webbrowser.open_new_tab(url)
