import requests
from bs4 import BeautifulSoup

url = 'https://tululu.org/b1/'

response = requests.get(url)
response.raise_for_status()

soup = BeautifulSoup(response.text, 'lxml')

book, author = soup.find('h1').text.split('::')

print(f'Заголовок: {book.strip()}\nАвтор: {author.strip()}')
