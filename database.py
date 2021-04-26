import json
import pyrebase
from datetime import date

firebaseConfig = {'apiKey': "AIzaSyDdqZKZMQhSWO8KFiO-8azjyH42N91UuLg",
                  'authDomain': "focus-bda7e.firebaseapp.com",
                  'projectId': "focus-bda7e",
                  'databaseURL': "https://focus-bda7e-default-rtdb.firebaseio.com/",
                  'storageBucket': "focus-bda7e.appspot.com",
                  'messagingSenderId': "999898533530",
                  'appId': "1:999898533530:web:c60c6c9e5f3db3ef5f9923",
                  'measurementId': "G-95VXE5XTS9"}

firebase = pyrebase.initialize_app(firebaseConfig)

db = firebase.database()
auth = firebase.auth()
storage = firebase.storage()


#def main():
#    loginScreen()

global email

"""
def loginScreen():
    valid = 0
    while not valid:
        action = input("Login or Signup: ")
        if action[0].upper() == 'L':
            login()
            valid = 1
        elif action[0].upper() == 'S':
            signup()
            valid = 1
        else:
            print("Invalid Selection")
"""

def login():
    global email
    loginEmail = input("Enter email: ")
    loginPassword = input("Enter password: ")
    try:
        user = auth.sign_in_with_email_and_password(loginEmail, loginPassword)
        print("Successful sign in")
        email = loginEmail
    except Exception as e:
        error_json = e.args[1]
        error = json.loads(error_json)['error']
        print(error['message'])


def signup():
    signupEmail = input("Enter your email: ")
    signupPassword = input("Enter a password: ")
    confirmPass = input("Comfirm your password: ")
    if signupPassword == confirmPass:
        try:
            auth.create_user_with_email_and_password(signupEmail, signupPassword)
            print("Successful sign up")
            login()
        except Exception as e:
            error_json = e.args[1]
            error = json.loads(error_json)['error']
            print(error['message'])
    else:
        print("Passwords do not match")

def updateDatebase(blinking, napping):
    global email
    userID = email.replace(".", ",")
    today = date.today()
    db.child("users").child(userID).child("Data").child(today).update(blinking)
    db.child("users").child(userID).child("Data").child(today).update(napping)
