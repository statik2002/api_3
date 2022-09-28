import argparse
import json
import os
import time
import sys
import requests
from urllib.parse import urljoin, urlsplit
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup
from pathlib import Path


def check_for_redirect(response, scan_page=True):

    if scan_page:
        if response.history:
            return False
        else:
            return True
    else:
        if response.history:
            raise requests.HTTPError


def download_img(url, folder):

    response = requests.get(url)
    response.raise_for_status()

    check_for_redirect(response)

    filepath = Path(folder).joinpath(urlsplit(url)[2].split('/')[2])

    with open(filepath, 'wb') as file:
        file.write(response.content)

    return filepath


def download_txt(url, filename, folder):

    filepath = Path(folder).joinpath(
        f'{sanitize_filename(filename.strip())}'
        f'_{url.split("=")[1].strip()}.txt'
    )
    response = requests.get(url)
    response.raise_for_status()

    check_for_redirect(response)

    with open(filepath, 'wb') as file:
        file.write(response.content)

    return filepath


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


def download_book(book,
                  main_folder,
                  download_img_flag=True,
                  download_txt_flag=True
                  ):

    book_folder_name = Path(main_folder).joinpath(book['book_name'])

    Path(book_folder_name).mkdir(exist_ok=True)

    if download_img_flag:
        image_filepath = download_img(book['book_image_url'], book_folder_name)
    else:
        image_filepath = ''

    book['book_image_url'] = os.fspath(image_filepath)

    if download_txt_flag:
        txt_filepath = download_txt(
            book['book_txt_url'],
            book['book_name'],
            book_folder_name
        )
    else:
        txt_filepath = ''

    book['book_txt_url'] = os.fspath(txt_filepath)
    save_comments(book_folder_name, book['book_comments'])
    save_genres(book_folder_name, book['book_genres'])


def parse_book_page(url, page_soup):

    # Не нашел как эту конструкцию провернуть через select
    book_url = page_soup.find('a', text='скачать txt')
    if not book_url:
        return

    book_name, book_author = clear_string(
        page_soup.select_one('h1').text
    ).strip().split('::')

    book_image_url = page_soup.select_one(
        'div .bookimage a img[src]'
    )['src']

    book_txt_url = urljoin(url, book_url['href'])
    if not book_txt_url:
        return

    book_comments = [
        comment.text for comment in page_soup.select('div.texts span.black')
    ]

    book_genres = [genre.text for genre in page_soup.select('span.d_book a')]

    book = {
        'book_name': book_name.strip(),
        'book_author': book_author.strip(),
        'book_txt_url': book_txt_url if book_url else None,
        'book_image_url': urljoin(url, book_image_url),
        'book_comments': book_comments,
        'book_genres': book_genres,
    }

    return book


def get_books_links(url, start_page=1, end_page=999):

    book_links = []
    for page in range(start_page, end_page):
        response = requests.get(urljoin(url, str(page)))
        response.raise_for_status()

        if not check_for_redirect(response, scan_page=True):
            break

        soup = BeautifulSoup(response.text, 'lxml')

        books = soup.find_all('table', class_='d_book')

        for book in books:
            book_url = book.find('div', class_='bookimage').find('a')
            book_links.append(urljoin(url, book_url['href']))

    return book_links


def main():
    parser = argparse.ArgumentParser(
        description='Скрипт для скачивание книг с сайта https://tululu.org/',
    )
    parser.add_argument(
        '--start_page',
        help='с какой страницы качать (число)',
        type=int,
        default=1
    )
    parser.add_argument(
        '--end_page',
        help='по какую страницу качать (число)',
        type=int,
        default=9999
    )
    parser.add_argument(
        '--dest_folder',
        help='путь к папке для хранения книг',
        default='books'
    )
    parser.add_argument(
        '--skip_imgs',
        help='Не скачивать картинки',
        action='store_true'
    )
    parser.add_argument(
        '--skip_txt',
        help='Не скачивать книги',
        action='store_true'
    )
    parser.add_argument(
        '--json_path',
        help='Путь к файлу json с описанием книг',
        default='books'
    )
    args = parser.parse_args()

    sci_fi_url = 'https://tululu.org/l55/'

    img_download_flag = False if args.skip_imgs else True
    txt_download_flag = False if args.skip_txt else True

    book_catalog = []

    Path(args.dest_folder).mkdir(exist_ok=True)

    book_links = get_books_links(
        sci_fi_url,
        int(args.start_page),
        int(args.end_page)
    )

    print(*book_links, sep='\n')

    for book_link in book_links:

        total_connection_try, current_connection_try = 5, 0

        while True and current_connection_try < total_connection_try:

            try:
                response = requests.get(book_link)
                response.raise_for_status()

                check_for_redirect(response)
                soup = BeautifulSoup(response.text, 'lxml')

                book = parse_book_page(response.url, soup)
                if not book:
                    break

                download_book(
                    book,
                    args.dest_folder,
                    download_img_flag=img_download_flag,
                    download_txt_flag=txt_download_flag,
                )

                book_catalog.append(book)

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

    with open(Path(args.json_path).joinpath('books.json'), 'w') as books_file:
        books_file.write(json.dumps(book_catalog, ensure_ascii=False))


if __name__ == '__main__':
    main()
