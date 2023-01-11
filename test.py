import requests
import json


def test_register():
    url = "http://localhost:8004/api/auth/signup"

    payload = json.dumps({
        "userName": "fanyangli",
        "email": "1800017759@pku.edu.cn",
        "password": "123456"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


def login():
    url = "http://localhost:8004/api/auth/login"
    payload = json.dumps({
        "email": "1800017759@pku.edu.cn",
        "password": "123456"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return json.loads(response.text)["token"]


def test_find_user():
    token = login()
    url = "http://localhost:8004/api/friend/find-friends?userName=ll&page=1&size=4"
    headers = {
        'authorization': token
    }
    response = requests.request("GET", url, headers=headers)
    print(response.text)


def test_follow():
    token = login()
    url = "http://localhost:8004/api/friend/follow"
    headers = {
        'authorization': token
    }
    for uid in ['1737123891', '2068921703', '1882469954', '1397621265']:
        data = json.dumps({
            'uid': uid
        })
        response = requests.request("POST", url, headers=headers, data=data)
        print(response.text)

def test_unfollow():
    token = login()
    url = "http://localhost:8004/api/friend/unfollow"
    headers = {
        'authorization': token
    }
    # for uid in ['1737123891']:
    for uid in ['1737123891', '2068921703', '1882469954', '1397621265']:
        data = json.dumps({
            'uid': uid
        })
        response = requests.request("POST", url, headers=headers, data=data)
        print(response.text)

def test_follow_list():
    token = login()
    url = "http://localhost:8004/api/friend/my-friends?type=concerns&page=1&size=10"
    headers = {
        'authorization': token
    }
    response = requests.request("GET", url, headers=headers)
    print(response.text)
    

def test():
    url = "http://localhost:8004/api/test"

    response = requests.request("GET", url)
    print(response.text)


def test_post_weibo():
    token = login()
    url = "http://localhost:8004/api/weibo/send"
    payload = json.dumps({
        "message": "oooooooohhhhhh"
    })
    headers = {
        'Content-Type': 'application/json',
        'authorization': token
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)


def test_get_weibo():
    token = login()
    url = "http://localhost:8004/api/weibo?page=1&size=10"
    headers = {
        'authorization': token
    }
    response = requests.request("GET", url, headers=headers)
    print(response.text)
    t = json.loads(response.text)
    print(t)


if __name__ == '__main__':

    # test()
    # test_register()
    # test_find_user()
    # test_follow()
    # test_follow_list()
    # test_post_weibo()
    # test_get_weibo()
    # test_unfollow()
    # test_follow_list()


    # test_post_weibo()
    # get_weibo()
    ...
