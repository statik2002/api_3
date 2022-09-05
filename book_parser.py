import os.path

import requests
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup


def download_txt(url, filename, folder='books/'):
    return os.path.join(folder, f'{sanitize_filename(filename)}.txt')

url = 'https://tululu.org/b1/'

response = requests.get(url)
response.raise_for_status()

soup = BeautifulSoup(response.text, 'lxml')

book, author = soup.find('h1').text.split('::')

print(f'Заголовок: {book.strip()}\nАвтор: {author.strip()}')

print(download_txt('https://tululu.org/txt.php?id=1', 'Али\\би', folder='txt/'))
