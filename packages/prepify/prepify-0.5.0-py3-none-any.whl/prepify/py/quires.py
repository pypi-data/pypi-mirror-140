

from natsort import natsorted
import PySimpleGUI as sg

def add_quire(values: dict, window: sg.Window):
    quires = window['quire_structure'].get_list_values()
    if values['quire_note'] == '':
        quire_note = ''
    else:
        quire_note = f"({values['quire_note']})"
    for q in quires:
        if q.startswith(f'{values["quire_number_actual"]}'):
            sg.popup_ok('"Actual" quire number cannot be repeated', title='Duplicate Quire')
            return
    new_quire = f"{values['quire_number_actual']}: {values['quire_number_written']}.{values['quire_from']}–{values['quire_to']} {quire_note}"
    quires.append(new_quire)
    quires = natsorted(quires)
    window['quire_structure'].update(quires)
