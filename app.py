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
from kivymd.uix.button import MDFillRoundFlatButton, MDRaisedButton
from kivymd.uix.pickers import MDDatePicker, MDTimePicker
from kivymd.uix.label import MDLabel


@dataclass
class Creds:
    token: str


Window.size = (300, 500)


class LoginScreen(Screen):
    pass


class EventsScreen(Screen):
    pass


class EventScreen(Screen):
    pass


class MyEventsScreen(Screen):
    pass


class MyProfileScreen(Screen):
    pass


class CreateEventScreen(Screen):
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
                "on_release": lambda x="createevent": self.menu_callback(x),
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
        sm.add_widget(CreateEventScreen(name='createevent'))
        sm.add_widget(EventScreen(name='event'))
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
            list = ThreeLineAvatarIconListItem(text=i['title'] if i['title'] else "",
                                               secondary_text=i['description'] if i['description'] else "",
                                               tertiary_text=f"Starting {i['date'][5:]} at {i['start_time'][:5]}",
                                               on_release=self.get_event)
            self.root.get_screen('events').ids.box.add_widget(list)

    def my_events(self):
        headers = {
            'accept': 'application/json',
            'Bear': '',
            'Authorization': f'Bearer {Creds.token}',
        }
        response = requests.get('http://46.48.59.66:2222/events/my', headers=headers)
        self.root.get_screen('myevents').ids.box.add_widget(MDLabel(text="New Events", halign="center"))
        for i in response.json()['owner']['future_event']:
            print(130, i)
            new_list = ThreeLineAvatarIconListItem(text=i['title'] if i['title'] else "",
                                                   secondary_text=i['description'] if i['description'] else "",
                                                   tertiary_text=f"Starting {i['date'][5:]} at {i['start_time'][:5]}",
                                                   on_release=self.get_event)
            self.root.get_screen('myevents').ids.box.add_widget(new_list)
        self.root.get_screen('myevents').ids.box.add_widget(MDLabel(text="Past Events", halign="center"))
        for i in response.json()['owner']['past_event']:
            past_list = ThreeLineAvatarIconListItem(text=i['title'] if i['title'] else "",
                                                    secondary_text=i['description'] if i['description'] else "",
                                                    tertiary_text=f"Starting {i['date'][5:]} at {i['start_time'][:5]}",
                                                    on_release=self.get_event)
            self.root.get_screen('myevents').ids.box.add_widget(past_list)

    def create_event(self):
        print("EVENT")
        self.root.get_screen('createevent').ids.createevent.title = (
            MDTextField(hint_text="Title, max lenght - 10", max_text_length=10))
        self.root.get_screen('createevent').ids.createevent.add_widget(
            self.root.get_screen('createevent').ids.createevent.title)

        self.root.get_screen('createevent').ids.createevent.description = (
            MDTextField(hint_text="Description", multiline=True))
        self.root.get_screen('createevent').ids.createevent.add_widget(
            self.root.get_screen('createevent').ids.createevent.description)

        self.root.get_screen('createevent').ids.createevent.add_widget(
            MDRaisedButton(text="Choose data", pos_hint={'center_x': .5, 'center_y': .5}, md_bg_color="799DE4",
                           on_release=lambda x: self.show_date_picker()))

        self.root.get_screen('createevent').ids.createevent.address = (
            MDTextField(hint_text="Address", max_text_length=20))
        self.root.get_screen('createevent').ids.createevent.add_widget(
            self.root.get_screen('createevent').ids.createevent.address)

        self.root.get_screen('createevent').ids.createevent.add_widget(
            (MDRaisedButton(text="Choose time", pos_hint={'center_x': .5, 'center_y': .5}, md_bg_color="799DE4",
                            on_release=lambda x: self.show_time_picker())))

        self.root.get_screen('createevent').ids.createevent.add_widget(
            MDFillRoundFlatButton(text_color="white",
                                  md_bg_color="799DE4",
                                  text="Submit",
                                  on_press=lambda x: self.event_create(
                                      self.root.get_screen('createevent').ids.createevent)))

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
            self.root.get_screen('myprofile').ids.profile.name = (
                MDTextField(hint_text=response.json()["name"], helper_text="Name"))
            self.root.get_screen('myprofile').ids.profile.add_widget(self.root.get_screen('myprofile').ids.profile.name)

            self.root.get_screen('myprofile').ids.profile.surname = (
                MDTextField(hint_text=response.json()["surname"], helper_text="Surname"))
            self.root.get_screen('myprofile').ids.profile.add_widget(
                self.root.get_screen('myprofile').ids.profile.surname)

            self.root.get_screen('myprofile').ids.profile.lastname = (
                MDTextField(hint_text=response.json()["last_name"], helper_text="Last name"))
            self.root.get_screen('myprofile').ids.profile.add_widget(
                self.root.get_screen('myprofile').ids.profile.lastname)

            self.root.get_screen('myprofile').ids.profile.add_widget(
                MDFillRoundFlatButton(text_color="white",
                                      md_bg_color="799DE4",
                                      text="Submit",
                                      on_press=lambda x: self.profile_edit(
                                          self.root.get_screen('myprofile').ids.profile)))

    def get_event(self, new_list):
        self.root.current = "event"
        self.root.get_screen('event').ids.event.add_widget(
            MDLabel(text=new_list.text if new_list.text else ""))
        self.root.get_screen('event').ids.event.add_widget(
            MDLabel(text=new_list.secondary_text if new_list.secondary_text else ""))
        self.root.get_screen('event').ids.event.add_widget(
            MDLabel(text=new_list.tertiary_text if new_list.tertiary_text else ""))

    def event_create(self, layout):
        print(dir(layout))
        if "date" not in dir(layout) or "time" not in dir(layout):
            self.dialog = MDDialog(
                text="Input data or time!"
            )
            self.dialog.open()
        else:
            headers = {
                'accept': 'application/json',
                'Content-Type': 'application/json',
                'Bear': '',
                'Authorization': f'Bearer {Creds.token}',
            }

            json_data = {
                'title': layout.title.text,
                'description': layout.description.text,
                'date': str(layout.date),
                'start_time': str(layout.time),
                'address': layout.address.text,
                'count_people': 0,
            }
            response = requests.post('http://46.48.59.66:2222/events/create', headers=headers, json=json_data)
            # {'status': 'OK', 'event_id': 17}
            print(response.json())
            self.dialog = MDDialog(
                text="Event created!"
            )
            self.dialog.open()
    def profile_edit(self, layout):
        headers = {
            'accept': 'application/json',
            'Bear': '',
            'Authorization': f'Bearer {Creds.token}',
            'Content-Type': 'application/json',
        }

        json_data = {
            'name': layout.name.text,
            'surname':  layout.surname.text,
            'last_name': layout.lastname.text,

        }

        response = requests.post('http://46.48.59.66:2222/profile/change', headers=headers, json=json_data)
        if response.status_code == 200:
            self.dialog = MDDialog(
                text="Profile changed!"
            )
            self.dialog.open()
        else:
            self.dialog = MDDialog(
                text=response.json()['detail']
            )
            self.dialog.open()

    def menu_callback(self, text_item):
        self.menu.dismiss()
        Snackbar(text=text_item).open()
        if text_item == "myevents":
            self.root.current = "myevents"
            self.my_events()
        elif text_item == "events":
            self.root.current = "events"
            self.all_events()
        elif text_item == "myprofile":
            self.root.current = "myprofile"
            self.my_profile()
        elif text_item == "createevent":
            self.root.current = "createevent"
            self.create_event()

    def on_save(self, instance, value, date_range):
        self.root.get_screen('createevent').ids.createevent.date = value
        print(instance, value, date_range)

    def on_save_time(self, instance, value):
        self.root.get_screen('createevent').ids.createevent.time = value
        print(instance, value)

    def on_cancel(self, instance, value):
        """Events called when the "CANCEL" dialog box button is clicked."""

    def show_date_picker(self):
        date_dialog = MDDatePicker(primary_color="799DE4")
        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        date_dialog.open()

    def show_time_picker(self):
        time_dialog = MDTimePicker(primary_color="799DE4", accent_color="white", text_button_color="white")
        time_dialog.bind(on_save=self.on_save_time)
        time_dialog.open()


MainApp().run()
