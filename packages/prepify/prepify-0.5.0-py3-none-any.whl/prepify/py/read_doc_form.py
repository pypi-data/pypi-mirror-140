import datetime
import json
from pathlib import Path

from natsort import natsorted
import PySimpleGUI as sg

import prepify.py.edit_settings as es
import prepify.py.foliation as fo


ALL_DOC_VALUES = (
    'csntm_id',
    'ga_number',
    'ldab', 
    'pinakes', 
    'bibliography', 
    'papyrus', 
    'parchment', 
    'paper', 
    'number_of_leaves', 
    'number_of_columns', 
    'lines_max', 
    'lines_min', 
    'width_min', 
    'width_max',
    'bottom_width_min',
    'bottom_width_max',
    'height_min', 
    'height_max', 
    'bottom_height_min',
    'bottom_height_max',
    'depth_bottom', 
    'depth_top',
    'majuscule',
    'minuscule',
    'condition',
    'date_range_start',
    'date_range_end',
    'exact_year',
    'numeration_note',
    'biblical_content_gospels',
    'biblical_content_acts',
    'biblical_content_paul',
    'biblical_content_catholic',
    'biblical_content_revelation',
    'biblical_content_specific',
    'language_greek',
    'language_latin',
    'language_coptic',
    'language_syriac',
    'language_georgian',
    'language_geez',
    'institution',
    'shelf_number',
    'former_owners',
    'examiner',
    'general_comments',
    'exact_year?',
    'cover_edge', 
    'cover_spine', 
    'cover_top', 
    'cover_bottom',
    'cover_front',
    'cover_back',
    'cover_3d',
    'notes_for_digitizers',
    'marginalia',
    'institution_description',
    'guide_sheet',
    'cf_intf_comments',
    'biblical_content_incomplete',
    'quire_comments',
    'has_icon',
    'has_illumination',
    'has_lection',
    'has_commentary',
    'icon_notes',
    'illumination_notes',
    'lection_notes',
    'commentary_notes',
    'continuous',
    'lectionary',
    'paschal',
    'sanctoral',
    'esk',
    'sk',
    'e',
    'k',
    '94_liste',
    'additional_nt_mss?',
    'additional_nt_mss',
    'other_additional_mss?',
    'other_additional_mss',
    'institution_place',
    'institution_comments',
    'imager',
    'year_imaged',
    'month_imaged',
    'day_imaged',
    'year',
    'month',
    'day',
    'paper_secondary',
    'papyrus_secondary',
    'parchment_secondary',
    'exterior',
    'geo_shape',
    'lines_normal',
    'ms_other_places',
    'other_features',
    'has_ektheses',
    'ektheses_notes',
    'has_otmarks',
    'otmarks_notes',
    'has_neume',
    'neume_notes',
    'has_carpianus',
    'carpianus_notes',
    'has_rubrication',
    'rubrication_notes',
    'has_headings',
    'headings_notes',
    'has_icons',
    'icons_notes',
    'has_kephalaia',
    'kephalaia_notes',
    'has_commentary',
    'commentary_notes',
    'commentary_framed',
    'commentary_alternating',
    'commentary_color',
    'commentary_color',
    'commentary_majuscule',
    'commentary_minuscule',
    'has_headings',
    'headings_notes',
    '94_liste',
)

DISABLED = (
    'has_illumination',
    'has_lection',
    'has_icon',
    'has_commentary',
    'has_ektheses',
    'has_otmarks',
    'has_neume',
    'has_carpianus',
    'has_rubrication',
    'has_headings',
    'has_icons',
    'has_kephalaia',
)

LISTBOXES = (
    'quire_structure',
    'table_of_contents',
    'former_owners'
)

def get_doc_data(values: dict, window: sg.Window, foliation: fo.Foliation):
    to_save = {}
    for key in ALL_DOC_VALUES:
        to_save[key] = values[key]
    for key in LISTBOXES:
        to_save[key] = window[key].get_list_values()
    to_save['sections'] = foliation.sections
    return to_save

def save_doc_data(values: dict, window: sg.Window, foliation: fo.Foliation, save_temp: bool = False, crashed: bool = False):
    settings = es.get_settings()
    to_save = get_doc_data(values, window, foliation)
    if save_temp:
        now = datetime.datetime.now().strftime('%Y%m%d-%H%M')
        save_path = f'failsafe_{now}.json'
    elif crashed:
        now = datetime.datetime.now().strftime('%Y%m%d-%H%M')
        save_path = f'crash_recovery_{now}.json'
    else:
        save_path = sg.popup_get_file(
            '', no_window=True, file_types=(('JSON Files', '*.json'),), 
            initial_folder=settings['prepdoc_folder'], save_as=True)
    if not save_path:
        return
    try:
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(to_save, f, ensure_ascii=False, indent=4)
    except Exception as e:
        sg.popup_ok(f'Failed to save.\n(for David: {e})', title='Bummer')
    es.update_settings('prepdoc_folder', Path(save_path).parent.as_posix())
    return save_path

def load_from_saved(window: sg.Window):
    settings = es.get_settings()
    file_path = sg.popup_get_file(
        '', no_window=True, file_types=(('JSON Files', '*.json'),), 
        initial_folder=settings['prepdoc_folder'])
    if not file_path:
        return
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            previous_data = json.load(f)
    except Exception as e:
        sg.popup_ok(f'Could not open that file. See error below\n{e}')
        return
    es.update_settings('prepdoc_folder', Path(file_path).parent.as_posix())
    for key in ALL_DOC_VALUES:
        window[key].update(previous_data.get(key))
    for key in LISTBOXES:
        window[key].update(values=previous_data.get(key, []))
    foliation = fo.Foliation(previous_data['sections'])
    window['foliation'].update(values=foliation.as_sg_tree())
    return foliation

def update_cf_intf(liste_entry: dict, window: sg.Window, ga: str, shelf: dict):
    '''Update the "Cf. INTF" tab values with offline data from
    INTF's database.'''
    window['intf_GA Number'].update(value=ga)
    window['intf_shelf'].update(value=shelf['shelfNumber'])
    window['intf_contents'].update(value=liste_entry.get('content_summary', ''))
    window['intf_date'].update(value=f"{liste_entry.get('originYear', {}).get('content', '')} {liste_entry.get('originYear', {}).get('early', '')}–{liste_entry.get('originYear', {}).get('late', '')}")
    window['intf_material'].update(value=liste_entry['material'])
    window['intf_leaves'].update(value=shelf['leavesCount'])
    window['intf_columns'].update(value=liste_entry.get('columns', ''))
    # format line count
    if liste_entry.get('lineCount', {}).get('lineCountMax', ''):
        line_count = f"{liste_entry['lineCount']['lineCountMin']}–{liste_entry['lineCount']['lineCountMax']}"
    else:
        line_count = liste_entry.get('lineCount', {}).get('lineCountMin', '')
    window['intf_lines'].update(value=line_count)
    # format width
    if liste_entry.get('width'):
        if liste_entry['width'].get('widthMax'):
            width = f"{liste_entry['width']['widthMin']}–{liste_entry['width']['widthMax']}"
        else:
            width = liste_entry['width'].get('widthMin')
    else:
        width = ''
    # format height
    if liste_entry.get('height'):
        if liste_entry['height'].get('heightMax'):
            height = f"{liste_entry['height']['heightMin']}–{liste_entry['height']['heightMax']}"
        else:
            height = liste_entry['height'].get('heightMin')
    else:
        height = ''
    if width == '' and height == '':
        dimensions = ''
    else:
        dimensions = f'{width} W\n{height} H'
    window['intf_dimensions'].update(value=dimensions)

def parse_dimensions(values):
    if values['width_min'] == values['width_max'] or values['width_max'] == 0:
        width = values['width_min']
    else:
        width = f'{values["width_min"]}–{values["width_max"]}'
    if values['height_min'] == values['height_max'] or values['height_max'] == 0:
        height = values['width_min']
    else:
        height = f'{values["height_min"]}–{values["height_max"]}'
    depth = f'{values["depth_bottom"]} (b) {values["depth_top"]} (t)'
    return width, height, depth

def format_content(values):
    content = ''
    options = (
        ('gospels', 'e'), 
        ('acts', 'a'), 
        ('catholic', 'c'), 
        ('paul', 'p'), 
        ('revelation', 'r'), 
        )
    for item in options:
        if values[f'biblical_content_{item[0]}']:
            content = f'{content.lstrip()}{item[1]}'
    if values['biblical_content_specific'] != '':
        content = f'{content}: {values["biblical_content_specific"]}'
    if values['biblical_content_incomplete']:
        content = f'{content} †'
    return content

def format_date(values):
    if values['exact_year?']:
        date = values['exact_year']
    elif values['date_range_start'] == 0 and values['date_range_end'] == 0:
        date = '—'
    else:
        date = f'{values["date_range_start"]}–{values["date_range_end"]}'
    return date

def format_material(values):
    for m in ('papyrus', 'parchment', 'paper'):
        if values[m]:
            break
    else:
        m = '—'
    return m

def format_lines(values):
    if values['lines_max'] == 0 or values['lines_min'] == values['lines_max']:
        lines = values['lines_min']
    else:
        lines = f'{values["lines_min"]}–{values["lines_max"]}'
    if lines == 0:
        lines = '—'
    return lines

def load_cf_csntm(values: dict, window: sg.Window):
    window['csntm_GA Number'].update(value=values['ga_number'])
    window['csntm_shelf'].update(value=values['shelf_number'])
    content = format_content(values)
    window['csntm_contents'].update(value=content)
    date = format_date(values)
    window['csntm_date'].update(value=date)
    # material
    material = format_material(values)
    window['csntm_material'].update(value=material)
    # leaves
    window['csntm_leaves'].update(value=values['number_of_leaves'])
    window['csntm_columns'].update(value=values['number_of_columns'])
    # lines
    lines = format_lines(values)
    window['csntm_lines'].update(value=lines)
    # dimensions
    width, height, depth = parse_dimensions(values)
    if width == '' and height == '':
        dimensions = ''
    else:
        dimensions = f'{width} cm W\n{height} cm H\n{depth} cm D'
    window['csntm_dimensions'].update(value=dimensions)

def add_former_institute(values: dict, window: sg.Window):
    previous_owners = window['former_owners'].get_list_values()
    owner = values['previous_owner']
    place = values['previous_place']
    shelf = values['previous_shelf']
    date = values['date_sold']
    if owner == place == shelf == '':
        sg.popup_ok('At least one value is required between owner, place, and shelf.', title='Missing Value')
        return
    elif owner == place == '':
        new_entry = f'Shelf Number: {shelf} — {date}'
    elif owner == shelf == '':
        new_entry = f'Place: {place} — {date}'
    elif place == shelf == '':
        new_entry = f'Owner: {owner} — {date}'
    elif owner == '':
        new_entry = f'({place}): {shelf} — {date}'
    elif place == '':
        new_entry = f'{owner}: {shelf} — {date}'
    elif shelf == '':
        new_entry = f'{owner} ({place}) — {date}'
    else:
        new_entry = f'{owner} ({place}): {shelf} — {date}'
    previous_owners.append(new_entry)
    window['former_owners'].update(values=previous_owners)

def remove_selected_from_listbox(values: dict, window, key: str):
    listbox_contents = window[key].get_list_values()
    new_list = []
    for item in listbox_contents:
        if item in values[key]:
            continue
        new_list.append(item)
    window[key].update(values=new_list)

def add_toc_entry(values: dict, window: sg.Window):
    toc = window['table_of_contents'].get_list_values()
    toc.append(values['toc_entry'])
    window['table_of_contents'].update(values=toc)
    window['toc_entry'].update('')

def sort_toc(window):
    items = window['table_of_contents'].get_list_values()
    items = natsorted(items)
    window['table_of_contents'].update(values=items)

def quick_save(values, window, foliation):
    to_save = get_doc_data(values, window, foliation)
    to_save['sections'] = foliation.sections
    if values['csntm_id'] == '':
        sg.popup_ok('CSNTM ID field must not be empy', title='CSNTM ID Required')
        return
    try:
        with open(f'{values["csntm_id"]}.json', 'w', encoding='utf-8') as f:
            json.dump(to_save, f, ensure_ascii=False, indent=4)
        sg.popup_quick_message(f'{values["csntm_id"]} saved!')
    except:
        return

def decolor_buttons(window, sections: list[dict]):
    for section in ('Frontmatter', 'Body', 'Backmatter'):
        window[section].update(button_color='#046380')
        window[section].update(disabled=False)
    for section in sections:
        if section['main_section']:
            window[section['main_section']].update(button_color='#05a366')

def hide_all_folio_options(window):
    window['number_title'].update(visible=False)
    window['number'].update(visible=False)
    window['number'].update(value='')
    window['written_from'].update(visible=False)
    window['written_from'].update(value='')
    window['n-dash'].update(visible=False)
    window['written_to'].update(visible=False)
    window['written_to'].update(value='')
    window['Add'].update(visible=False)
    window['written_range_title'].update(visible=False)

def hide_unhide_foliation(values: dict, window: sg.Window):
    if values['folio_type'] in {'Front Inside Cover', 'Back Inside Cover'}:
        window['number_title'].update(visible=False)
        window['number'].update(visible=False)
        window['number'].update(value='')
        window['written_from'].update(visible=False)
        window['written_from'].update(value='')
        window['n-dash'].update(visible=False)
        window['written_to'].update(visible=False)
        window['written_to'].update(value='')
        window['Add'].update(visible=True)
        window['written_range_title'].update(visible=False)
    elif values['folio_type'] == 'Unnumbered':
        window['written_from'].update(visible=False)
        window['written_from'].update(value='')
        window['written_to'].update(visible=False)
        window['written_to'].update(value='')
        window['number_title'].update(visible=True)
        window['number'].update(visible=True)
        window['number'].update(value='')
        window['n-dash'].update(visible=False)
        window['Add'].update(visible=False)
        window['written_range_title'].update(visible=False)
    elif values['folio_type'] in {'Foliated', 'Paginated'}:
        window['written_range_title'].update(visible=True)
        window['written_from'].update(visible=True)
        window['written_from'].update(value='')
        window['n-dash'].update(visible=True)
        window['written_to'].update(visible=True)
        window['written_to'].update(value='')
        window['number'].update(visible=False)
        window['number'].update(value='')
        window['Add'].update(visible=False)
