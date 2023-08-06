

import PySimpleGUI as sg

import prepify.py.read_doc_form as rdf


class Foliation:

    def __init__(self, sections: list[dict] = []):
        self.sections = sections

    def insert_section(
                        self,
                        insert_at: str,
                        selected: list,
                        main_section: str = None,
                        foliation_type: str = None,
                        foliation_number: str = None,
                        written_from: str = None,
                        written_to: str = None,
                    ):
        if main_section:
            for section in self.sections:
                if section == main_section:
                    main_section = f'{main_section}+'
        new_section = {
            'main_section': main_section,
            'foliation_type': foliation_type,
            'foliation_number': foliation_number,
            'written_from': written_from,
            'written_to': written_to,
        }
        if insert_at == 'Add':
            self.sections.append(new_section)
        elif insert_at == 'Insert at Beginning':
            self.sections.insert(0, new_section)
        elif insert_at == 'Insert after Selected' and selected != []:
            self.sections.insert(selected[0]+1, new_section)
        elif insert_at == 'replace':
            self.sections[selected[0]] = new_section
        else: # just in case the user does something weird, add the section at the end and let them see what they did wrong.
            self.sections.append(new_section)
        
    def remove_section(self, selected_indices: list[int]):
        pruned_sections = []
        for i, section in enumerate(self.sections):
            if i in selected_indices:
                continue
            pruned_sections.append(section)
        self.sections = pruned_sections

    def get_section_by_index(self, index: int):
        return self.sections[index]

    def as_sg_tree(self):
        tree = sg.TreeData()
        main = ''
        for i, section in enumerate(self.sections):
            if section.get('main_section'):
                main = i
                tree.Insert('', i, section['main_section'].upper(), ['', ''])
                continue
            elif section.get('foliation_type') in {'Front Inside Cover', 'Back Inside Cover'}:
                tree.Insert(main, i, section['foliation_type'], ['', ''])
            elif section.get('foliation_type') == 'Unnumbered':
                tree.Insert(main, i, section['foliation_type'], [section['foliation_number'], ''])
            elif section.get('foliation_type') in {'Paginated', 'Foliated'}:
                landmarks = f"{section['written_from']}–{section['written_to']}"
                # try:
                number = int(section.get('written_to')) - int(section.get('written_from')) + 1
                # except:
                #     number = '?'
                tree.Insert(main, i, section['foliation_type'], [number, landmarks])
        return tree

    def calculate_total_images(self, values: dict, window):
        total = 0
        for section in self.sections:
            if section['main_section']:
                continue
            elif section['foliation_type'] in {'Front Inside Cover', 'Back Inside Cover'}:
                total += 1
            elif section['foliation_type'] == 'Unnumbered':
                total += int(section['foliation_number']) * 2
            elif section['foliation_type'] == 'Foliated':
                total += (int(section['written_to']) - int(section['written_from']) + 1) * 2
            elif section['foliation_type'] == 'Paginated':
                total += int(section['written_to']) - int(section['written_from']) + 1
        for k in ('cover_edge', 'cover_spine', 'cover_top', 'cover_bottom', 'cover_front', 'cover_back', 'cover_3d'):
            if values[k]:
                total += 1
        window['total'].update(f'{total}')

    def create_guide(self):
        def add_cover(section: dict, guide: list, count: int, side: str):
            guide.append({
                'Image #': f'{count}{side}', 
                'Landmark': section['foliation_type'], 
                'Contents': '', 
                'Notes for Imagers': '', 
                'Notes': '',
                'Actual Folio': ''})
            count += 1
            return guide, count
        def add_unnumbered(section: dict, guide: list, count: int, actual: int, side: str, actual_name: str):
            for _ in range(int(section['foliation_number'])):
                guide.append({
                    'Image #': f'{count}{side}', 
                    'Landmark': section['foliation_type'], 
                    'Contents': '', 
                    'Notes for Imagers': '', 
                    'Notes': '',
                    'Actual Folio': f'{actual_name} {actual}{side}'})
                count += 1
                actual += 1
            return guide, count, actual
        def add_foliated(section: dict, guide: list, count: int, actual: int, side: str, actual_name: str):
            start = int(section['written_from'])
            stop = int(section['written_to']) + 1
            for landmark in range(start, stop):
                guide.append({
                    'Image #': f'{count}{side}',
                    'Landmark': f'{landmark}{side}',
                    'Contents': '',
                    'Notes for Imagers': '',
                    'Notes': '',
                    'Actual Folio': f'{actual_name} {actual}{side}'})
                count += 1
                actual += 1
            return guide, count, actual
        def add_paginated(section: dict, guide: list, count: int, actual: int, side: str, actual_name: str):
            odds = []
            evens = []
            start = int(section['written_from'])
            stop = int(section['written_to']) + 1
            for page in range(start, stop):
                if page % 2 == 0:
                    evens.append(page)
                else:
                    odds.append(page)
            if side == 'a':
                pages = odds
            elif side == 'b':
                pages = evens
            for page in pages:
                guide.append({
                    'Image #': f'{count}{side}',
                    'Landmark': f'p. {page}',
                    'Contents': '',
                    'Notes for Imagers': '',
                    'Notes': '',
                    'Actual Folio': f'{actual_name} {actual}{side}'})
                count += 1
                actual += 1
            return guide, count, actual
        def create_side_guide(guide, count, actual, side):
            actual_name = ''
            for section in self.sections:
                if section['main_section']:
                    if section['main_section'] == 'Body':
                        actual_name = 'TEXT'
                    else:
                        actual_name = section['main_section'].upper()
                    actual = 1
                elif section['foliation_type'] in {'Front Inside Cover', 'Back Inside Cover'}:
                    guide, count = add_cover(section, guide, count, side)
                elif section['foliation_type'] == 'Unnumbered':
                    guide, count, actual = add_unnumbered(section, guide, count, actual, side, actual_name)
                elif section['foliation_type'] == 'Foliated':
                    guide, count, actual = add_foliated(section, guide, count, actual, side, actual_name)
                elif section['foliation_type'] == 'Paginated':
                    guide, count, actual = add_paginated(section, guide, count, actual, side, actual_name)
            return guide, count, actual

        guide_a, _, _ = create_side_guide([], 0, 1, 'a')
        guide_b, _, _ = create_side_guide([], 0, 1, 'b')

        return guide_a, guide_b

    def create_collated_guide(self):
        guide_a, guide_b = self.create_guide()
        guide = []
        for a, b in zip(guide_a, guide_b):
            guide.append(a)
            guide.append(b)
        if guide[0]['Landmark'] == 'Front Inside Cover':
            guide.pop(0)
        if guide[-1]['Landmark'] == 'Back Inside Cover':
            guide.pop(-1)
        return guide

    def create_decollated_guide(self):
        guide_a, guide_b = self.create_guide()
        guide = guide_a + guide_b
        if guide[0]['Landmark'] == 'Front Inside Cover':
            guide.pop(0)
        if guide[-1]['Landmark'] == 'Back Inside Cover':
            guide.pop(-1)
        return guide

    def create_xslx(self, name: str = 'temp.xlsx'):
        guide = self.create_collated_guide()
        import pandas as pd
        df = pd.DataFrame.from_dict(guide)
        df.index += 1
        ####
        try:
            writer = pd.ExcelWriter(name)
        except:
            sg.popup_ok('Close or rename the open Excel file before generating another', title='File Write Denied')
            return
        df.to_excel(writer, sheet_name='Guide', index=False, na_rep='')
        for column in df:
            column_length = max(df[column].astype(str).map(len).max(), len(column))
            col_idx = df.columns.get_loc(column)
            writer.sheets['Guide'].set_column(col_idx, col_idx, column_length)
        writer.save()


def enforce_spin(values: dict, window: sg.Window):
    for value in ['number', 'written_from', 'written_to']:
        if not values[value].isnumeric() or values[value] == '0':
            window[value].update(value='')

def submit_section(values: dict, window: sg.Window, foliation: Foliation, insert_foliation: str):
    if values['folio_type'] in {'Front Inside Cover', 'Back Inside Cover'}:
        foliation.insert_section(
            insert_foliation,
            values['foliation'],
            foliation_type=values['folio_type']
        )
    elif values['folio_type'] == 'Unnumbered':
        if values['number'] == '':
            return
        foliation.insert_section(
            insert_foliation,
            values['foliation'],
            foliation_type=values['folio_type'],
            foliation_number=values['number']
        )
    elif values['folio_type'] in {'Foliated', 'Paginated'}:
        if values['written_from'] == '' or values['written_to'] == '':
            return
        elif values['folio_type'] == 'Paginated':
            if int(values['written_from']) % 2 == 0 or int(values['written_to']) % 2 != 0:
                sg.popup_ok('When entering page numbers, the first number must be odd, and the second must be even.', title='Number Problem')
                return
        foliation.insert_section(
            insert_foliation, # either insert at end, beginning, or after selected
            values['foliation'], # a list of user-selected rows in the Tree
            foliation_type=values['folio_type'],
            written_from=values['written_from'],
            written_to=values['written_to'],
        )
    tree = foliation.as_sg_tree()
    window['foliation'].update(values=tree)
    window['number'].update('')
    window['written_from'].update('')
    window['written_to'].update('')
    window['folio_type'].update('-select-')

def remove_section(values: dict, window, foliation: Foliation):
    foliation.remove_section(values['foliation'])
    window['foliation'].update(values=foliation.as_sg_tree())

def submit_main_section(values: dict, window: sg.Window, section_name: str, foliation: Foliation, insert_at: str):
    for section in foliation.sections:
        if section_name == section['main_section']:
            return
    foliation.insert_section(
        insert_at,
        values['foliation'],
        main_section=section_name
    )
    tree = foliation.as_sg_tree()
    window['foliation'].update(values=tree)
    # rdf.color_section_buttons(window, section_name)
    rdf.decolor_buttons(window, foliation.sections)

def submit_other_section(values: dict, window: sg.Window, foliation: Foliation, insert_at: str):
    section_name = sg.popup_get_text(
        'Enter a custom section name below.', title='Enter a Section Name'
        )
    if not section_name:
        return
    foliation.insert_section(
        insert_at,
        values['foliation'],
        main_section=section_name,
    )
    tree = foliation.as_sg_tree()
    window['foliation'].update(values=tree)

def open_excel(filename: str = 'temp.xlsx'):
    try:
        import platform
        if platform.system() == 'Windows':
            import os
            os.startfile('temp.xlsx')
        else:
            import subprocess
            subprocess.call(('open', filename))
    except:
        sg.popup(f'Close or save "{filename}" to a different file name before creating another spreadsheet.', title="Ooops")

def edit_foliation_window(folio_type: str, number: str = '', written_from: str = '', written_to: str = ''):
    # initial state
    if folio_type in {'Front Inside Cover', 'Back Inside Cover'}:
        n = True
        w = True
    elif folio_type in {'Foliated', 'Paginated'}:
        n = True
        w = False
    elif folio_type == 'Unnumbered':
        n = False
        w = True
    else:
        n = False
        w = False
    cat = [
        'Front Inside Cover',
        'Back Inside Cover',
        'Unnumbered',
        'Foliated',
        'Paginated',
        ]
    four = (4, 1)
    layout = [
        [
            sg.T('Type'),
            sg.Drop(cat, default_value=folio_type, k='folio_type', readonly=True, enable_events=True),
            sg.T('Number: ', key='number_title'),
            sg.Input(number, k='number', size=four, enable_events=True, disabled=n),
            sg.T('Written Range', key='written_range'),
            sg.Input(written_from, k='written_from', size=four, enable_events=True, disabled=w),
            sg.T('–'),
            sg.Input(written_to, k='written_to', size=four, enable_events=True, disabled=w),
        ],
        [sg.Button('Submit Edit', expand_x=True), sg.Button('Cancel', expand_x=True)],
    ]

    window = sg.Window('Add Subsection', layout)
    while True:
        event, values = window.read()
        if event in {'Cancel', None, sg.WINDOW_CLOSED}:
            window.close()
            return
        elif event == 'Submit Edit':
            window.close()
            return values
        elif event in {'number', 'written_from', 'written_to'}:
            enforce_spin(values, window)
        elif event == 'folio_type':
            if values['folio_type'] in {'Front Inside Cover', 'Back Inside Cover'}:
                window['number'].update(disabled=True)
                window['written_from'].update(disabled=True)
                window['written_to'].update(disabled=True)
            elif values['folio_type'] == 'Unnumbered':
                window['number'].update(disabled=False)
                window['written_from'].update(disabled=True)
                window['written_to'].update(disabled=True)
            elif values['folio_type'] in {'Foliated', 'Paginated'}:
                window['number'].update(disabled=True)
                window['written_from'].update(disabled=False)
                window['written_to'].update(disabled=False)
