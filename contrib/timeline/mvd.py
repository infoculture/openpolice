#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Парсер страницы истории с официального сайта МВД РФ. Возвращает json, приведённый к формату TimelineJS.
'''

# Настройки
BASE_URL = 'http://www.mvd.ru' # Адрес сайта МВД РФ
URL = '%s/mvd/history/' % BASE_URL # Адрес страницы истории

import urllib2, json, re, argparse, os
from bs4 import BeautifulSoup as bs

def fetch(url):
    'Получить web-страницу по URL'
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    return response.read()

# Месяцы года на русском языке в родительном падеже, в нижнем регистре
MONTHS_PARENTAL = (
    u'января',
    u'февраля',
    u'марта',
    u'апреля',
    u'мая',
    u'июня',
    u'июля',
    u'августа',
    u'сентября',
    [u'октября',
        u'oктябpя', # Тут некоторые символы - латинские вместо русских
    ],
    u'ноября',
    u'декабря',
)

# Они же в именительном
MONTHS = (
    u'январь',
    u'февраль',
    u'март',
    u'апрель',
    u'май',
    u'июнь',
    u'июль',
    u'август',
    u'сентябрь',
    u'октябрь',
    u'ноябрь',
    u'декабрь',
)

# Полугодия
HALVES = (
    u'первое',
    u'второе',
)

def parse_month(month, months):
    'Преобразование названия месяца в его номер (1-12)'
    
    month = month.decode('utf-8').lower()
    
    for index, variants in enumerate(months):
        if month == variants:
            return index + 1

        elif (type(variants) in (list, tuple)) and (month in variants):
            return index + 1

    raise Exception('Не удалось распознать месяц: ' + month)

def d(date):
    'Формат даты из tuple(DD, MM, YY) в YYYY,MM,DD'

    date = list(date)
    date.reverse()

    return ','.join(map(str, date))

def parse_date(raw):
    'Парсинг даты или диапазона дат'

    # Очистка от левых символов
    raw = raw.replace(u'–', u'-').encode('utf-8')

    chunks = None

    # Шаблоны регулярных выражений для месяцев, лет, дней
    DAY = '(\d+)'
    MONTH = '([^ -]+)'
    YEAR = '(\d{4})'
    G = '(г\.|года|\.)' # завершение даты

    # 10 января 1928 г.
    match = re.match(r'^%s *%s *%s *%s$' % (DAY, MONTH, YEAR, G), raw)
    if match:
        chunks = match.groups()

        # Очистка даты
        date = d([
            int(chunks[0]),
            parse_month(chunks[1], MONTHS_PARENTAL),
            int(chunks[2])
        ])

        return date, date

    # 25 октября (8 ноября) 1917 г.
    # Старый стиль, указанный в скобках, игнорируем
    match = re.match(r'^%s *%s (\([^\)]+\))* *%s *%s$' % (DAY, MONTH, YEAR, G), raw)
    if match:
        chunks = match.groups()

        # Очистка даты
        date = d([
            int(chunks[0]),
            parse_month(chunks[1], MONTHS_PARENTAL),
            int(chunks[3])
        ])

        return date, date
    
    # 'Январь 1928 г.'
    match = re.match(r'^%s *%s *%s$' % (MONTH, YEAR, G), raw)
    if match:
        chunks = match.groups()

        date = d([
            1, # 1 число месяца
            parse_month(chunks[0], MONTHS), # месяца
            int(chunks[1]) # года
        ])

        return date, date

    # '1928 г.'
    match = re.match(r'%s *%s$' % (YEAR, G), raw)
    if match:
        chunks = match.groups()

        date = d([
            1, # 1 число
            1, # января
            int(chunks[0]) # Указанного года
        ])
        
        return date, date

    # 16, 17 января 1811 г.
    # 29-31 января 1920 г.
    # 23 – 29 июня 1937 г.
    match = re.match(r'^%s *[,\-] *%s *%s *%s *%s$' % (DAY, DAY, MONTH, YEAR, G), raw)
    if match:
        chunks = match.groups()

        month = parse_month(chunks[2], MONTHS_PARENTAL)
        year  = int(chunks[3])

        return d([
            int(chunks[0]),
            month,
            year
        ]), d([
            int(chunks[1]),
            month,
            year
        ])

    # Март-апрель 1928 г.
    # Июль – Август 1823 г.
    match = re.match(r'^%s *[,\-] *%s *%s *%s$' % (MONTH, MONTH, YEAR, G), raw)
    if match:
        chunks = match.groups()

        year = int(chunks[2])

        return d([
            1,
            parse_month(chunks[0], MONTHS),
            year
        ]), d([
            1,
            parse_month(chunks[1], MONTHS),
            year
        ])

    # 30 июля - 1 августа 1918 г.
    match = re.match(r'^%s *%s *[,\-] *%s *%s *%s *%s$' % (DAY, MONTH, DAY, MONTH, YEAR, G), raw)
    if match:
        chunks = match.groups()

        year = int(chunks[4])

        return d([
            int(chunks[0]),
            parse_month(chunks[1], MONTHS_PARENTAL),
            year
        ]), d([
            int(chunks[2]),
            parse_month(chunks[3], MONTHS_PARENTAL),
            year
        ])

    # Второе полугодие 1939 г.
    HALF = '([^ ]+)'
    match = re.match(r'^%s полугодие *%s *%s$' % (HALF, YEAR, G), raw)
    if match:
        chunks = match.groups()

        start = (
            1,
            (parse_month(chunks[0], HALVES) - 1) * 6 + 1, # Первый месяц полугодия
            int(chunks[1])
        )

        end = ([
            1,
            (start[1] + 6) % 6, # Сложение по модулю 6 даёт первый месяц следующего полугодия
            start[2] if start[1] == 1 else start[2] + 1
        ])

        return d(start), d(end)

    raise Exception('Не удалось распознать дату: %s' % raw)

def get_links(page):
    'Получение навигации (списка разделов сайта по годам)'

    slider = page.find('div', 'filter_slide')

    # Элементы слайдера
    anchors = slider.find_all('a', '')

    return tuple(
        (a.find('div', 'l').text.replace(u'–', u'-').replace(u' ', u''),
            BASE_URL + a['href'])
        for a in anchors)

def get_events(page):
    'Список событий'

    # Список абзацев
    items = page.find('div', 'newstyle').find_all(recursive=False)

    event  = None
    events = []
    for item in items:
        # Если мы нашли заголовок. Отбрасываем слишком длинные -- это не даты.
        if item.span and len(item.text) < 40:
            start_date, end_date = parse_date(item.text)
            # Шаблон события
            event = {
                'startDate': start_date,
                'endDate':   end_date,
                'text':      u'',
                'headline':  None,
            }

            events.append(event)

        elif item.find('img'):
            # В блоке есть изображение
            img = item.find('img')
            event['asset'] = {
                'media': BASE_URL + img['src'],
                'credit': u'Официальный сайт МВД России',
                'caption': item.text,
            }

        else:
            # Заголовок
            if not event['headline']:
                event['headline'] = item.text

            # Прочий текст
            if item.name == u'ul': # Список?
                # Пробегаем по всем элементам
                event['text'] += u''.join(u'<p>%s</p>' % li.text for li in item.find_all())
            
            else: # Что-то другое?
                event['text'] += u'<p>%s</p>' % item.text

    return events

def format_output(contents):
    'Вывод JSON'

    result = {
        'timeline': {
            'headline': u'История МВД РФ',
            'type': 'default',
            'startDate': '1800',
            'text': u'История министерства внутренних дел РФ',
            'date': contents,
        },
    }

    return json.dumps(result, ensure_ascii=False).encode('utf-8', 'ignore')

# Разбор командной строки
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('-s', '--split', help='Разделить данные на несколько файлов', action="store_true")
parser.add_argument('-o', '--output', help='Имя выходного файла')
args = parser.parse_args()

# Проверка аргументов
if args.split and not args.output:
    raise Exception('''Пожалуйста, укажите имя выходных файлов.
Например, если указать timeline.json, то выходные данные будут разделены по файлам timeline.1980.json, timeline.1995-2000.json, и так далее.''')

# Загрузка основной страницы
startpage = bs(fetch(URL))
links = get_links(startpage)

# Основной цикл
if args.split: # Если надо разделять на файлы
    basename, ext = os.path.splitext(args.output)

    for years, link in links:
        # Выгрузка и анализ событий
        contents = get_events(bs(fetch(link)))

        # Форматирование результата
        output = format_output(contents)

        # Вывод
        with open('%s.%s%s' % (basename, years, ext), 'w') as outfile:
            outfile.write(output)

else: # Если всё в одном файле
    contents = []
    
    for name, link in links:
        contents.extend(get_events(bs(fetch(link))))

    # Готовый результат
    output = format_output(contents)

    if args.output: # Если запись в файл
        with open(args.output, 'w') as outfile:
            outfile.write(output)

    else: # Если вывод на stdout
        print output
