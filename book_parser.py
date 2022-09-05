import os.path
import requests
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def download_txt(url, filename, folder='books/'):
    filepath = os.path.join(folder, f'{sanitize_filename(filename)}.txt')

    response = requests.get(url)

    try:
        check_for_redirect(response)

        if not os.path.exists(folder):
            os.makedirs(folder)

        # Добавить функционал id для неуникальных фалов
        with open(filepath, 'wb') as file:
            file.write(response.content)

    except:
        pass


url = 'https://tululu.org/b'

for i in range(1, 10):

    response = requests.get(f'{url}{str(i)}/')
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'lxml')

    book_name = soup.find('h1').text.split('::')[0]
    book_url = soup.find('a', text='скачать txt')
    if book_url:
        print(book_url['href'])
        download_txt(f'{url[:-2]}{book_url["href"]}', book_name)
