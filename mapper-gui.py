#!/usr/bin/env python3

"""A simple GUI for mapper.py."""

import os
import kivy
import threading
kivy.require('1.9.1')

from mapper               import map, bitsFromFile
from kivy.app             import App
from kivy.clock           import Clock
from kivy.uix.label       import Label
from kivy.uix.button      import Button
from kivy.uix.textinput   import TextInput
from kivy.uix.boxlayout   import BoxLayout
from kivy.uix.gridlayout  import GridLayout
from kivy.uix.progressbar import ProgressBar
from kivy.uix.filechooser import FileChooserListView


class MainScreen(BoxLayout):
    """Main view"""

    def updateProgress(self, value): # NOTE: Only yo be called by Clock Schedulling
        self.progressBar.value = value
        print("FIRE")

    def generate(self):
        thread = threading.Thread(target=self.generateThread)
        thread.start()

    def generateThread(self):
        Clock.schedule_once(lambda dt: self.updateProgress(0)) # NOTE: PBar

        path = os.path.join(self.fileSelector.path, self.fileSelector.selection[0])
        Clock.schedule_once(lambda dt: self.updateProgress(5)) # NOTE: PBar

        data = bitsFromFile(path)
        Clock.schedule_once(lambda dt: self.updateProgress(10)) # NOTE: PBar

        scale = int(self.scaleInput.text)
        ratio = float(self.ratioInput.text)
        multiple = int(self.multipleInput.text)
        if self.nameInput.text == None or self.nameInput.text == "":
            name = path
        else:
            name = os.path.join(self.fileSelector.path, self.nameInput.text)

        map(data, scale=scale, ratio=ratio, multiple=multiple, name=name)
        Clock.schedule_once(lambda dt: self.updateProgress(100)) # NOTE: PBar


class MapperGUI(App):
    """Main app"""
    def build(self):
        return MainScreen()


if __name__ == '__main__':
    MapperGUI().run()
