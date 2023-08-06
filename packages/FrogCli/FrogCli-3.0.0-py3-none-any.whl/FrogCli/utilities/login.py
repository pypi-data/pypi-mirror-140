import json
from getpass import getpass


with open("FrogCli/utilities/login.json", "r") as outfile:
    _user_data = json.load(outfile)

_is_logged_in = _user_data['is_login']


def login():
    loop = True
    if _is_logged_in == 'False':
        while loop:
            user_name = input("Username: ")
            password = getpass("Password: ")
            if _user_data['user_name'] == user_name and _user_data['password'] == password:
                print(f"Logged in successfully as {user_name}")
                loop = False
                _user_data['is_login'] = 'True'
                with open("FrogCli/utilities/login.json", "w") as outfile:
                    json.dump(_user_data, outfile)
                outfile.close()
            else:
                print("Username / Password incorrect")

