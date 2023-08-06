#!/usr/bin/python

import configparser
import datetime
import glob
import os.path
import re
import socket
import sys
import time
import queue
import sched

from PIL import Image
from pystray import Icon, Menu, MenuItem
from concurrent.futures import ThreadPoolExecutor
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

INI_FILENAME = "rectree.ini"

def dict_sort_by_key(dict):
    return {key: val for key, val in sorted(dict.items(), key=lambda elem: elem[0], reverse=True)}


class TreeHandler(FileSystemEventHandler):

    def __init__(self, queue, exclusions=''):
        #self.modified = []
        self.exclusions = exclusions
        self.queue = queue

    def on_any_event(self, event):
        print(event)
        path = event.src_path
        pathfile = os.path.abspath(path)
        if event.is_directory:
            return
        if len(self.exclusions) == 0 or len(re.findall(self.exclusions, pathfile)) == 0:
            new_item = {'type': event.event_type, 'pathfile': pathfile}
            print("Putting in queue", new_item)
            self.queue.put(new_item)


class TreeScanner:

    def __init__(self, dir, num_items=5, exclusions=''):
        self.dir = dir
        self.num_items = num_items
        self.mtimes = []
        self.treedict = {}
        self.exclusions = exclusions
        self.queue = queue.Queue()
        self.notifications = []

    def dirtree(self):
        start = datetime.datetime.now()
        tree = glob.glob(os.path.abspath(self.dir) +
                         os.sep + "**", recursive=True)
        treedict = {}
        for filepath in tree:
            if not os.path.isdir(filepath):
                if len(self.exclusions) == 0 or len(re.findall(self.exclusions, filepath)) == 0:
                    treedict[os.path.getmtime(filepath)] = filepath

        self.treedict = dict_sort_by_key(treedict)

        end = datetime.datetime.now()
        print(self.dir+':', str(end-start))
        return self.treedict

    def poll(self):
        event_handler = TreeHandler(self.queue, self.exclusions)
        observer = Observer()
        observer.schedule(event_handler, self.dir, recursive=True)
        observer.start()

    def query(self):
        modified_files = []
        while not self.queue.empty():
            dequeued = self.queue.get()
            print(
                f"Retrieving {dequeued['type']}:  '{dequeued['pathfile']}' from queue")
            modified_files.append(dequeued)
        return modified_files

    def update_tree(self):
        changed = self.query()
        for item in changed:
            type = item['type']
            filepath = item['pathfile']
            # if filepath in self.treedict.values():
            if filepath in self.treedict.values() and (type == 'modified' or type == 'deleted'):
                # retrieves the key for this filepath in the dirtree dictionary
                values_idx = list(self.treedict.values()).index(filepath)
                key = list(self.treedict.keys())[values_idx]
                del self.treedict[key]
            if type == 'modified' or type == 'created':
                self.treedict[os.path.getmtime(filepath)] = filepath
            self.notifications.append(f"{type} {filepath}")

        self.treedict = dict_sort_by_key(self.treedict)

    def empty_notifications(self):
        self.notifications = []

    def treeset(self):
        values = list(self.treedict.values())
        return set(values[:self.num_items])


class MenuFiller():

    def __init__(self, config,runner):
        self.scanners = []
        self.config = config
        self.runner = runner
        self.mute = False

    def fillsubdirmenuitems(self, treescanner):
        menuitems = []
        dictpath = {}
        treedict = treescanner.treedict
        mtimes = list(treedict.keys())
        for mtime in mtimes[:treescanner.num_items]:
            filepath = treedict[mtime]
            filename = os.path.basename(filepath)
            dictpath[filename] = filepath
            item = MenuItem(filename, lambda icon, item: os.startfile(dictpath[item.text]),
                            visible=True)
            menuitems.append(item)
        return tuple(menuitems)

    def dir_menuitems(self, scanner):
        dir_menuitems = self.fillsubdirmenuitems(scanner)
        dir_menu = MenuItem(scanner.dir,  Menu(* dir_menuitems))
        return dir_menu




    def append_constant_menu_items(self):
        mainmenu_items = []

        mainmenu_items.append(Menu.SEPARATOR)
#        editItem = MenuItem("config", lambda icon: os.startfile(INI_FILENAME))
        editItem = MenuItem("config", lambda icon: self.runner.gui_config(icon))

        mainmenu_items.append(editItem)
        reloadItem = MenuItem("reload", lambda icon: self.runner.reload_app(icon))
        mainmenu_items.append(reloadItem)
        muteItem = MenuItem("mute", lambda icon: self.runner.mute_notifications(icon))
        mainmenu_items.append(muteItem)

        mainmenu_items.append(Menu.SEPARATOR)

        exitItem = MenuItem("exit", lambda icon: self.runner.exit_menu(icon))
        mainmenu_items.append(exitItem)
        return mainmenu_items

    def retrieve_main_menu_items(self, icon=None):

        mainmenu_items = []

        start = datetime.datetime.now()
        for scanner in self.scanners:
            scanner.update_tree()
            if self.runner.mute == False and len(scanner.notifications) > 0:
                text = "\n".join([notification for notification in scanner.notifications])
                if  len(text) > 255: # On Windows, the notification text can not exceed 255 chars
                    text = f"There where {len(scanner.notifications)} changes in {scanner.dir}"
                icon.notify(text)
                scanner.empty_notifications()
            mainmenu_items.append(self.dir_menuitems(scanner))

        end = datetime.datetime.now()
        print( datetime.datetime.now(),"Execution time", end - start)

        mainmenu_items.extend(self.append_constant_menu_items())

        items = tuple(mainmenu_items)
        return items

    def fill_initial_menu(self, icon=None):
        start = datetime.datetime.now()
        dirs = []
        for direntry in self.config.sections():
            dir = self.config.get(direntry, 'dir')
            num_items = self.config.getint(direntry, 'num')
            try:
                exclusions = self.config.get(direntry, 'exclude')
            except (KeyError, configparser.NoOptionError):
                exclusions = ''
            dirs.append((dir, num_items, exclusions))

        mainmenu_items = []

        for dir, num_items, exclusions in dirs:
            self.scanners.append(TreeScanner(dir, num_items, exclusions))

        with ThreadPoolExecutor(max_workers=3) as executor:
            executor.map(TreeScanner.dirtree, self.scanners)

        for scanner in self.scanners:
            mainmenu_items.append(self.dir_menuitems(scanner))
            scanner.poll()

        end = datetime.datetime.now()
        print("Execution time", end - start)

        mainmenu_items.extend(self.append_constant_menu_items())

        items = tuple(mainmenu_items)
        return items

class Runner:

    def __init__(self,icon = None):
      self.icon = icon
      self.config = None
      self.filler = None
      self.scheduler = sched.scheduler()
      self.mute = False

    def unmute_notifications(self):
        print("Unmute notifications")
        self.mute = False
        self.scheduler = sched.scheduler()
        self.icon.icon = Image.open(self.config['DEFAULT']['icon'])

    def mute_notifications(self,icon):
        print("muting notifications")
        self.mute = True
        self.icon.icon = Image.open('taskchecker-traced.ico')
        self.scheduler.enter(int(self.config['DEFAULT']['mute_interval']),1,self.unmute_notifications)
        self.scheduler.run()

    def load_config(self):
        config = configparser.ConfigParser()
        config.read(INI_FILENAME)
        print("Reading", INI_FILENAME)
        self.config = config
        return config

    def run(self):
        self.load_config()
        def_config = self.config['DEFAULT']
        iconpath = def_config['icon']
        self.filler = MenuFiller(self.config,self)
        icon = Icon(__name__, Image.open(iconpath), title=__file__,
                    menu=self.filler.fill_initial_menu())
        self.icon = icon
        icon.run_detached()

        while True:
            time.sleep(int(def_config['wait']))
            print("Updating menu")
            if not icon._running:
                break
            try:
                icon.menu = self.filler.retrieve_main_menu_items(icon)
                icon.update_menu()
            except SystemExit as sex:
                break


    def exit_menu(self, icon):
        icon.stop()

    def reload_app(self,icon):
        self.load_config()
        def_config = self.config['DEFAULT']
        iconpath = def_config['icon']
        self.filler = MenuFiller(self.config,self)
        icon.menu = self.filler.fill_initial_menu()
        icon.update_menu()


    def gui_config(self,icon):
        import rectree_config_gui
        rectree_config_gui.config_gui()
        self.reload_app(icon)

def main():
    Runner().run()
#    except Exception as ex:
#        print(ex)


if __name__ == '__main__':
    main()
