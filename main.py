import requests
import os

url = "https://tululu.org/txt.php?id="

dirs='books'
if not os.path.exists(dirs):
    os.makedirs(dirs)

for i in range(1, 11):

    response = requests.get(url+str(i))
    response.raise_for_status()

    filename = f'{dirs}/id{str(i)}.txt'
    with open(filename, 'wb') as file:
        file.write(response.content)