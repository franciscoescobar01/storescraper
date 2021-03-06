import logging
from decimal import Decimal

from bs4 import BeautifulSoup

from storescraper.product import Product
from storescraper.store import Store
from storescraper.categories import RAM, HEADPHONES, COMPUTER_CASE, MONITOR, \
    MOUSE, STEREO_SYSTEM, MOTHERBOARD, PROCESSOR, PROJECTOR, \
    SOLID_STATE_DRIVE, VIDEO_CARD, KEYBOARD, PRINTER, STORAGE_DRIVE, NOTEBOOK
from storescraper.utils import session_with_proxy, remove_words


class SetupSpace(Store):
    @classmethod
    def categories(cls):
        return [
            RAM,
            HEADPHONES,
            COMPUTER_CASE,
            MONITOR,
            MOUSE,
            STEREO_SYSTEM,
            MOTHERBOARD,
            PROCESSOR,
            PROJECTOR,
            SOLID_STATE_DRIVE,
            KEYBOARD,
            PRINTER,
            VIDEO_CARD,
            NOTEBOOK,
            STORAGE_DRIVE
        ]

    @classmethod
    def discover_urls_for_category(cls, category, extra_args=None):
        url_extensions = [
            ['ram', RAM],
            ['audifonos', HEADPHONES],
            ['gabinetes', COMPUTER_CASE],
            ['monitores', MONITOR],
            ['mouse', MOUSE],
            ['parlantes', STEREO_SYSTEM],
            ['placa-madre', MOTHERBOARD],
            ['procesadores', PROCESSOR],
            ['proyectores', PROJECTOR],
            ['ssd', SOLID_STATE_DRIVE],
            ['ssd-1', SOLID_STATE_DRIVE],
            ['m2-sata', SOLID_STATE_DRIVE],
            ['m2-nvme', SOLID_STATE_DRIVE],
            ['hdd', STORAGE_DRIVE],
            ['tarjeta-de-video', VIDEO_CARD],
            ['teclados', KEYBOARD],
            ['impresoras', PRINTER],
            ['gaming', VIDEO_CARD],
            ['notebook', NOTEBOOK],
        ]

        session = session_with_proxy(extra_args)
        products_urls = []
        for url_extension, local_category in url_extensions:
            if local_category != category:
                continue
            page = 1
            while True:
                if page > 10:
                    raise Exception('page overflow: ' + url_extension)
                url_webpage = 'https://setupspace.cl/collections/{}?page={}' \
                    .format(url_extension, page)

                data = session.get(url_webpage).text
                soup = BeautifulSoup(data, 'html.parser')
                product_containers = soup.findAll('div', 'product-wrap')

                if not product_containers:
                    if page == 1:
                        logging.warning('Empty category: ' + url_webpage)
                    break
                for container in product_containers:
                    product_url = container.find('a')['href']
                    products_urls.append('https://setupspace.cl' + product_url)
                page += 1

        return products_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        response = session.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        name = soup.find('h1', 'product_name').text
        sku = soup.find('input', {'name': 'id'})['value'].strip()
        if not soup.find('span', 'current_price').find('span', 'money'):
            return []
        normal_price = Decimal(remove_words(
            soup.find('span', 'current_price').find('span', 'money').text))
        offer_price = normal_price

        stock_container = soup.find(
            'form', 'shopify-product-form').find('div', 'items_left')

        if not stock_container:
            return []

        if stock_container.text == '':
            stock = -1
        else:
            stock = int(stock_container.text.split()[0])

        picture_urls = []

        for tag in soup.findAll('a', 'lightbox'):
            picture_urls.append('https:' + tag['href'].split('?')[0])

        p = Product(
            name,
            cls.__name__,
            category,
            url,
            url,
            sku,
            stock,
            normal_price,
            offer_price,
            'CLP',
            sku=sku,
            picture_urls=picture_urls
        )
        return [p]
