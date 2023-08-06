import requests
import pyrebase

url = "https://get-edu-default-rtdb.firebaseio.com/"
api = "cNJEo3IzeldpLz4NWV7m3DSJ6t2jmkcpNVJ8BNPh"

config = {
    "apiKey": "AIzaSyDEvdQ05NmnxyGqakwlqPObyGGgTmQr7lQ",
    "authDomain": "get-edu.firebaseapp.com",
    "databaseURL": "https://get-edu-default-rtdb.firebaseio.com",
    "projectId": "get-edu",
    "storageBucket": "get-edu.appspot.com",
    "messagingSenderId": "999546458038",
    "appId": "1:999546458038:web:a5b1858e830ebbd8ce3b17",
    "measurementId": "G-5ZJ4JJ5MWJ"
}
firebase = pyrebase.initialize_app(config)
storage = firebase.storage()

class Account():

    def fix(username):
        username = username.replace("/", "")
        username = username.replace(" ", "")
        username = username.lower()
        return username

    def valid(username):
        find_url = "https://get-edu-default-rtdb.firebaseio.com/Account/{}/.json".format(username)
        all_data = requests.get(find_url + '?auth=' + api)
        data = all_data.json()

        if data is None:
            return False

        else:
            return True

    def create(username, name, password):
        if name == "" or username == "" or password == "":
            return "Invalid"

        else:

            if len(password) >= 8:
                username = Account.fix(username)
                name = name.replace("/", "")
                password = password.replace("/", "")

                account_url = url + "Account/.json"
                flag = Account.valid(username)

                if flag == False:
                    user_data = {username: {"username": username, "name": name, "password": password, "buy": ["none"], "sell": ["none"]}}
                    requests.patch(url=account_url, json=user_data)
                    return "Success"

                else:
                    return "This username already exists. Please login."

            else:
                return "Password must be more than 8 words"

class Course():

    def create(id, name, owner):
        owner = Account.fix(owner)
        name = name.replace("/", "")
        id = Account.fix(id)

        flag = Account.valid(owner)

        if flag == True:
            course_url = url + "Course/.json"
            find_url = "https://get-edu-default-rtdb.firebaseio.com/Course/{}/.json".format(id)
            all_data = requests.get(find_url + '?auth=' + api)
            data = all_data.json()

            if data is None:
                course_data = {id: {"id": id, "name": name, "owner": owner, "videos": ["none"], "participants": ["none"], "payments": ["none"]}}
                requests.patch(url=course_url, json=course_data)

                account_url = url + "Account/.json"

                find_acc_url = "https://get-edu-default-rtdb.firebaseio.com/Account/{}/.json".format(owner)
                all_info = requests.get(find_acc_url + '?auth=' + api)
                info = all_info.json()
                info_list = list(info.values())

                buy = info_list[0]
                sell = info_list[3]
                sell.append(id)

                if buy[0] == "none":
                
                    if sell[0] == "none":
                        user_data = {owner: {"username": owner, "name": info_list[1], "password": info_list[2], "buy": ["none"], "sell": [id]}}
                
                    else:
                        user_data = {owner: {"username": owner, "name": info_list[1], "password": info_list[2], "buy": ["none"], "sell": sell}}
                
                else:
                
                    if sell[0] == "none":
                        user_data = {owner: {"username": owner, "name": info_list[1], "password": info_list[2], "buy": buy, "sell": [id]}}
                
                    else:
                        user_data = {owner: {"username": owner, "name": info_list[1], "password": info_list[2], "buy": buy, "sell": sell}}

                requests.patch(url=account_url, json=user_data)
                return "Success"

            else:
                return "Course id already exists."

        else:
            return "No user found. Please create an account."

    def myCourses(username):
        username = Account.fix(username)
        find_url = "https://get-edu-default-rtdb.firebaseio.com/Account/{}/.json".format(username)
        all_data = requests.get(find_url + '?auth=' + api)
        data = all_data.json()
        data_list = list(data.values())
        return data_list[3]

    def paidCourses(username):
        username = Account.fix(username)
        find_url = "https://get-edu-default-rtdb.firebaseio.com/Account/{}/.json".format(username)
        all_data = requests.get(find_url + '?auth=' + api)
        data = all_data.json()
        data_list = list(data.values())
        return data_list[0]

class Payment():

    def pay(id, screenshot, username):
        id = Account.fix(id)
        username = Account.fix(username)

        path = "Courses/{0}/{1}".format(id, username)
        storage.child(path).put(screenshot)
        url = storage.child(path).get_url(None)

        find_acc_url = "https://get-edu-default-rtdb.firebaseio.com/Account/{}/.json".format(username)
        all_info = requests.get(find_acc_url + '?auth=' + api)
        info = all_info.json()
        info_list = list(info.values())

        course_url = "https://get-edu-default-rtdb.firebaseio.com/Course/{}/.json".format(id)
        all_data = requests.get(course_url + '?auth=' + api)
        data = all_data.json()
        data_list = list(data.values())

        buy = info_list[0]
        sell = info_list[3]

        try:
            buy.remove(id)

            if buy == []:
                buy = ["none"]

        except:
            buy.append(id)

        if buy[0] == "none":
            user_data = {username: {"username": username, "name": info_list[1], "password": info_list[2], "buy": [id], "sell": sell}}
        
        else:
            user_data = {username: {"username": username, "name": info_list[1], "password": info_list[2], "buy": buy, "sell": sell}}

        if data_list[2] != username:
            acc_url = "https://get-edu-default-rtdb.firebaseio.com/Account/.json"
            requests.patch(url=acc_url, json=user_data)
            name = data_list[1]
            owner = data_list[2]
            participants = data_list[3]
            payments = data_list[4]
            videos = data_list[5]

            try:
                participants.remove("none")
                payments.remove("none")
                
                try:
                    participants.remove(username)
                    payments.remove(url)

                    participants.append(username)
                    payments.append(url)

                    course_data = {id: {"id": id, "name": name, "owner": owner, "videos": videos, "participants": participants, "payments": payments}}
                    course_link = "https://get-edu-default-rtdb.firebaseio.com/Course/.json"
                    requests.patch(url=course_link, json=course_data)
                    return "Success"
                    
                except:
                    participants.append(username)
                    payments.append(url)

                    course_data = {id: {"id": id, "name": name, "owner": owner, "videos": videos, "participants": participants, "payments": payments}}
                    course_link = "https://get-edu-default-rtdb.firebaseio.com/Course/.json"
                    requests.patch(url=course_link, json=course_data)
                    return "Success"

            except:

                try:
                    participants.remove(username)
                    payments.remove(url)

                    participants.append(username)
                    payments.append(url)

                    course_data = {id: {"id": id, "name": name, "owner": owner, "videos": videos, "participants": participants, "payments": payments}}
                    course_link = "https://get-edu-default-rtdb.firebaseio.com/Course/.json"
                    requests.patch(url=course_link, json=course_data)
                    return "Success"

                except:
                    participants.append(username)
                    payments.append(url)

                    course_data = {id: {"id": id, "name": name, "owner": owner, "videos": videos, "participants": participants, "payments": payments}}
                    course_link = "https://get-edu-default-rtdb.firebaseio.com/Course/.json"
                    requests.patch(url=course_link, json=course_data)
                    return "Success"

        else:
            return "You're buying your own course!"

    def fetch(id, username):
        id = Account.fix(id)
        username = Account.fix(username)

        course_url = "https://get-edu-default-rtdb.firebaseio.com/Course/{}/.json".format(id)
        all_data = requests.get(course_url + '?auth=' + api)
        data = all_data.json()
        data_list = list(data.values())

        if data_list[2] == username:
            participants = data_list[3]
            payments = data_list[4]

            data_dict = {}
            
            for i in range(0, len(participants)):
                data_dict[str(participants[i])] = str(payments[i])

            return data_dict

        else:
            return "Permission denied."