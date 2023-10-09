import requests

email = input("Email: ")
password = input("Password: ")

data = {
    "email":email,"password":password
}

endpoint = "http://127.0.0.1:8000/api/token/"

login = requests.post(endpoint, data=data)

try:
    if login.status_code == 200:
        print("User succesfully logged in")
    elif login.status_code == 401 or login.status_code == 400:
        print("Enter a valid email and password")
except Exception as e:
    raise e