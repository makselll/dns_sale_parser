import json
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests


def dns(search: str, last_page, min_price, max_price) -> list:
    print('Dns')
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0'
    }
    page = 1
    while True:
        print(page)
        url = f'https://www.dns-shop.ru/search/?q={search}&p={page}&order=popular&stock=all&price={min_price}-{max_price}'
        session = requests.session()
        session.headers.update(headers)

        rs = session.get(url)
        data = json.loads(rs.text)
        root = BeautifulSoup(data['html'], 'lxml')
        pages = root.find_all('li',{'class': 'pagination-widget__page'})
        real_lat_page = pages[-1].attrs["data-page-number"]
        if last_page > int(real_lat_page):
            last_page = int(real_lat_page)
        for a in root.select('.product-info__title-link > a'):
            rs = session.get(urljoin(rs.url, a['href']))
            root = BeautifulSoup(rs.text, 'lxml')
            current_price = root.find('span', {'class': 'current-price-value'}).text.strip().replace(' ', '')
            try:
                prev_price = root.select_one('.prev-price-total').text.strip().replace(' ', '')
            except AttributeError:
                continue

            sale = int(prev_price) - int(current_price)
            sale_in_proc = 100 - int(current_price) * 100 / int(prev_price)

            items.append(
                (a.get_text(strip=True), sale_in_proc, sale, prev_price, current_price, urljoin(rs.url, a['href']))
            )
        page = page + 1
        if page == last_page:
            break
    return items


def wildberries (search: str, last_page, min_price, max_price) -> list:
    print('Wildberries')
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0'
        }
    page = 1
    while True:
        print(page)
        url = f'https://www.wildberries.ru/catalog/0/search.aspx?price={min_price};{max_price}&subject=657&search={search}&page={page}'
        session = requests.get(url, headers)
        soup = BeautifulSoup(session.text, 'lxml')
        products = soup.find_all('div', {'class': "dtList i-dtList j-card-item"})
        real_last_page = soup.find('p', {'class': 'searching-results-text'})

        if real_last_page:
            break
        elif page == last_page:
            break
        for item in products:
            title = item.find('span', {'class': "goods-name"}).text
            href = item.find('a', {'class': 'ref_goods_n_p'})[ 'href' ]
            try:
                current_price = item.find('span', {'class': 'lower-price'}).text.strip().replace('\xa0', '').replace(
                    '₽', '')
                continue
            except AttributeError:
                current_price = item.find('ins', {'class': 'lower-price'}).text.replace('\xa0', '').replace('₽', '')
                prev_price = item.find('span', {'class': 'price-old-block'}).text.replace('\xa0', '')
                prev_price = prev_price[ :prev_price.find('₽') ]

            sale = int(prev_price) - int(current_price)
            sale_in_proc = 100 - int(current_price) * 100 / int(prev_price)
            items.append((title, sale_in_proc, sale, prev_price, current_price, href))
        page = page + 1
    return items

def citilink (search: str, last_page, min_price, max_price) -> list:
    print('Citilink')
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0'
        }
    page = 1
    while True:
        print(page)
        url = f'https://www.citilink.ru/search/?text={search}&p={page}'
        session = requests.get(url, headers)
        soup = BeautifulSoup(session.text, 'lxml')
        products = soup.find_all('div', {'class': "ddl_product"})
        real_last_page = int(soup.find('li', {'class': 'last'}).text)
        if page == real_last_page or page == last_page:
            break
        for item in products:
            title = item.find('a', {'class': "ddl_product_link"}).text
            href = item.find('a', {'class': 'ddl_product_link'})[ 'href' ]
            try:
                current_price = item.find('span', {'class': 'subcategory-product-item__price_standart'}).\
                    text.replace(' ','').replace('руб.', '').strip()
                prev_price = item.find('span', {'class': 'subcategory-product-item__price_old'}).\
                    text.replace(' ', '').replace('руб.', '').strip()
            except AttributeError:
                continue
            if int(current_price) > max_price or int(current_price) < min_price:
                continue
            sale = int(prev_price) - int(current_price)
            sale_in_proc = 100 - int(current_price) * 100 / int(prev_price)
            items.append((title, sale_in_proc, sale, prev_price, current_price, href))
        page = page + 1
    return items

def ozon (search: str, min_price, max_price) -> list:
    print('Ozon')
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0'
        }
    page = 1
    end = False
    while end is False:
        print(page)
        url = f'https://www.ozon.ru/category/videokarty-15721/?price={min_price}.000%3B{max_price}.000&text={search}&sorting=discount&from_global=true&page={page}'
        session = requests.get(url, headers)
        soup = BeautifulSoup(session.text, 'lxml')
        products = soup.find_all('div', {'class': "tile m-list m-border"})
        for item in products:
            title = item.find('span', {'data-test-id': "tile-name"}).text.strip()
            href = 'https://www.ozon.ru' + item.find('a', {'class': 'tile-wrapper'})[ 'href' ]
            try:
                current_price = item.find('span', {'data-test-id': 'tile-price'}).text.replace('\u2009', '').replace(
                    '₽', '').strip()
                prev_price = item.find('div', {'data-test-id': 'tile-discount'}).text.replace('\u2009', '').replace('₽', '').strip()
                sale_in_proc = item.find('div', {'class': 'a1n3'}).text.replace('%', '').replace('\u2212', '').strip()
            except AttributeError:
                end = True
            sale = int(prev_price) - int(current_price)
            items.append((title, int(sale_in_proc), sale, prev_price, current_price, href))
        page = page + 1
    return items


if __name__ == '__main__':
    """
    Данная программа позволяет находить товары с самой большой скидкой.
    Прикольно использовать ее на какие-то праздники, по типу Нового-года, Черной пятницы.
    Вбиваете товар, который нужно найти, Кол-во страниц, Минимальную цену и Максимальную цену. Можете вбить очень большое число,
    тогда программа будет искать до последней страницы
    """
    name = input('Что будем искать?\n: ')
    page = int(input('Сколько страниц мне просматреть ?\n: '))
    min_price = int(input('Минимальная цена ?\n: '))
    max_price = int(input('Максимальная цена ?\n: '))
    items = []
    items = wildberries(name, page, min_price, max_price)
    items = items + dns(name, page, min_price, max_price)
    items = items + citilink(name, page, min_price, max_price)
    items = items + ozon(name, min_price, max_price)
    items.sort(key=lambda i: i[1], reverse = True)

    print(f'Search {name!r}...')
    print(f'  Result ({len(items)}):')
    for title,sale_in_proc, sale,prev_price, current_price, url in items:
        print(f'    {title!r}: Скидка:{"%.2f" % sale_in_proc}% - {sale} Руб Цена до скидки:{prev_price} Руб. Цена со скидкой:{current_price} Руб. {url}')
    print()
