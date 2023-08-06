import json
from pathlib import Path

import PySimpleGUI as sg


__version = '0.1.0'

def get_tx_json(json_folder, siglum: str, reference: str):
    try:
        with open(f'{json_folder}/{siglum}/{reference}.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return
    
def get_witnesses(tx_json: dict):
    witnesses = []
    for wit in tx_json['witnesses']:
        words = []
        for token in wit['tokens']:
            words.append(token['original'])
        text = ' '.join(words)
        witnesses.append({'id': wit['id'], 'text': text})
    return witnesses

def save_settings(settings: dict, main_dir):
    with open(f'{main_dir}/settings.json', 'w') as f:
        json.dump(settings, f, indent=4)

def save_folder_location(folder_location: str, settings: dict, main_dir):
    settings['json_folder'] = folder_location
    save_settings(settings, main_dir)
    sg.popup_quick_message('JSON Folder Location Saved')
    return settings

#######################
'''GUI'''
#######################
def ok(msg, title):
    layout = [[sg.T(msg)],
              [sg.B('Ok')]]
    window = sg.Window(title, layout)
    window.read()
    window.close()

def yes_cancel(msg, title):
    layout = [[sg.T(msg)],
              [sg.B('Yes'), sg.T(''), sg.B('Cancel')]]
    window = sg.Window(title, layout)
    event, _ = window.read()
    window.close()
    if event == 'Yes':
        return True
    else:
        return False

def get_settings(main_dir):
    try:
        with open(f'{main_dir}/settings.json', 'r') as f:
            settings = json.load(f)
            settings['json_folder']
            return settings
    except:
        return {'json_folder': ''}

def validate_load_tx(values: dict):
    if values['siglum'] in ['', None] or values['ref'] in ['', None]:
        ok('"Siglum" and "Reference" fields cannot be blank.', 'Forgetting Something?')
        return False
    return True

def set_hands(window: sg.Window, witnesses: list):
    hands = []
    for wit in witnesses:
        hands.append(wit['id'])
    window['hands'].update(values=hands, value=hands[0])
    return hands[0]

def set_text(window: sg.Window, witnesses: list, hand):
    for wit in witnesses:
        if wit['id'] == hand:
            window['tx_box'].update(wit['text'])
            break

def load_transcription(values: dict, settings: dict, window: sg.Window):
    if not validate_load_tx(values):
        return
    tx_json = get_tx_json(values['json_folder'], values['siglum'], values['ref'])
    if not tx_json:
        ok('Failed to get witnesses from this JSON file.', 'Bummer!')
        return
    witnesses = get_witnesses(tx_json)
    if not witnesses:
        ok('Failed to find text in this file.', 'Bummer')
        return
    first_hand = set_hands(window, witnesses)
    set_text(window, witnesses, first_hand)
    return True

def update_by_hand(values, settings, window):
    if not validate_load_tx(values):
        return
    tx_json = get_tx_json(settings['json_folder'], values['siglum'], values['ref'])
    if not tx_json:
        ok('Failed to get witnesses from this JSON file.', 'Bummer!')
        return
    witnesses = get_witnesses(tx_json)
    if not witnesses:
        ok('Failed to find text in this file.', 'Bummer')
        return
    set_text(window, witnesses, values['hands'])

def tokenize(text: str, siglum: str):
    tokens = []
    index = 2
    for word in text.split():
        tokens.append({
            'index': str(index),
            'original': word,
            't': word,
            'rule_match': [word],
            'siglum': siglum,
            'reading': siglum,
        })
        index += 2
    return tokens

def save_json_tx(tx_json: dict, values: dict):
    with open(f'{values["json_folder"]}/{values["siglum"]}/{values["ref"]}.json', 'w', encoding='utf-8') as f:
        json.dump(tx_json, f, ensure_ascii=False, indent=4)

def save_transcription(values: dict, settings: dict):
    if not yes_cancel('Update and save the original JSON transciption file?', 'Save?'):
        return
    tx_json = get_tx_json(settings['json_folder'], values['siglum'], values['ref'])
    wit_to_update = None
    for i, wit in enumerate(tx_json['witnesses']):
        if wit['id'] == values['hands']:
            wit_to_update = i
            break
    if wit_to_update is None:
        return
    tx_json['witnesses'].pop(wit_to_update)
    tx_json['witnesses'].append({'id': values['hands'], 'tokens': tokenize(values['tx_box'], values['hands'])})
    save_json_tx(tx_json, values)
    sg.popup_quick_message('JSON file updated')

def layout(settings: dict):
    return [
        [sg.T('JSON Folder: '), sg.Input(settings['json_folder'], key='json_folder'), sg.FolderBrowse(), sg.B('Save Folder Location')],
        [sg.T('Siglum: '), sg.Input('', key='siglum', size=(8, 1)), sg.T('Reference: '), sg.Input('', key='ref'), sg.Button('Load Transcription')],
        [sg.HorizontalSeparator()],
        [sg.T('Hands: '), sg.Drop([], key='hands', size=(10, 1), readonly=True), sg.Button('Update')],
        [sg.Multiline('', key='tx_box', size=(120, 5))],
        [sg.Button('Save Transcription')]
    ]

def main():
    sg.LOOK_AND_FEEL_TABLE['Parchment'] = {
                                        'BACKGROUND': '#FFE9C6',
                                        'TEXT': '#533516',
                                        'INPUT': '#EAC8A3',
                                        'TEXT_INPUT': '#2F1B0A',
                                        'SCROLL': '#B39B73',
                                        'BUTTON': ('white', '#C55741'),
                                        'PROGRESS': ('#01826B', '#D0D0D0'),
                                        'BORDER': 1, 'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0,
                                        }
    sg.theme('Parchment')
    sg.set_options(dpi_awareness=True)
    main_dir = Path(__file__).parent.as_posix()
    settings = get_settings(main_dir)
    window = sg.Window(f'JSON Transcription Editor v{__version}', layout(settings))
    
    loaded = False
    while True:
        event, values = window.read()
        # print(event, values)
        
        if event in [sg.WINDOW_CLOSED, None]:
            break

        elif event == 'Save Folder Location':
            settings = save_folder_location(values['json_folder'], settings, main_dir)

        elif event == 'Load Transcription':
           loaded = load_transcription(values, settings, window)

        elif event == 'Update':
            update_by_hand(values, settings, window)

        elif event == 'Save Transcription':
            if loaded:
                save_transcription(values, settings)
    
    window.close()

if __name__ == '__main__':
    main()
