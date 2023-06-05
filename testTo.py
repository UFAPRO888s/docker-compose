
import requests

url = 'http://45.154.24.65:8080/token'
myobj = {

    "username": "johndoe",
    "full_name": "John Doe",
    "email": "johndoe@example.com",
    "hashed_password": "fakehashedsecret",
    "disabled": False,

}

xAAA = requests.post(url, json=myobj)

print(xAAA.text)
