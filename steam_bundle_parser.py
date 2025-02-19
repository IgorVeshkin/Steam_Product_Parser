# Скрипт создан: 16/01/2025

# Импорт BeautifulSoup - библиотеки для парсинга данных с web-страницы
from bs4 import BeautifulSoup
# Импорт Selenium - библиотеки для автоматизированого взаимодействия со страницей
from selenium import webdriver
# Обработка текста для получения данных (например, числовых значений цены товара)
import re

# TODO: При использовании парсера открывается много окон, поскольку из ранее открытых окон данные уже получены, нужно разработать способ закрытия окон браузера
def steam_item_parser(url: str = 'https://store.steampowered.com/app/598700/The_Vagrant/') -> dict:
    # Создаю объект selenuim
    driver = webdriver.Edge()

    # Перехожу на сайт
    driver.get(url)

    # Передаю html-код страницы в BeautifulSoup и создаю объект на основе полученных данных
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Получаю тело страницы
    body = soup.body

    # Блок названия продукта
    product_name = body.find('div', {'id': 'appHubAppName'})

    # Блок названия bundle-а
    bundle_title_block = body.find('h2', {'class': 'pageheader'})


    # Если блок названия bundle-а существует, значит обрабатываю товар как bundle
    # Информацию о bundle пока не храню, получаю отдельные товары в bunlde-е
    if bundle_title_block:

        print('Название bundle:', bundle_title_block.text)

        # Получаю список блоков всех продуктов bundle
        bundle_products_list = body.find_all('div', {'class': 'bundle_package_item'})

        # Получаю ссылки на продукты, входящие в bundle
        bundle_products_urls = list(map(lambda x: x.div.a['href'], bundle_products_list))

        print('Количество товаров в bundle:', len(bundle_products_list))
        print('Ссылки на продукты, хранящиеся в bundle:', bundle_products_urls, end='\n\n')

        # Формирую данные для bundle
        bundle_items_data = dict(Standalone=[], DLC=[], Soundtrack=[])

        for product_url in bundle_products_urls:

            # Получаю данные товаров по очереди
            current_product = steam_item_parser(url=product_url)

            # Если после выполнения функции steam_item_parser,
            # функция вернула структуру формата dict(Standalone=[], DLC=[], Soundtrack=[]),

            # Значит есть DLC/Soundtrack + Original_Game
            if 'Standalone' in current_product.keys():

                # Если ни одна запись не была добавлена в Standalone
                if not bundle_items_data['Standalone']:
                    bundle_items_data['Standalone'].append(current_product['Standalone'])


                # Если записи в Standalone присутствуют
                else:
                    # И текущей среди их нет (код работает проверил)
                    if current_product['Standalone'] not in bundle_items_data['Standalone']:
                        print('Not Present in my Standalone structure!!!')
                        bundle_items_data['Standalone'].append(current_product['Standalone'])


                # Поскольку все dlc и саундтреки - это уникальные записи в рамках бандла (bundle),
                # проверку на их присутствие в финальной структуре проводить не нужно
                if current_product['DLC'] is not None:
                    bundle_items_data['DLC'].append(current_product['DLC'])

                if current_product['Soundtrack'] is not None:
                    bundle_items_data['Soundtrack'].append(current_product['Soundtrack'])

                continue

            # Если функция steam_item_parser вернула структуры standalone-продукта, то добавляю её в общий перечень (если текущий товар не был представлен в перечне)
            if current_product not in bundle_items_data['Standalone']:
                bundle_items_data['Standalone'].append(current_product)


        # print('Структура bundle:', bundle_items_data)

        # print('\nТовар является бандлом (bundle). На данный момент, обработки ссылок с bundle нет. Прекращаю выполнение программы...')

        return bundle_items_data

    # Если продукт не является bundle-ом, то работаю как с обычным товаром
    product_name = product_name.text

    # Описание продукта
    product_description_element = body.find('div', {'class': 'game_description_snippet'})

    product_description = None

    # Если элемент описания найден, то это полноценный цифровой товар (не dlc),
    # иначе в блоке будет указано, что требуется steam-версия другого продукта для запуска
    if product_description_element:
        product_description = product_description_element.text.replace('\n', '').strip()

    product_type = 'Standalone'

    # Если продукт является дополнительным контентом (DLC или Soundtrack),
    # то необходимо хранить ссылку на оригинальный товар, с которым работает дополнение

    standalone_product_for_dlc_url = None

    dlc_body = body.find('div', {'class': 'game_area_dlc_bubble'})

    # Если dlc_body возвращает None, это не значит, что товар не является dlc
    # Поскольку 'game_area_dlc_bubble' - это дополнительный контент, а класс 'game_area_bubble' - это саундтрек
    # Или можно использовать второй класс того же div-элемента 'game_area_soundtrack_bubble'

    # Если товар - это дополнительный контент (dlc)
    if dlc_body:
        dlc_body = body.find('div', {'class': 'game_area_dlc_bubble'})

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
        # Updated at 02/02/2025: IndexError возникает по причине отсутствия данных об издателе (произвожу отслеживание таких ситуаций, использую try-except)
        try:
            if 'Разработчик' in data_columns[0].text:
                product_developers_list = data_columns[1].a.text

            if 'Издатель' in data_columns[0].text:
                product_publisher = data_columns[1].a.text
                break
        except IndexError as error:
            print(f'\nДанные издателя для товара \'{product_name}\' отсутствуют')

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

    # Текст ошибки: UnboundLocalError: cannot access local variable 'discount_price_v2' where it is not associated with a value
    # Чтобы избедать ошибку переношу переменные price_no_discount_rub, discount_price_v2, discount_percentage_v2 в глобальное поле

    price_no_discount_rub = None

    discount_price_v2 = None
    discount_percentage_v2 = None


    # Если цена найдена (точно скидки нет)...
    if price_no_discount:
        # Первый способ получения цены товара
        print("На данный момент товар идет без скидки по цене (1-ый способ):",
              price_no_discount.text.replace('\n', '').strip())

        # Второй способ получения цены товара
        print("На данный момент товар идет без скидки по цене (2-ой способ):",
              int(price_no_discount['data-price-final']) / 100)

        price_no_discount_rub = int(price_no_discount['data-price-final']) / 100

        # Для более подробного понимания структуры страницы раскомментировать нижнию строчку и посмотреть структуру блока 'game_purchase_action_bg'
        # print('price_body', price_body, end='\n\n')


    else:
        discount_percentage = price_body.find('div', {'class': 'discount_pct'})

        # Проверка лишняя поскольку если price_no_discount (товар точно без скидки) не найдена, то товар точно будет по скидке
        # Если блок скидки в процентах найден...
        # if discount_percentage:

        # то точно должна быть обычная цена и скидочная

        # Обычная цена (В самом steam можно получить оригинальную цену без скидки только в виде текста формата '99 руб.')
        original_price = price_body.find('div', {'class': 'discount_original_price'}).text

        # Получаю числовое значение цены
        original_price = float(re.findall(r'\d+', original_price)[0])

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
        original_product_parsed_data = steam_item_parser(url=standalone_product_for_dlc_url)

        # Формирую данные для bundle
        parsed_item_data = dict(Standalone=None, DLC=None, Soundtrack=None)

        # Данные оригинального проекта для DLC сохраняю в соответсвующем блоке словаря
        parsed_item_data['Standalone'] = original_product_parsed_data

        # Данные DLC помещяю в соответсвующий раздел
        parsed_item_data[product_type] = {
                'name': product_name,
                'developer': product_developers_list,
                'publisher': product_publisher,
                'release_date': release_date,
                'original_price': price_no_discount_rub if price_no_discount_rub else original_price,
                'discount_price': discount_price_v2 if discount_price_v2 else None,
                'discount_percentage': discount_percentage_v2 if discount_percentage_v2 else None,
                'cover_url': product_header_image_cover_url,
                'original_product_name': original_product_parsed_data['name'],
            }

        # print('\nFormedData:', parsed_item_data)

        return parsed_item_data


    # Формирую данные отдельной записи
    parsed_item_data = {
            'name': product_name,
            'developer': product_developers_list,
            'publisher': product_publisher,
            'release_date': release_date,
            'original_price': price_no_discount_rub if price_no_discount_rub else original_price,
            'discount_price': discount_price_v2 if discount_price_v2 else None,
            'discount_percentage': discount_percentage_v2 if discount_percentage_v2 else None,
            'cover_url': product_header_image_cover_url
        }

    # print('\nFormedData:', parsed_item_data)

    return parsed_item_data

def main():
    # Ссылка на товар (standalone)
    url = 'https://store.steampowered.com/app/598700/The_Vagrant/'

    # Ссылка на товар (dlc)
    url = 'https://store.steampowered.com/app/888360/The_Vagrant_Artbook/'

    # Ссылка на товар (dlc)
    url = 'https://store.steampowered.com/app/930200/The_Vagrant_Cosplay_Album/'

    # Ссылка на товар (bundle)
    url = 'https://store.steampowered.com/bundle/7650/The_Vagrant_Bundle/'

    # url = 'https://store.steampowered.com/app/1701520/Afterimage/'

    # Ссылка на товар (есть демо-версия)
    # url = 'https://store.steampowered.com/app/2527500/MiSide/'

    # Ссылка на товар (soundtrack)
    # url = 'https://store.steampowered.com/app/3404450/MiSide_Soundtrack/'

    # Ссылка на товар (soundtrack по скидке на 16/01/2025)
    # url = 'https://store.steampowered.com/app/916000/Hollow_Knight__Gods__Nightmares/'

    # Ссылка на bundle, в котором в начале идет dlc, а потом сам товар (для проверки заполнения Standalone-продукта через dlc)
    # Bundle, где необходимо провести проверку на отсутствии издателя
    # url = 'https://store.steampowered.com/bundle/28404/Frontier_hunter__Tower_hunter__Deluxe_Edition/'

    # DLC, где необходимо провести проверку на отсутствии издателя
    # url = 'https://store.steampowered.com/app/2177420/Pogranichnyj_oxotnik__DLC__Newbie_Prop_Pack/'

    # Ссылка на bundle (Только игры, standalone)
    # url = 'https://store.steampowered.com/bundle/22179/Pixel_Perfect_Bundle/'

    # Ссылка на bundle (standalone, dlc, soundtrack)
    # url = 'https://store.steampowered.com/bundle/15234/The_Igas_Back_Bundle/'

    # Ссылка на bundle (Только dlc)
    # url = 'https://store.steampowered.com/bundle/40875/Bloodstained_Ritual_of_the_Night__Miriams_Complete_Cosmetic_Bundle/'

    parsed_product = steam_item_parser(url=url)

    print('Структура спарсенного товара:', parsed_product)

if __name__ == '__main__':
    main()