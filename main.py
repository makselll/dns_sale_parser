import json
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests


def dns(search, min_price, max_price):
    print('Dns')
    page = 1
    while True:
        print(page)
        url = f'https://www.dns-shop.ru/search/?q={search}&p={page}&order=popular&stock=all&price={min_price}-{max_price}'
        session = requests.session()
        session.headers.update(headers)
        rs = session.get(url)
        data = json.loads(rs.text)
        if data['html'] is None:
            print('Товар не найден')
            break
        else:
            soup = BeautifulSoup(data['html'], 'lxml')
            all_pages = soup.find_all('li',{'class': 'pagination-widget__page'})
            if all_pages:  # Если код с пагинацией найден
                last_page = all_pages[-1].attrs["data-page-number"]
            else:
                last_page = 1
            for tag_a in soup.select('.product-info__title-link > a'):
                title = tag_a.text
                href = urljoin(rs.url, tag_a['href'])
                rs = session.get(href)
                soup = BeautifulSoup(rs.text, 'lxml')
                current_price = soup.find('span', {'class': 'current-price-value'}).text.strip().replace(' ', '')
                try:
                    prev_price = soup.select_one('.prev-price-total').text.strip().replace(' ', '')
                except AttributeError:  # Скидки на данный товар нет
                    continue
                sale_in_rub = int(prev_price) - int(current_price)
                sale_in_percent = 100 - round(int(current_price) * 100 / int(prev_price), 2)
                items[title] = {
                    'shop': 'Dns',
                    'href': href,
                    'sale_in_percent': sale_in_percent,
                    'sale_in_rub': str(sale_in_rub) + ' Руб.',
                    'prev_price': prev_price + ' Руб.',
                    'current_price': current_price + ' Руб.',
                    }
            if page == int(last_page):
                return items
            page = page + 1
    return {}


def wildberries(search, min_price, max_price):
    print('Wildberries')
    page = 1
    while True:
        print(page)
        url = f'https://www.wildberries.ru/catalog/0/search.aspx?price={min_price};{max_price}&subject=657&search={search}&page={page}'
        session = requests.get(url, headers)
        soup = BeautifulSoup(session.text, 'lxml')
        if soup.find('p', {'class': 'searching-results-text'}):
            print('Товар не найден')
            return items
        else:
            products = soup.find_all('div', {'class': "dtList i-dtList j-card-item"})
            for product in products:
                title = product.find('span', {'class': "goods-name"}).text
                href = product.find('a', {'class': 'ref_goods_n_p'})[ 'href' ]
                try:
                    current_price = product.find('span', {'class': 'lower-price'}).text.strip().replace('\xa0', '').replace(
                        '₽', '')
                    continue
                except AttributeError:
                    current_price = product.find('ins', {'class': 'lower-price'}).text.strip().replace('\xa0', '').replace(
                        '₽', '')
                    prev_price = product.find('span', {'class': 'price-old-block'}).text.replace('\xa0', '')
                    prev_price = prev_price[ :prev_price.find('₽') ]

                sale_in_rub = int(prev_price) - int(current_price)
                sale_in_percent = 100 - round(int(current_price) * 100 / int(prev_price), 2)
                items[title] = {
                  'shop': 'Wildberries',
                  'href': href,
                  'sale_in_percent': sale_in_percent,
                  'sale_in_rub': str(sale_in_rub) + ' Руб.',
                  'prev_price': prev_price + ' Руб.',
                  'current_price': current_price + ' Руб.',
                    }
            try:
                soup.find('a', {'class': 'next'}).text  # Последняя страница
            except AttributeError:
                break
            page = page + 1
    return items


def citilink (search, min_price, max_price):
    print('Citilink')
    page = 1
    while True:
        print(page)
        url = f'https://www.citilink.ru/search/?text={search}&p={page}'
        session = requests.get(url, headers)
        soup = BeautifulSoup(session.text, 'lxml')
        products = soup.find_all('div', {'class': "ddl_product"})
        for product in products:
            title = product.find('a', {'class': "ddl_product_link"}).text
            href = product.find('a', {'class': 'ddl_product_link'})[ 'href' ]
            try:
                current_price = product.find('span', {'class': 'subcategory-product-item__price_standart'}).\
                    text.replace(' ','').replace('руб.', '').strip()
                prev_price = product.find('span', {'class': 'subcategory-product-item__price_old'}).\
                    text.replace(' ', '').replace('руб.', '').strip()
            except AttributeError:
                continue
            if int(current_price) > max_price or int(current_price) < min_price:
                continue
            sale_in_rub = int(prev_price) - int(current_price)
            sale_in_percent = 100 - round(int(current_price) * 100 / int(prev_price), 2)
            items[title] = {
                'shop': 'Citilink',
                'href': href,
                'sale_in_percent': sale_in_percent,
                'sale_in_rub': str(sale_in_rub) + ' Руб.',
                'prev_price': prev_price + ' Руб.',
                'current_price': current_price + ' Руб.',
                }
        if not soup.findAll('li', {'class': 'next'}):  # Если больше нет следующих станиц
            break
        page = page + 1
    return items


def ozon (search, min_price, max_price):
    print('Ozon')
    page = 1
    counter = 0
    while True:
        print(page)
        url = f"https://www.ozon.ru/search?deny_category_prediction=true&from_global=true&price={min_price}.000%3B{max_price}.000&sorting=discount&page={page}&text={search} "
        session = requests.get(url, headers)
        soup = BeautifulSoup(session.text, 'lxml')
        products = soup.find_all('div', {'class': "a3d0 a3d9 a3d2"})
        products_count = int(soup.find('div', {'class': 'a3q3'}).text.split(' ')[-2])
        for product in products:
            counter += 1
            try:  # Если товар закончился - пропускаем
                int(product.find('span', {'class': 'a4o2'}).text.replace('%', '').replace('\u2212', '').strip())
            except:
                continue
            title = product.find('span', {'data-test-id': "tile-name"}).text.strip()
            href = 'https://www.ozon.ru' + product.find('a', {'class': 'a3c9'})[ 'href' ]
            current_price = product.find('span', {'data-test-id': 'tile-price'}).text.replace('\u2009', '').replace(
                '₽', '').strip()
            prev_price = product.find('div', {'data-test-id': 'tile-discount'}).text.replace('\u2009', '').replace('₽', '').strip()
            sale_in_percent = int(product.find('span', {'class': 'a4o2'}).text.replace('%', '').replace('\u2212', '').strip())
            sale_in_rub = int(prev_price) - int(current_price)
            items[ title ] = {
                'shop': 'Citilink',
                'href': href,
                'sale_in_percent': sale_in_percent,
                'sale_in_rub': str(sale_in_rub) + ' Руб.',
                'prev_price': prev_price + ' Руб.',
                'current_price': current_price + ' Руб.',
                }
        if products_count == counter:  # Если обошел все найденные товар - выключаем
            break
        page = page + 1
    return items


if __name__ == '__main__':
    """
    Данная программа позволяет находить товары с самой большой скидкой.
    Прикольно использовать ее на какие-то праздники, по типу Нового-года, Черной пятницы.
    Вбиваете товар, который нужно найти, Кол-во страниц, Минимальную цену и Максимальную цену. Можете вбить очень большое число,
    тогда программа будет искать до последней страницы
    """
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0'
        }
    items = {}

    search = input('Что будем искать?\n: ')
    min_price = int(input('Минимальная цена ?\n: '))
    max_price = int(input('Максимальная цена ?\n: '))

    items.update(wildberries(search, min_price, max_price))
    items.update(dns(search, min_price, max_price))
    items.update(citilink(search, min_price, max_price))
    items.update(ozon(search, min_price, max_price))

    items = {key: items[key] for key in sorted(items, key=lambda x: (items[x]['sale_in_percent']), reverse=True)}

    with open("result.json", "w", encoding='utf-8') as write_file:
        json.dump(items, write_file, indent=4, ensure_ascii=False,)



