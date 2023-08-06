from json import load, dump
from os import remove
from time import sleep
from threading import Thread

class Manager:
    
    def __init__(self, path="database.db", default={}, everyload=False):
        path = str(path)
        self.path = path
        self.default = default
        self.load()
        self.last = default
        self.everyload = everyload

    def load(self):
        try:
                f = open(self.path, "r")
        except:
            f = open(self.path, "w")
            dump(self.default.copy(), f, ensure_ascii=False)
            f.close()
        try:
            self.db = load(f)
        except Exception as err:
            self.db = self.default.copy()
            self.save()
        f.close()

    def get(self, connect=True):
        if self.everyload: self.load()
        return self.db if connect else self.db.copy()

    def save(self):
        f = open(self.path, "w")
        dump(self.db, f, ensure_ascii=False)
        f.close()
        return True

    def clear(self, default=None):
        self.db = self.default.copy() if default == None else default.copy()
        return self.db

    def delete(self):
        remove(self.path)
        return True
            
# ------------------------------------------- #
# | Lib created by Zoom Developer           | #
# | VK: vk.com/zoom_developer               | #
# | DISCORD: Zoom aka Дурка#1185            | # 
# ------------------------------------------- #
