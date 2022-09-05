import requests
import os


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


url = "https://tululu.org/txt.php?id="

dirs = 'books'
if not os.path.exists(dirs):
    os.makedirs(dirs)

for i in range(1, 11):

    response = requests.get(url + str(i))

    try:
        check_for_redirect(response)
        filename = f'{dirs}/id{str(i)}.txt'
        with open(filename, 'wb') as file:
            file.write(response.content)
    except:
        pass
