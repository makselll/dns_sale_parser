import json
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests


def get_products(search: str, last_page) -> list:
    """
    Данная программа позволяет находить товары с самой большой скидкой.
    Прикольно использовать ее на какие-то праздники, по типу Нового-года, Черной пятницы.
    Вбиваете товар, который нужно найти и кол-во страниц. Можете вбить очень большое число,
    тогда программа будет искать до последней страницы
    """
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0'
    }
    page = 1
    items = [ ]
    while True:
        print(page)
        url = f'https://www.dns-shop.ru/search/?q={search}&p={page}&order=popular&stock=all'
        session = requests.session()
        session.headers.update(headers)

        rs = session.get(url)
        data = json.loads(rs.text)
        root = BeautifulSoup(data['html'], 'html.parser')
        pages = root.find_all('li',{'class': 'pagination-widget__page'})
        real_lat_page = pages[-1].attrs["data-page-number"]
        if last_page > int(real_lat_page):
            last_page = int(real_lat_page)
        for a in root.select('.product-info__title-link > a'):
            rs = session.get(urljoin(rs.url, a['href']))
            root = BeautifulSoup(rs.text, 'html.parser')
            current_price = root.find('span', {'class': 'current-price-value'}).text.strip().replace(' ', '')
            try:
                prev_price = root.select_one('.prev-price-total').text.strip().replace(' ', '')
            except AttributeError:
                prev_price = current_price

            sale = int(prev_price) - int(current_price)
            sale_in_proc = sale * 100 / int(current_price)

            items.append(
                (a.get_text(strip=True), sale_in_proc, sale, prev_price, current_price, urljoin(rs.url, a['href']))
            )
        page = page + 1
        if page == last_page:
            break
    return items


if __name__ == '__main__':
    print(get_products.__doc__)
    name = input('Что будем искать?\n: ')
    page = int(input('Сколько страниц мне просматреть ?\n: '))
    items = get_products(name, page)

    items.sort(key=lambda i: i[1], reverse = True)
    print(f'Search {name!r}...')
    print(f'  Result ({len(items)}):')
    for title,sale_in_proc, sale,prev_price, current_price, url in items:
        print(f'    {title!r}: Скидка:{"%.2f" % sale_in_proc}% - {sale} Руб Цена до скидки:{prev_price} Руб. Цена со скидкой:{current_price} Руб. {url}')
    print()
