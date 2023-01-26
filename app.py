from os.path import dirname
from kivy.metrics import dp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivy.lang import Builder
from kivy.core.window import Window
import requests
import os
from dataclasses import dataclass
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.snackbar import Snackbar
from kivymd.app import MDApp
from kivymd.uix.list import ThreeLineAvatarIconListItem
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFillRoundFlatButton


@dataclass
class Creds:
    token: str


Window.size = (300, 500)


class LoginScreen(Screen):
    pass


class EventsScreen(Screen):
    pass


class MyEventsScreen(Screen):
    pass


class MyProfileScreen(Screen):
    pass


class MainApp(MDApp):

    def build(self):
        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": f"My events",
                "height": dp(56),
                "on_release": lambda x="myevents": self.menu_callback(x),
            },
            {
                "viewclass": "OneLineListItem",
                "text": f"Profile",
                "height": dp(56),
                "on_release": lambda x="myprofile": self.menu_callback(x),
            },
            {
                "viewclass": "OneLineListItem",
                "text": "All events",
                "height": dp(56),
                "on_release": lambda x="events": self.menu_callback(x),
            },
            {
                "viewclass": "OneLineListItem",
                "text": "Create Event",
                "height": dp(56),
                "on_release": lambda x="create": self.menu_callback(x),
            },
        ]
        self.menu = MDDropdownMenu(
            items=menu_items,
            width_mult=4,
        )
        Builder.load_file(os.path.join(dirname(__file__), 'login.kv'))
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(EventsScreen(name='events'))
        sm.add_widget(MyEventsScreen(name='myevents'))
        sm.add_widget(MyProfileScreen(name='myprofile'))
        return sm

    def do_login(self, login, password):
        print(login, password)
        import json
        json_data = {
            'username': str(login),
            'password': str(password),
        }
        res = requests.post('http://46.48.59.66:2222/login', data=json.dumps(json_data))
        if res.json().get("detail"):
            print(res.json())
            self.dialog = MDDialog(
                text=str(res.json().get("detail"))
            )
            self.dialog.open()
        else:
            print(res.json())
            Creds.token = res.json()["access_token"][0]
            Builder.load_file(os.path.join(dirname(__file__), 'events.kv'))
            self.menu_callback("events")

    def callback(self, button):
        print("Callback")
        self.menu.caller = button
        self.menu.open()

    def all_events(self):
        response = requests.get('http://46.48.59.66:2222/events')
        for i in response.json():
            print(type(i['date']))
            list = ThreeLineAvatarIconListItem(text=i['title'],
                                               secondary_text=f"Starting {i['date'][5:]} at {i['start_time'][:5]}",
                                               tertiary_text=f"Address {i['address']}")
            self.root.get_screen('events').ids.box.add_widget(list)

    def my_events(self):
        headers = {
            'accept': 'application/json',
            'Bear': '',
            'Authorization': f'Bearer {Creds.token}',
        }
        response = requests.get('http://46.48.59.66:2222/events/my', headers=headers)
        for i in response.json():
            print(type(i['date']))
            list = ThreeLineAvatarIconListItem(text=i['title'],
                                               secondary_text=f"Starting {i['date'][5:]} at {i['start_time'][:5]}",
                                               tertiary_text=f"Address {i['address']}")
            self.root.get_screen('myevents').ids.box.add_widget(list)

    def my_profile(self):
        self.root.current = "myprofile"
        print("Profile", self.root.current)
        headers = {
            'accept': 'application/json',
            'Bear': '',
            'Authorization': f'Bearer {Creds.token}',
        }
        response = requests.get('http://46.48.59.66:2222/profile', headers=headers)
        if response.json().get("detail") == "Not authenticated":
            self.dialog = MDDialog(
                text="Not authenticated"
            )
            self.dialog.open()
        else:
            self.root.get_screen('myprofile').ids.profile.add_widget(
                MDTextField(hint_text=response.json()["username"], helper_text="Username", id="username"))
            self.root.get_screen('myprofile').ids.profile.add_widget(
                MDTextField(hint_text=response.json()["name"], helper_text="Name", id="name"))
            self.root.get_screen('myprofile').ids.profile.add_widget(
                MDTextField(hint_text=response.json()["surname"], helper_text="Surname", id="surname"))
            self.root.get_screen('myprofile').ids.profile.add_widget(
                MDTextField(hint_text=response.json()["last_name"], helper_text="Last name", id="lastname"))
            self.root.get_screen('myprofile').ids.profile.add_widget(
                MDTextField(hint_text=response.json()["email"], helper_text="E-mail", id="email"))
            self.root.get_screen('myprofile').ids.profile.add_widget(
                MDFillRoundFlatButton(text_color="white",
                                      md_bg_color="799DE4",
                                      text="Submit"))

    def profile_edit(self, ids):
        return self

    def menu_callback(self, text_item):
        self.menu.dismiss()
        Snackbar(text=text_item).open()
        if text_item == "myevents":
            self.root.current = "myevents"
        elif text_item == "events":
            self.root.current = "events"
            self.all_events()
        elif text_item == "myprofile":
            self.root.current == "myprofile"
            self.my_profile()


MainApp().run()
