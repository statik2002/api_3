import requests
from bs4 import BeautifulSoup

url = 'https://www.franksonnenbergonline.com/blog/are-you-grateful/'

response = requests.get(url)
response.raise_for_status()

soup = BeautifulSoup(response.text, 'lxml')

print(soup.find('main').find('header').find('h1').text)

print(soup.find('img', class_='attachment-post-image')['src'])

print(soup.find('div', class_='entry-content'))
