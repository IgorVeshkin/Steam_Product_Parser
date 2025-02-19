# Steam Product Parser

## Описание

Проект производит парсинг данных товаров со Steam. На данном этапе разработки реализован функционал парсинга (`Standalone`, `Standalone + DLC/Soundtack`, `Bundle`). Проект находится в разработке

>[!NOTE]  
> На текущий момент парсинг `bundle` производит только сбор данных продуктов, включенных в набор. Данные `bundle` не собираются

## Основные технологии проекта
Язык программирования: `Python 3.12`

Проект был разработан с использованием библиотек `BeautifulSoup4`, `Selenium`

## Установка проекта
Выполните команду `pip install -r requirements.txt` для установки всех зависимойстей проекта в виртуальную среду

## Основные скрипты

На момент последней публикации проект состоит из 4 скриптов:

__main.py__ </br>
- __Описание:__ В данном скрипте реализован основной функционал парсинга товаров площадки `Steam` (ранний вариант). Парсинг только отдельного конкретного товара.

__steam_bundle_parser.py__ </br>
- __Описание:__ Скрипт реализует функционал парсинга наборов товаров. Поддержка как парсинга одиночного товара, так и набора. Основан на скрипте `main.py`.

__steam_bundle_parser_v2.py__ </br>
- __Описание:__ В данную итерацию парсера был добавлен функционал парсинга товаров, у которых отсутствует информация об издателе. Был разработан функционал, предотвращаяющий многократный парсинг основного товара.

> [!NOTE]  
> 
> __Проблема мультипарсинга__
> 
> Если происходит парсинг товаров в составе `bundle`, то без должного мониторинга данных при парсинге `DLC/Soundtrack` будет производиться парсинг `Standalone` товара, непосредственно связанного с дополнительным контентом, данные которого ранее уже были получены.

__steam_bundle_parser_v3.py__ </br>
- __Описание:__ В данном скрипте были убраны ненужные и излишнее выводы информации в терминал. Использована библиотека `pprint` для отображения сложных структур данных (структура, выводимая после завершения работы парсера).