from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

url = 'https://tululu.org/l55/'

for page in range(1, 5):

    response = requests.get(urljoin(url, str(page)))
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'lxml')

    books = soup.find_all('table', class_='d_book')

    for book in books:
        book_url = book.find('div', class_='bookimage').find('a')
        print(urljoin(url, book_url['href']))
