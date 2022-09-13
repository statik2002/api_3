import argparse
import time
import sys
import requests
from urllib.parse import urljoin, urlsplit
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup
from pathlib import Path
from pprint import pprint


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def download_img(url, folder):

    response = requests.get(url)
    response.raise_for_status()

    check_for_redirect(response)

    filepath = Path(folder).joinpath(urlsplit(url)[2].split('/')[2])

    with open(filepath, 'wb') as file:
        file.write(response.content)


def download_txt(url, filename, folder):

    filepath = Path(folder).joinpath(
        f'{sanitize_filename(filename.strip())}_{url.split("=")[1].strip()}.txt'
    )
    response = requests.get(url)
    response.raise_for_status()

    check_for_redirect(response)

    with open(filepath, 'wb') as file:
        file.write(response.content)


def save_comments(folder, comments=[]):

    filepath = Path(folder).joinpath('комментарии.txt')

    with open(filepath, 'w') as file:
        if not comments:
            print('Нет комментариев', file=file)
        print(*comments, sep='\n', file=file)


def save_genres(folder, genres=[]):

    filepath = Path(folder).joinpath('жанры.txt')

    with open(filepath, 'w') as file:
        if not genres:
            print('Нет жанра', file=file)
        print(*genres, sep='\n', file=file)


def clear_string(string):
    return string.replace('\xa0', '')


def download_book(book, main_folder):

    book_folder_name = Path(main_folder).joinpath(book['book_name'])

    Path(book_folder_name).mkdir(exist_ok=True)

    download_img(book['book_image_url'], book_folder_name)
    download_txt(book['book_txt_url'], book['book_name'], book_folder_name)
    save_comments(book_folder_name, book['book_comments'])
    save_genres(book_folder_name, book['book_genres'])


def parse_book_page(url, page_soup):

    book_url = page_soup.find('a', text='скачать txt')
    if not book_url:
        return

    book_name, book_author = clear_string(
        page_soup.find('h1').text
        ).strip().split('::')

    book_image_url = page_soup.find(
        'div', class_='bookimage'
        ).find('a').find('img')

    book_txt_url = urljoin(url, book_url['href'])

    book_comments_raw = page_soup.find_all('div', class_='texts')
    book_comments = [comment.find("span", class_="black").text for comment in book_comments_raw]

    book_genres = list(page_soup.find('span', class_='d_book').find_all('a'))

    book = {
        'book_name': book_name,
        'book_author': book_author,
        'book_txt_url': book_txt_url if book_url else None,
        'book_image_url': urljoin(url, book_image_url["src"]),
        'book_comments': book_comments,
        'book_genres': [genre.text for genre in book_genres]
    }

    return book


def main():
    parser = argparse.ArgumentParser(
        description='Скрипт для скачивание книг с сайта https://tululu.org/',
    )
    parser.add_argument('start_id', help='с какой книги (число)', type=int)
    parser.add_argument('end_id', help='по какую книгу (число)', type=int)
    args = parser.parse_args()

    url = 'https://tululu.org/'

    main_folder = 'books'

    Path(main_folder).mkdir(exist_ok=True)

    for book_id in range(args.start_id, args.end_id):

        total_connection_try, current_connection_try = 5, 0

        while True and current_connection_try < total_connection_try:

            try:
                response = requests.get(urljoin(url, f'b{str(book_id)}/'))
                response.raise_for_status()

                check_for_redirect(response)
                soup = BeautifulSoup(response.text, 'lxml')

                book = parse_book_page(response.url, soup)

                download_book(book, main_folder)

                break

            except requests.exceptions.ConnectionError:
                print(f'Нет связи. Продолжим через 2 секунды, попыток - '
                      f'{current_connection_try} из {total_connection_try}')
                time.sleep(2)
                current_connection_try += 1

            except requests.exceptions.HTTPError:
                print('Неверный ответ от сервера')
                break

            except requests.exceptions.URLRequired:
                print('Неверный URL')
                sys.exit()

            except requests.exceptions.TooManyRedirects:
                print('Слишком много редиректов')
                break


if __name__ == '__main__':
    main()
