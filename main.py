from enum import auto

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.lang import Builder
from os import listdir
from kivy.properties import ObjectProperty




class AddButton(Button):
    pass


class SubtractButton(Button):
    pass

class FlavioButton(Button):
    pass

class Container(GridLayout):
    display = ObjectProperty()
    flavioButton = ObjectProperty()

    def add_one(self):
        value = int(self.display.text)
        self.display.text = str(value+1)

    def subtract_one(self):
        value = int(self.display.text)
        self.display.text = str(value-1)

    def flavio_button(self):
        self.display.text = str(0)
        self.display.font_size += int(200)
        self.flavioButton.text = "DEUDEU!!! "



class MainApp(App):

    def build(self):
        self.title = 'Awesome app!!!'
        return Container()

if __name__ == "__main__":
    #load all kv files
    kv_path = './screens/'
    for kv in listdir(kv_path):
        Builder.load_file(kv_path + kv)

    #configuracao inicial
    #Config.set('graphics', 'fullscreen', 0)
    #Config.write()

    #run app
    app = MainApp()
    app.run()



