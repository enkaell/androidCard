from kivy.app import App
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
import os
import requests
from dataclasses import dataclass

@dataclass
class Creds:
    token: str

from connected import Connected

class Login(Screen):
    def do_login(self, loginText, passwordText):
        app = App.get_running_app()

        app.username = loginText
        app.password = passwordText
        data = {
            'username': loginText,
            'password': passwordText,
        }

        res = requests.post('http://46.48.59.66:2222/login', data=data)
        if res.json().get("detail") == "Incorrect username or password" or not passwordText or not loginText:
            print("BAD")
        else:
            self.manager.transition = SlideTransition(direction="left")
            self.manager.current = 'connected'
            Creds.token = res.json().get("access_token")
            app.config.read(app.get_application_config())
            app.config.write()

    def resetForm(self):
        self.ids['login'].text = ""
        self.ids['password'].text = ""


class LoginApp(App):
    username = StringProperty(None)
    password = StringProperty(None)

    def build(self):
        manager = ScreenManager()

        manager.add_widget(Login(name='login'))
        manager.add_widget(Connected(name='connected'))

        return manager

    def get_application_config(self):
        if not self.username:
            return super(LoginApp, self).get_application_config()

        conf_directory = self.user_data_dir + '/' + self.username

        if not os.path.exists(conf_directory):
            os.makedirs(conf_directory)

        return super(LoginApp, self).get_application_config(
            '%s/config.cfg' % conf_directory
        )


if __name__ == '__main__':
    LoginApp().run()
