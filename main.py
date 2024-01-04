from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from pgdb import Connection  # install this package (pip install pgdb)
from kivy.uix.popup import Popup
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.config import Config
from kivy.uix.recycleview import RecycleView
from stopwatch import Stopwatch
from kivy.uix.scrollview import ScrollView
import datetime
import auth
import serial
import importlib
import math
import pandas as pd 
# import serial_test

'''
Storage (for necessary information across screens) --------
'''


class Storage():
    stored_username = ""
    stored_password = ""
    stored_user_id = 0
    stored_first_name = ""
    stored_last_name = ""

    popup_messages = {
        "account_creation": "Account Created! Next, fill out your account details.",
        "incorrect_login": "Incorrect login information. Please try again.",
        "duplicate_username": "Username is already taken, please try another name.",
        "spaces_in_username": "Usernames may not contain spaces.",
        "account_save": "Successfully saved your account data!",
        "successful_login": "Successfully logged into your account!",
        "group_joined": "Group successfully joined!",
        "invalid_code": "Join code is invalid.",
        "group_creation": "Group has been successfully created!"
    }
    
    stopwatch = Stopwatch() 
    workout_type = ""

'''    -----------------------------------------------------            '''

# database connection information in auth.py
conn = Connection(database=auth.database, host=auth.host,
                  user=auth.user, password=auth.password)
cur = conn.cursor()

Window.size = (731, 1300)  # set window size to ~phone resolution, (9:16 ratio)

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

# create a screen manager for kv.txt


class Manager(ScreenManager):
    pass

# the login screen and its functions


class LoginScreen(Screen):
    user_name = ObjectProperty(None)
    password = ObjectProperty(None)

    # might need to do more error checking
    def login(self):
        sql = "SELECT * FROM users WHERE username=%s"
        data = (self.user_name.text.rstrip().lstrip(), )
        cur.execute(sql, data)

        try:
            user_info = cur.fetchall()[0]
            db_password = user_info[2]
            if self.password.text.rstrip() == db_password:
                Storage.stored_user_id = user_info[0]
                Storage.stored_username = self.user_name.text.rstrip().lstrip()
                Storage.stored_password = self.password.text.rstrip()
                if user_info[3] != None:
                    Storage.stored_first_name = user_info[3]
                if user_info[4] != None:
                    Storage.stored_last_name = user_info[4] 
                if user_info[6] != None:
                    Storage.stored_mass = user_info[6]
                self.user_name.text = ""  # clears text inputs after correct login
                self.password.text = ""
                self.parent.current = 'home'
                show_popup("successful_login")
            else:
                show_popup("incorrect_login")
        except:
            show_popup("incorrect_login")

    def create(self):
        if self.user_name.text.find(' ') != -1:
            show_popup("spaces_in_username")
        else:
            sql = "SELECT * FROM users WHERE username=%s;"
            data = (self.user_name.text.rstrip().lstrip(), )
            cur.execute(sql, data)

            if cur.fetchone() == None:
                sql = "INSERT INTO users (username, password) VALUES (%s, %s);"
                Storage.stored_username = self.user_name.text.rstrip().lstrip() # store username and pwd here
                Storage.stored_password = self.password.text.rstrip() # user_id is stored in account screen
                data = (Storage.stored_username, Storage.stored_password)
                cur.execute(sql, data)
                conn.commit()
                show_popup("account_creation")
                self.parent.current = 'account'
                self.manager.transition.direction = 'left'
                self.user_name.text = ""  
                self.password.text = ""

            else:
                show_popup("duplicate_username")

class AccountScreen(Screen):
    first_name = ObjectProperty(None)
    last_name = ObjectProperty(None)
    cancel_button = ObjectProperty(None)
    weight = ObjectProperty(None)

    def cancel(self):
        self.store_id()
        self.parent.current = 'home'

    def save_data(self):
        Storage.stored_first_name = self.first_name.text
        Storage.stored_last_name = self.last_name.text
        try:
            Storage.stored_mass = float(self.weight.text) / 2.2046226218488 # convert to kg
        except:
            Storage.stored_mass = 0

        sql = "UPDATE users SET first_name=%s, last_name=%s, mass=%s WHERE username=%s;"
        data = (Storage.stored_first_name, Storage.stored_last_name, Storage.stored_mass, Storage.stored_username)
        cur.execute(sql, data)  
        conn.commit()      

        self.store_id()

        self.first_name.text = ""
        self.last_name.text = ""
        self.weight.text = ""

        show_popup("account_save")
        self.parent.current = 'home'

    def store_id(self, *args):
        sql = "SELECT * FROM users WHERE username=%s"
        data = (Storage.stored_username, )
        cur.execute(sql, data)
        Storage.stored_user_id = cur.fetchone()[0]

# home/main screen


class HomeScreen(Screen):
    username_display = ObjectProperty(None)
    join_code = ObjectProperty(None)

    def on_enter(self, *args):
        self.username_display.text = Storage.stored_first_name
        if Storage.stored_first_name == "":
            self.username_display.text = ""

    def logout(self):
        self.parent.current = 'login'
        Storage.stored_username = ""  # removes saved information
        Storage.stored_password = ""
        # REMOVE OTHER STORED INFORMATION AS WELL

    def join_group(self):
        sql = "SELECT * FROM Groups WHERE group_id=%s"
        data = (int(self.join_code.text), )
        cur.execute(sql, data)
        db_check = cur.fetchone()

        if db_check == None:
            show_popup("invalid_code")
        else:
            # BUG: enters into database multiple times
            sql = "INSERT INTO Students (user_id, group_id) VALUES (%s, %s);"
            data = (Storage.stored_user_id, int(self.join_code.text))
            cur.execute(sql, data)
            conn.commit()
            show_popup("group_joined")

        self.join_code.text = ""

# tabbed panel for home screen ^


class Tab(TabbedPanel):
    def __init__(self, *args, **kwargs):
        super(Tab, self).__init__(*args, **kwargs)
        self.tab_pos = 'left_top'

# screens for tabs:


# screen for grow mode


class GrowMode(Screen):
    pass


class StoryMode(Screen):
    data = ObjectProperty(None)

    def start_miliseconds(self):
        Clock.schedule_interval(self.update_label, .02)

    def pause_animation(self):
        Clock.unschedule(self.update_label)

    def update_label(self, *args):
        self.data.text = str(serial_test.imuData())

class RunWalk(Screen):
    hours = ObjectProperty(None)
    minutes = ObjectProperty(None)
    seconds = ObjectProperty(None)
    milis = ObjectProperty(None)

    # **** Stopwatch class is used to prevent kivy scheduling glitches from happening 

    running = False # to stop bugs from happening, like spamming start btn
    store_seconds = 0

    def start_timer(self):
        if self.running == False:
            self.running = True
            Storage.stopwatch.start()
            Clock.schedule_interval(self.update_labels, .001) # refresh rate

    def pause_timer(self):
        if self.running == True:
            self.running = False
            Storage.stopwatch.stop()
            Clock.unschedule(self.update_labels)

    def stop_timer(self):
        if self.running == True:
            self.running = False
            Storage.stopwatch.stop()
            Clock.unschedule(self.update_labels)
            Storage.workout_type = "Run/Walk"

    def update_labels(self, *args):
        self.milis.text = str(int(round(Storage.stopwatch.elapsed % 1, 2) * 100))
        self.seconds.text = str(int(round(Storage.stopwatch.elapsed % 60, 1)))
        self.minutes.text = str(int(Storage.stopwatch.elapsed // 60))
        self.hours.text = str(int(Storage.stopwatch.elapsed // 3600))

    def reset_stopwatch(self):
        Storage.stopwatch.reset()
        self.update_labels()


class SubmitRun(Screen):
    workout = ObjectProperty(None)
    duration = ObjectProperty(None)
    calories = ObjectProperty(None)

    calculated_calories = 0

    def on_enter(self, *args):
        self.workout.text = "Workout: " + Storage.workout_type # BUG: not updating in screen for some reason
        Storage.workout_type = "" # reset workout_type as this may change
        time = str(int(Storage.stopwatch.elapsed // 3600)) + ' : ' 
        minutes = int(Storage.stopwatch.elapsed // 60) # used later for MET Calculation
        time += str(minutes) + ' : ' 
        time += str(int(round(Storage.stopwatch.elapsed % 60, 1))) + ' : '
        time += str(int(round(Storage.stopwatch.elapsed % 1, 2) * 100))

        self.duration.text = 'Duration: ' + time

        # MET Calculation for running in general w/o speed calculations (conflicts with walking)
        self.calculated_calories = (8 * 3.5 * float(Storage.stored_mass) / 200) * minutes

    def save(self):
        sql = 'INSERT INTO Workouts (user_id, exercise_id, calories_burned, distance, time) VALUES (%s, %s, %s, %s, %s)'
        data = (Storage.stored_user_id, 1, self.calculated_calories, 0, round(Storage.stopwatch.elapsed, 2))
        cur.execute(sql, data)
        conn.commit()
        Storage.stopwatch.reset()


class JoinGroup(Screen):
    pass


class CreateGroup(Screen):
    group = ObjectProperty(None)
    description = ObjectProperty(None)

    def create(self):
        sql = "INSERT INTO Groups (group_name, group_owner, group_description) VALUES (%s, %s, %s);"
        data = (self.group.text, Storage.stored_user_id, self.description.text)
        cur.execute(sql, data)
        conn.commit()
        self.group.text = ""
        self.description.text = ""
        show_popup("group_creation")

class Logs(Screen):
    pass

class TestRV(RecycleView):
    def __init__(self, **kwargs):
        super(TestRV, self).__init__(**kwargs)
        sample = [3, 6, 9, 12]
        self.data = [{'text': str(sample[i])} for i in range(len(sample))]


'''
Popups: ---------------------------------------
'''


class TextPopup(FloatLayout):
    popup_message = ObjectProperty(None)

def show_popup(message):
    show = TextPopup()
    show.popup_message.text = Storage.popup_messages[message]
    popupWindow = Popup(title="PowerPlant", content=show, size_hint=(0.5, 0.1))
    popupWindow.open()


'''  ------------------------------------------------------------       
'''

# read kv.txt into python
file = open('kv.txt').read()
kv = Builder.load_string(file)


class MyApp(App):
    def build(self):
        return kv


if __name__ == '__main__':
    MyApp().run()
    conn.close()
