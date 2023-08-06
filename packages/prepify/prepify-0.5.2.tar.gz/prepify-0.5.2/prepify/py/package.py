import os

import PySimpleGUI as sg

from prepify.py import backup
import prepify.py.edit_settings as es
import prepify.py.guide_sheet as gs


def minimally_valid(values: dict, submitted):
    if submitted == []:
        sg.popup_ok('At least one item of foliation must be completed.', title='Not so fast...')
        return
    if values['ga_number'] == '' or values['csntm_id'] == '':
        sg.popup_ok('Both the GA Number and CSNTM ID must be entered.', title='Form Incomplete')
        return
    if values['guide_sheet'] == '':
        sg.popup_ok('The Guide Sheet is crucial for the imaging team and must be selected.', title='Guide Sheet Required')
        return
    if values['project_folder'] == '':
        sg.popup_ok('A Project Folder must be selected.\nThis is where the prepdoc files will be saved.', title='No Project Folder')
        return
    return True

def package(values: dict, window):
    foliation = window['foliation'].get_list_values()
    if not minimally_valid(values, foliation):
        return
    backup.auto_save(values, window)
    from zipfile import ZipFile
    import shutil
    temp_xlsx = f'{values["csntm_id"]}.xlsx'
    try:
        shutil.copyfile(values['guide_sheet'], temp_xlsx)
    except PermissionError:
        sg.popup_ok('Close the Excel file before packing', title='Excel File Already Open')
        return
    guide = gs.decollate_guide(temp_xlsx)
    if not guide:
        return
    gs.create_xslx(guide, temp_xlsx)
    es.update_settings('project_folder', values['project_folder'])
    try:
        with ZipFile(f'{values["project_folder"]}/{values["csntm_id"]}.zip', 'w') as zip:
            zip.write(f'{values["csntm_id"]}.xlsx')
            zip.write(f'{values["csntm_id"]}.json')
        os.remove(f'{values["csntm_id"]}.xlsx')
        os.remove(f"{values['csntm_id']}.json")
        sg.popup_ok(f'The Guide Sheet and Prepdoc File have been packaged and saved to\n{values["project_folder"]}', title='Prepdocs Packaged!')
    except Exception as e:
        sg.popup_ok('Bummer. Something failed while compressing the prep documents.', title='Warning')
        return
