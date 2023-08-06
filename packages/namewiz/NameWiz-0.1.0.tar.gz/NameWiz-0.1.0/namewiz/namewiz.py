import datetime
import platform
if platform.system() == 'Windows':
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(2)

import PySimpleGUI as sg


# type, lang, ID, date

LANG = {
    'Greek': 'GRC',
    'English': 'ENG',
    'Latin': 'LAT',
    'Hebrew': 'HEB',
    'Syriac': 'SYC',
    'Aramaic': 'ARC',
    'Coptic': 'COP',
    'German': 'DEU',
    'French': 'FRA',
    'Italian': 'ITA',
    'Geez': 'GEZ',
    'Gothic': 'GOT'
}

def get_date():
    return datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day

def get_lang_radio(Label: str, lang_code: str):
    return sg.Radio(Label, 'lang', key=lang_code, enable_events=True)

def language_frame():
    languages = []
    two = []
    for l in LANG:
        two.append(get_lang_radio(l, LANG[l])) 
        if len(two) == 2:
           languages.append(two)
           two = [] 
    return languages

def parse_form(values: dict):
    doc_type = '?'
    genre = '??'
    lang = '???'
    id = '?????'
    year = '!!!!'
    month = '!!'
    day = '!!'
    for t in ['P', 'M']:
        if values[t]:
            doc_type = t
    for g in ['NT', 'OG', 'HB', 'EC', 'Forgery', 'APP', 'MOD_APP']:
        if values[g]:
            genre = g
    for l in LANG.values():
        if values[l]:
            lang = l
    if values['id'] != '':
        id = values['id']
    # process date
    if len(str(values['year'])) == 4:
        year = values['year']
    if len(str(values['month'])) <= 2:
        month = str(values['month']).zfill(2)
    if len(str(values['day'])) <= 2:
        day = str(values['day']).zfill(2)
    # 
    return f'{doc_type}_{genre}_{lang}_{id}_{year}{month}{day}'

def layout():
    tenbyone = (5, 1)
    year, month, day = get_date()
    type_frame = [
        [
            sg.Radio('Printed', 'type', key='P', enable_events=True), 
            sg.Radio('Handwritten', 'type', key='M', enable_events=True)
        ]
    ]
    genre_frame = [
        [sg.Radio('New Testament', 'genre', key='NT', enable_events=True), sg.Radio('Old Greek', 'genre', key='OG', enable_events=True)],
        [sg.Radio('Hebrew Bible', 'genre', key='HB', enable_events=True), sg.Radio('Early Christian Writing', 'genre', key='EC', enable_events=True)],
        [sg.Radio('Forgery', 'genre', key='Forgery', enable_events=True), sg.Radio('Appocrypha', 'genre', key='APP', enable_events=True)],
        [sg.Radio('Modern Appocrypha', 'genre', key='MOD_APP', enable_events=True)]
    ]
    id_tip = 'e.g. GA or Rahlfs #'
    id_frame = [
        [sg.T('Item ID: '), sg.I('', key='id', tooltip=id_tip, enable_events=True)]
            ]
    date_frame = [
        [
            sg.T('Year: '), sg.Spin([i for i in range(2000, 2031)], initial_value=year, key='year', size=tenbyone, enable_events=True),
            sg.T('Month: '), sg.Spin([i for i in range(1, 13)], initial_value=month, key='month', size=tenbyone, enable_events=True),
            sg.T('Day: '), sg.Spin([i for i in range(1, 32)], initial_value=day, key='day', size=tenbyone, enable_events=True)
        ]
            ]
    return [
        [sg.Frame('Item Type', type_frame)],
        [sg.Frame('Genre', genre_frame)],
        [sg.Frame('Primary Language', language_frame())],
        [sg.Frame('Item ID', id_frame)],
        [sg.Frame('Date', date_frame)],
        [sg.B('Refresh')],
        [sg.T('CSNTM Name: '), sg.I('', key='name')]
    ]


def main():
    MOST_KEYS = [
        'day', 'month', 'year', 'Refresh', 'id', 'P', 'M',
        'NT', 'OG', 'HB', 'EC', 'Forgery', 'MOD_APP', 'APP'
        ]
    sg.theme('LightBlue')
    window = sg.Window('NameWiz', layout())
    while True:
        event, values = window.read()
        if event in [None, sg.WIN_CLOSED]:
            break
        elif event in MOST_KEYS or event in LANG.values():
            window['name'].update(parse_form(values))

    window.close()