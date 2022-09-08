import argparse
import os.path
import requests
from urllib.parse import urljoin, urlsplit, unquote
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup
from pprint import pprint


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

    if not os.path.exists(folder):
        os.makedirs(folder)

    with open(filepath, 'wb') as file:
        file.write(response.content)


def save_comments(folder='comments/', comments=[]):

    if not os.path.exists(folder):
        os.makedirs(folder)

    filepath = os.path.join(folder, 'комментарии.txt')

    with open(unquote(filepath), 'w') as file:
        if not comments:
            print('Нет комментариев', file=file)
        print(*comments, sep='\n', file=file)


def save_genres(folder='genres/', genres=[]):

    if not os.path.exists(folder):
        os.makedirs(folder)

    filepath = os.path.join(folder, 'жанры.txt')

    with open(unquote(filepath), 'w') as file:
        if not genres:
            print('Нет жанра', file=file)
        print(*genres, sep='\n', file=file)


def clear_string(string):
    return string.replace('\xa0', '')


def parse_book_page(url, page_soup):

    book = dict()

    book['name'] = clear_string(page_soup.find('h1').text.split('::')[0]).strip()
    book['author'] = clear_string(page_soup.find('h1').text.split('::')[1]).strip()

    book_url = page_soup.find('a', text='скачать txt')
    if book_url:
        download_txt(
                    urljoin(url[:-1], book_url["href"]),
                    filename=book["name"],
                    folder=f'books/{book["name"]}/'
                    )
        book['txt_url'] = f'{url[:-2]}{book_url["href"]}'

        book_image_url = page_soup.find('div', class_='bookimage').find('a').find('img')
        if book_image_url:
            download_img(
                        urljoin(url, book_image_url["src"]),
                        folder=f'books/{book["name"]}/'
                        )
            book['image'] = urljoin(url, book_image_url["src"])

        book_comments = page_soup.find_all('div', class_='texts')
        comments = []
        for comment in book_comments:
            comments.append(comment.find("span", class_="black").text)
        save_comments(folder=f'books/{book["name"]}/', comments=comments)
        book['comments'] = comments

        genres = []
        book_genres = list(page_soup.find('span', class_='d_book').find_all('a'))
        for genre in book_genres:
            genres.append(genre.text)

        save_genres(folder=f'books/{book["name"]}/', genres=genres)
        book['genres'] = genres

        pprint(book)


def main():
    parser = argparse.ArgumentParser(
        description='Скрипт для скачивание книг с сайта https://tululu.org/',
    )
    parser.add_argument('start_id', help='с какой книги (число)', type=int)
    parser.add_argument('end_id', help='по какую книгу (число)', type=int)
    args = parser.parse_args()

    url = 'https://tululu.org/'

    for book_id in range(args.start_id, args.end_id):

        response = requests.get(f'{url}b{str(book_id)}/')
        response.raise_for_status()

        try:
            check_for_redirect(response)
            soup = BeautifulSoup(response.text, 'lxml')

            parse_book_page(url, soup)

        except requests.HTTPError as exception:
            print(f'Книга №{i} - Error: {exception}')


if __name__ == '__main__':
    main()
