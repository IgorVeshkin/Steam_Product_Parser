# Старт разработки: 08/01/2025

# Импорт BeautifulSoup - библиотеки для парсинга данных с web-страницы
from bs4 import BeautifulSoup
# Импорт Selenium - библиотеки для автоматизированого взаимодействия со страницей
from selenium import webdriver

# TODO: Сделать парсинг для bundle, поскольку там содержатся несколько товаров и вид страницы другой (Выполнено)

def steam_item_parser(url: str = 'https://store.steampowered.com/app/598700/The_Vagrant/') -> None:
    # Создаю объект selenuim
    driver = webdriver.Edge()

    # Перехожу на сайт
    driver.get(url)

    # Передаю html-код страницы в BeautifulSoup и создаю объект на основе полученных данных
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Получаю тело страницы
    body = soup.body

    # Название продукта
    product_name = body.find('div', {'id': 'appHubAppName'}).text

    # Описание продукта
    product_description_element = body.find('div', {'class': 'game_description_snippet'})

    product_description = None

    # Если элемент описания найден, то это полноценный цифровой товар (не dlc),
    # иначе в блоке будет указано, что требуется steam-версия другого продукта для запуска
    if product_description_element:
        product_description = product_description_element.text.replace('\n', '').strip()

    product_type = 'Standalone'

    dlc_body = body.find('div', {'class': 'game_area_dlc_bubble'})

    # Если товар - это дополнительный контент (dlc)
    if dlc_body:
        dlc_body = body.find('div', {'class': 'game_area_dlc_bubble'})

        # Если товар - это дополнительный контент (dlc) (Дополнительная проверка)
        if dlc_body:
            # Корректирую значение соответствующего пункта
            # Чтобы получить данные подтверждающие, что товар - это dlc, можно использовать следующую конструкцию: dlc_body.h1.text
            product_type = 'DLC'

    # Проверка есть ли саунтрек
    soundtrack_body = body.find('div', {'class': 'game_area_soundtrack_bubble'})

    # Если товар - это саундтрек
    if soundtrack_body:
        # Корректирую значение соответствующего пункта
        # Чтобы получить данные подтверждающие, что товар - это саундтрек, можно использовать следующую конструкцию: soundtrack_body.h1.text
        product_type = 'Soundtrack'

    # Список разработчиков продукта (Первый способ получить название разработчика продукта)
    # product_developers_list = body.find('div', {'id': 'developers_list'}).a.text

    # Список издателей продукта
    # Нахожу все div с классом dev_row. В одном хранится название разработчика, в другом название издаетеля
    product_dev_and_pub = body.find_all('div', {'class': 'dev_row'})

    product_publisher = 'No data'
    product_developers_list = 'No data'

    for instance in product_dev_and_pub:
        data_columns = instance.find_all('div')

        # Второй способ получить название разработчика продукта

        # В data_columns[0].text хранятся пояснение (разработчик или издатель)
        if 'Разработчик' in data_columns[0].text:
            product_developers_list = data_columns[1].a.text

        if 'Издатель' in data_columns[0].text:
            product_publisher = data_columns[1].a.text
            break

    # Дата выхода продукта
    release_date = body.find('div', {'class': 'release_date'}).find('div', {'class': 'date'}).text

    # Ссылка на изображение продукта
    product_header_image_cover_url = body.find('img', {'class': 'game_header_image_full'})['src']

    print('Название продукта:', product_name)
    # Вывожу описание продукта, только если оно найдено
    print('Описание продукта:', product_description) if product_description is not None else None
    print('Тип продукта:', product_type)
    print('Список разработчиков продукта:', product_developers_list)
    print('Издатель продукта:', product_publisher)

    # Блок получения цен (начало)

    # в div c классом game_purchase_action_bg хранятся данные цены продукта
    # Содержание div корректируется в зависимости есть ли скидка или нет

    price_body = body.find('div', {'class': 'game_purchase_action_bg'})

    # Если первый найденный блок содержит кнопку с текстом 'Загрузить'

    try:
        if price_body.div.a.span.text == 'Загрузить':
            print('Первый блок это загрузка демо-версии...\n')

            # Получаю все блоки и пропускаю первый, поскольку это загрузка демо-версии
            price_body = body.find_all('div', {'class': 'game_purchase_action_bg'})[1]
    except AttributeError as attr_error:
        pass

    price_no_discount = price_body.find('div', {'class': 'game_purchase_price'})

    # Ошибка возникает по причине того, что тег div с классом 'game_purchase_action_bg' также присутствует
    # в div с загрузкой демо-версии продукта, если демо-версия есть
    # Необходима проверка блока демо-версии

    # Текст ошибки:
    # File "D:\Documents\Python_files\Steam_Product_Parser\main.py", line 291, in main
    #     original_price = price_body.find('div', {'class': 'discount_original_price'}).text
    #                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    # AttributeError: 'NoneType' object has no attribute 'text'

    # Если цена найдена (точно скидки нет)...
    if price_no_discount:
        # Первый способ получения цены товара
        print("На данный момент товар идет без скидки по цене (1-ый способ):",
              price_no_discount.text.replace('\n', '').strip())

        # Второй способ получения цены товара
        print("На данный момент товар идет без скидки по цене (2-ой способ):",
              int(price_no_discount['data-price-final']) / 100)

        # Для более подробного понимания структуры страницы раскомментировать нижнию строчку и посмотреть структуру блока 'game_purchase_action_bg'
        # print('price_body', price_body, end='\n\n')

    else:
        discount_percentage = price_body.find('div', {'class': 'discount_pct'})

        # Проверка лишняя поскольку если price_no_discount (товар точно без скидки) не найдена, то товар точно будет по скидке
        # Если блок скидки в процентах найден...
        # if discount_percentage:

        # то точно должна быть обычная цена и скидочная

        # Обычная цена
        original_price = price_body.find('div', {'class': 'discount_original_price'}).text

        # Скидочная цена (Способ получения №1 с припиской 'руб.')
        discount_price = price_body.find('div', {'class': 'discount_final_price'}).text

        # Скидочная цена и размер скидки в процентах (Способ получения №2)
        discount_block = price_body.find('div', {'class': 'discount_block'})

        discount_price_v2 = int(discount_block['data-price-final']) / 100
        discount_percentage_v2 = int(discount_block['data-discount'])

        # Вывод данных цены
        print('Скидочная цена:', discount_price)
        print('Обычная цена:', original_price)
        print('Размер скидки на товар:', discount_percentage.text)

        # Вывод данных цены (Способ №2)
        print('Скидочная цена (способ №2):', discount_price_v2)
        print('Размер скидки на товар (способ №2):', discount_percentage_v2)

    # Блок получения цен (конец)

    print('Дата выхода продукта:', release_date)
    print('Ссылка заглавного изображения продукта:', product_header_image_cover_url)


def main():
    # Updated at 10/01/2025: Дополнительный контент различается между собой,
    # так доп. контент это один тип, а саундтрек - другой
    # Они отображаются по разному

    # Updated at 10/01/2025: На данный момент саундтреки тоже парсятся, но без запуска парсинга основного продукта
    # Тип остается Standalone

    # Updated at 10/01/2025: Буквально через полторы минуты разобрался в чем дело:
    # Дополнительный контент Я проверял по div с классом 'game_area_dlc_bubble'
    # А в случае с саунтреком нужно искать div с классом 'game_area_bubble'
    # div с классом 'game_area_dlc_bubble' и div с классом 'game_area_bubble' различаются по цвету!!!
    # Или можно использовать второй класс того же div-тега 'game_area_soundtrack_bubble' (Его и использую)

    # Ссылка на товар (standalone)
    url = 'https://store.steampowered.com/app/598700/The_Vagrant/'

    # Ссылка на товар (dlc)
    # url = 'https://store.steampowered.com/app/888360/The_Vagrant_Artbook/'

    # Ссылка на товар (dlc)
    # url = 'https://store.steampowered.com/app/930200/The_Vagrant_Cosplay_Album/'


    # url = 'https://store.steampowered.com/app/1701520/Afterimage/'


    # Пример №2

    # Ссылка на товар (есть демо-версия)
    # url = 'https://store.steampowered.com/app/2527500/MiSide/'

    # Ссылка на товар (soundtrack)
    # url = 'https://store.steampowered.com/app/3404450/MiSide_Soundtrack/'

    # Создаю объект selenuim
    driver = webdriver.Edge()

    # Перехожу на сайт
    driver.get(url)

    # Передаю html-код страницы в BeautifulSoup и создаю объект на основе полученных данных
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Получаю тело страницы
    body = soup.body

    # Элемент содержащий текст 'Купить {Название игры}': body.find('div', {'class': 'game_area_purchase_game'}).h1.text
    # Может возникнуть при условии, что блок стрима по игре отдаляет основную информацию товара от названия

    # Название продукта
    product_name = body.find('div', {'id': 'appHubAppName'}).text

    # Описание продукта
    product_description_element = body.find('div', {'class': 'game_description_snippet'})

    product_description = None

    # Если элемент описания найден, то это полноценный цифровой товар (не dlc),
    # иначе в блоке будет указано, что требуется steam-версия другого продукта для запуска
    if product_description_element:
        product_description = product_description_element.text.replace('\n', '').strip()

    # Тип продукта
    product_type = 'Standalone'

    standalone_product_for_dlc_url = None

    dlc_body = body.find('div', {'class': 'game_area_dlc_bubble'})

    # Если dlc_body возвращает None, это не значит, что товар не является dlc
    # Поскольку 'game_area_dlc_bubble' - это дополнительный контент, а класс 'game_area_bubble' - это саундтрек
    # Или можно использовать второй класс того же div-элемента 'game_area_soundtrack_bubble'

    # Если товар - это дополнительный контент (dlc)
    if dlc_body:
        # Корректирую значение соответствующего пункта
        # Чтобы получить данные подтверждающие, что товар - это dlc, можно использовать следующую конструкцию: dlc_body.h1.text
        product_type = 'DLC'

        standalone_product_for_dlc_url = dlc_body.p.a['href']

    # Проверка есть ли саунтрек
    soundtrack_body = body.find('div', {'class': 'game_area_soundtrack_bubble'})

    # Если товар - это саундтрек
    if soundtrack_body:
        # Корректирую значение соответствующего пункта
        # Чтобы получить данные подтверждающие, что товар - это саундтрек, можно использовать следующую конструкцию: soundtrack_body.h1.text
        product_type = 'Soundtrack'

        standalone_product_for_dlc_url = soundtrack_body.p.a['href']

    # Список разработчиков продукта (Первый способ получить название разработчика продукта)
    # product_developers_list = body.find('div', {'id': 'developers_list'}).a.text

    # Список издателей продукта
    # Нахожу все div с классом dev_row. В одном хранится название разработчика, в другом название издаетеля
    product_dev_and_pub = body.find_all('div', {'class': 'dev_row'})

    product_publisher = 'No data'
    product_developers_list = 'No data'


    for instance in product_dev_and_pub:
        data_columns = instance.find_all('div')

        # Второй способ получить название разработчика продукта

        # В data_columns[0].text хранятся пояснение (разработчик или издатель)
        if 'Разработчик' in data_columns[0].text:
            product_developers_list = data_columns[1].a.text

        if 'Издатель' in data_columns[0].text:
            product_publisher = data_columns[1].a.text
            break

    # Дата выхода продукта
    release_date = body.find('div', {'class': 'release_date'}).find('div', {'class': 'date'}).text

    # Ссылка на изображение продукта

    product_header_image_cover_url = body.find('img', {'class': 'game_header_image_full'})['src']

    print('Название продукта:', product_name)
    # Вывожу описание продукта, только если оно найдено
    print('Описание продукта:', product_description) if product_description is not None else None
    print('Тип продукта:', product_type)
    print('Список разработчиков продукта:', product_developers_list)
    print('Издатель продукта:', product_publisher)


    # Блок получения цен (начало)

    # в div c классом game_purchase_action_bg хранятся данные цены продукта
    # Содержание div корректируется в зависимости есть ли скидка или нет

    price_body = body.find('div', {'class': 'game_purchase_action_bg'})

    # Если первый найденный блок содержит кнопку с текстом 'Загрузить'

    try:
        if price_body.div.a.span.text == 'Загрузить':
            print('Первый блок это загрузка демо-версии...\n')

            # Получаю все блоки и пропускаю первый, поскольку это загрузка демо-версии
            price_body = body.find_all('div', {'class': 'game_purchase_action_bg'})[1]
    except AttributeError as attr_error:
        pass

    price_no_discount = price_body.find('div', {'class': 'game_purchase_price'})

    # Ошибка возникает по причине того, что тег div с классом 'game_purchase_action_bg' также присутствует
    # в div с загрузкой демо-версии продукта, если демо-версия есть
    # Необходима проверка блока демо-версии

    # Текст ошибки:
    # File "D:\Documents\Python_files\Steam_Product_Parser\main.py", line 291, in main
    #     original_price = price_body.find('div', {'class': 'discount_original_price'}).text
    #                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    # AttributeError: 'NoneType' object has no attribute 'text'

    # Если цена найдена (точно скидки нет)...
    if price_no_discount:
        # Первый способ получения цены товара
        print("На данный момент товар идет без скидки по цене (1-ый способ):",
              price_no_discount.text.replace('\n', '').strip())

        # Второй способ получения цены товара
        print("На данный момент товар идет без скидки по цене (2-ой способ):",
              int(price_no_discount['data-price-final']) / 100)

        # Для более подробного понимания структуры страницы раскомментировать нижнию строчку и посмотреть структуру блока 'game_purchase_action_bg'
        # print('price_body', price_body, end='\n\n')

    else:
        discount_percentage = price_body.find('div', {'class': 'discount_pct'})

        # Проверка лишняя поскольку если price_no_discount (товар точно без скидки) не найдена, то товар точно будет по скидке
        # Если блок скидки в процентах найден...
        # if discount_percentage:

        # то точно должна быть обычная цена и скидочная

        # Обычная цена
        original_price = price_body.find('div', {'class': 'discount_original_price'}).text

        # Скидочная цена (Способ получения №1 с припиской 'руб.')
        discount_price = price_body.find('div', {'class': 'discount_final_price'}).text

        # Скидочная цена и размер скидки в процентах (Способ получения №2)
        discount_block = price_body.find('div', {'class': 'discount_block'})

        discount_price_v2 = int(discount_block['data-price-final']) / 100
        discount_percentage_v2 = int(discount_block['data-discount'])

        # Вывод данных цены
        print('Скидочная цена:', discount_price)
        print('Обычная цена:', original_price)
        print('Размер скидки на товар:', discount_percentage.text)

        # Вывод данных цены (Способ №2)
        print('Скидочная цена (способ №2):', discount_price_v2)
        print('Размер скидки на товар (способ №2):', discount_percentage_v2)


    # Блок получения цен (конец)


    print('Дата выхода продукта:', release_date)
    print('Ссылка заглавного изображения продукта:', product_header_image_cover_url)

    # Если ссылка на оригинальный товар для dlc была успешно получена, то
    if standalone_product_for_dlc_url:
        # Вывод ссылки на оригинальный товар, если текущий - это dlc
        print('\nСсылка на продукт, с которым работает dlc:', standalone_product_for_dlc_url, end='\n\n')

        print('Продукт, с которым работает dlc:')

        # Парсю данные оригинального товара
        steam_item_parser(url=standalone_product_for_dlc_url)

if __name__ == '__main__':
    main()
