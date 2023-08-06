
import PySimpleGUI as sg

import prepify.py.read_doc_form as rdf
from prepify.py.liste import LISTE

def validate_ga(ga: str):
    ga = ga.lower()
    if ga.startswith('p'):
        if len(ga) not in [2, 3, 4] or not ga[1:].isnumeric():
            return
    elif ga in [0, '', None]:
        return
    elif ga.startswith('0'):
        if len(ga) > 4 or len(ga) < 2 or not ga.isnumeric() or ga.startswith('00'):
            return
    elif ga.startswith('l'):
        ga = ga.replace('ect', '').replace(' ', '')
        if len(ga) > 5 or len(ga) < 2 or not ga[1:].isnumeric():
            return
    else: #minuscule
        if len(ga) > 4 or not ga.isnumeric():
            return
    return True

def ga_to_id(ga: str):
    ga = ga.lower()
    if ga.startswith('p'):
        id = ga.replace('p', '')
        id = id.zfill(4)
        id = f'1{id}'
    elif ga.startswith('0'):
        id = ga[1:]
        id = id.zfill(4)
        id = f'2{id}'
    elif ga.startswith('l'):
        ga = ga.replace('ect', '').replace(' ', '')
        id = ga[1:]
        id = id.zfill(4)
        id = f'4{id}'
    else:
        id = ga.zfill(4)
        id = f'3{id}'
    return id, ga

def load_liste(id: str):
    # try:
    #     with open('resources/Liste_min.json', 'r', encoding='utf-8') as f:
    #         liste = json.load(f)
    # except:
    #     sg.popup_ok('The local Liste data is missing.\nTalk to David F about it.', title='Uhoh!')
    liste = LISTE
    entry = liste.get(id)
    if entry:
        return entry
    else:
        return

def popup_choose_shelf(liste_entry):
    institutions = []
    for shelf in liste_entry['shelves']:
        institutions.append(shelf['institution']['name'])
    def inst_buttons(institutions):
        buttons = []
        for inst in institutions:
            buttons.append([sg.Button(inst)])
        return buttons
    layout = [[sg.T('The entered GA Number is associated with the following institutions.\nSelect one:')],
                inst_buttons(institutions)]
    window = sg.Window('Multiple Shelf Numbers Found', layout=layout)
    event, _ = window.read()
    if event in [sg.WIN_CLOSED, sg.WIN_X_EVENT, None]:
        event = institutions[0]
    window.close()
    return event

def choose_shelf(liste_entry):
    if len(liste_entry['shelves']) == 1:
        return liste_entry['shelves'][0]
    else:
        inst_name = popup_choose_shelf(liste_entry)
    for shelf in liste_entry['shelves']:
        if shelf['institution']['name'] == inst_name:
            return shelf

def load_cf_intf(values: dict, window: sg.Window):
    # load intf
    ga = values['ga_number'] #type: str
    if ga.lower() in ['', None, 'none', 'n/a']:
        return
    if not validate_ga(ga):
        sg.popup_ok(f'The GA number "{ga}" is invalid', title='Invalid GA')
        return
    intf_id, ga = ga_to_id(ga)
    liste_entry = load_liste(intf_id)
    if not liste_entry:
        sg.popup_ok(f'Sorry, {ga} was not found in the offline Liste.', title='Uhoh')
        return
    # try:
    shelf = choose_shelf(liste_entry)
    rdf.update_cf_intf(liste_entry, window, ga, shelf)
    # except Exception as e:
        # sg.popup_ok(f'Something failed when getting the shelf instance for {ga}.\n(For David: {e})', title='Uhoh')

def get_full_liste(values):
    import toml
    ga = values['ga_number'] #type: str
    if ga.lower() in ['', None, 'none', 'n/a']:
        return
    if not validate_ga(ga):
        sg.popup_ok(f'The GA number "{ga}" is invalid', title='Invalid GA')
        return
    intf_id, ga = ga_to_id(ga)
    liste_entry = load_liste(intf_id)
    if not liste_entry:
        return
    formatted = toml.dumps(liste_entry).replace('\n', '\n\n')
    return formatted

def full_liste_layout(liste_entry: str):
    return [
        [sg.Multiline(liste_entry, expand_x=True, expand_y=True)],
        [sg.Stretch(), sg.Button('Close'), sg.Stretch()]
    ]