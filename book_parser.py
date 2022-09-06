import os.path
import requests
from urllib.parse import urljoin, urlsplit, unquote
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def download_img(url, folder='images/'):

    response = requests.get(url)

    if not os.path.exists(folder):
        os.makedirs(folder)

    filepath = os.path.join(folder, urlsplit(url)[2].split('/')[2])

    with open(unquote(filepath), 'wb') as file:
        file.write(response.content)


def download_txt(url, filename, folder='books/'):
    filepath = os.path.join(folder,
                            f'{sanitize_filename(filename.strip())}_{url.split("=")[1].strip()}.txt'
                            )

    response = requests.get(url)

    try:
        check_for_redirect(response)

        if not os.path.exists(folder):
            os.makedirs(folder)

        with open(filepath, 'wb') as file:
            file.write(response.content)

    except:
        pass


def download_comments(url):
    pass

url = 'https://tululu.org/b'

for i in range(1, 10):

    response = requests.get(f'{url}{str(i)}/')
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'lxml')

    book_name = soup.find('h1').text.split('::')[0]
    book_url = soup.find('a', text='скачать txt')
    if book_url:
        #download_txt(f'{url[:-2]}{book_url["href"]}', book_name)
        #book_image_url = soup.find('div', class_='bookimage').find('a').find('img')
        #if book_image_url:
        #    download_img(urljoin(url, book_image_url["src"]))

        #book_comments = soup.find_all('div', class_='texts')
        #print(book_name)
        #for comment in book_comments:
        #    print(f'-- {comment.find("span", class_="black").text}')

        print(book_name)
        book_genres = soup.find('span', class_='d_book').find_all('a')
        for genre in book_genres:
            print(genre.text, end=',')
