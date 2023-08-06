from datetime import datetime

import PySimpleGUI as sg

import prepify.py.edit_settings as es


def cf_intf(spacer):
    titles_column = [
        [sg.T('')],
        [sg.T('GA Number: ')],
        [sg.T('Shelf Number: ')],
        [sg.T('Contents: ')],
        [sg.T('Date: ')],
        [sg.T('Material: ')],
        [sg.T('Leaves: ')],
        [sg.T('Columns: ')],
        [sg.T('Lines: ')],
        [sg.T('Dimensions: ', size=(10, 3))]
    ]
    csntm_column = [
        [sg.Text('CSNTM')],
        [sg.T('', key='csntm_GA Number', size=spacer, background_color='#f0f0f0')],
        [sg.T('', key='csntm_shelf', size=spacer, background_color='#f0f0f0')],
        [sg.T('', key='csntm_contents', size=spacer, background_color='#f0f0f0')],
        [sg.T('', key='csntm_date', size=spacer, background_color='#f0f0f0')],
        [sg.T('', key='csntm_material', size=spacer, background_color='#f0f0f0')],
        [sg.T('', key='csntm_leaves', size=spacer, background_color='#f0f0f0')],
        [sg.T('', key='csntm_columns', size=spacer, background_color='#f0f0f0')],
        [sg.T('', key='csntm_lines', size=spacer, background_color='#f0f0f0')],
        [sg.T('', key='csntm_dimensions', background_color='#f0f0f0', size=(30, 3), expand_y=True)]
    ]
    intf_column = [
        [sg.Text('INTF (Online Liste)')],
        [sg.T('', key='intf_GA Number', size=spacer, background_color='#f0f0f0')],
        [sg.T('', key='intf_shelf', size=spacer, background_color='#f0f0f0')],
        [sg.T('', key='intf_contents', size=spacer, background_color='#f0f0f0')],
        [sg.T('', key='intf_date', size=spacer, background_color='#f0f0f0')],
        [sg.T('', key='intf_material', size=spacer, background_color='#f0f0f0')],
        [sg.T('', key='intf_leaves', size=spacer, background_color='#f0f0f0')],
        [sg.T('', key='intf_columns', size=spacer, background_color='#f0f0f0')],
        [sg.T('', key='intf_lines', size=spacer, background_color='#f0f0f0')],
        [
            sg.T('', key='intf_dimensions', background_color='#f0f0f0', size=(30, 3)),
            sg.Button('View Full Liste Description', key='view_liste')
        ]
    ]
    return [
        [sg.T('GA Number', size=spacer), sg.I('', key='ga_number'), sg.Button('Refresh', key='refresh_description')],
        [sg.Column(titles_column), sg.VerticalSeparator(), sg.Column(csntm_column), sg.VerticalSeparator(), sg.Column(intf_column)],
        [sg.T('Adjustments'), sg.Multiline('', expand_y=True, expand_x=True, key='cf_intf_comments'), sg.T('1994 Liste Details'), sg.Multiline('', expand_x=True, expand_y=True, key='94_liste')],
        [sg.Checkbox('Was the 1994 Liste consulted?', key='94_liste')]
    ]

def meta_data(spacer):
    return [
        [sg.T('CSNTM ID', size=spacer), sg.I('', key='csntm_id')],
        [sg.T('MS in Other Places', size=spacer), sg.I('', key='ms_other_places')],
        [sg.T('LDAB', size=spacer), sg.I('', key='ldab')],
        [sg.T('Pinakes', size=spacer), sg.I('', key='pinakes')],
        [sg.T('Bibliography', size=spacer), sg.Multiline('', key='bibliography', expand_y=True, expand_x=True)],
    ]

def quires(spacer, big_range):
    four = (4, 1)
    hundred = [i for i in range(101)]
    return [
        [sg.Stretch(), sg.Button('Remove Selected', key='remove_quire', button_color='#ff6e52'), sg.Listbox([], k='quire_structure', size=(80, 10), select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED), sg.Stretch()],
        [
            sg.T('Quire Number Actual'),
            sg.Spin(hundred, initial_value=1, k='quire_number_actual', size=four),
            sg.T('Quire Number Written'),
            sg.Input('', key='quire_number_written', size=four),
            sg.T('From'),
            sg.Spin(big_range, k='quire_from', size=four),
            sg.T('To'),
            sg.Spin(big_range, k='quire_to', size=four),
            ],
        [
            sg.T('Note'),
            sg.Input('', key='quire_note'),
            sg.Button('Add Quire', expand_x=True)
            ],
        [sg.T('Quire Comments'), sg.Multiline('', key='quire_comments', expand_y=True, expand_x=True)]
    ]

def physical_observations(spacer, five_one, big_range):
    eight = (10, 1)
    return [
        [sg.T('Primary Material', size=spacer), 
            sg.Radio('Papyrus', 'material', key='papyrus'), 
            sg.Radio('Parchment', 'material', key='parchment'),
            sg.Radio('Paper', 'material', key='paper')],
        [sg.T('Secondary Material', size=spacer), 
            sg.Radio('Papyrus', 'secondary_material', key='papyrus_secondary'), 
            sg.Radio('Parchment', 'secondary_material', key='parchment_secondary'),
            sg.Radio('Paper', 'secondary_material', key='paper_secondary')],
        [sg.T('Number of Leaves', size=spacer), sg.Spin(big_range, key='number_of_leaves', size=five_one)],
        [sg.T('Number of Columns', size=spacer), sg.Spin([1,2,3,4], key='number_of_columns', size=five_one)],
        [sg.T('Number of Lines', size=spacer), 
            sg.T('Min:'), sg.Spin([i for i in range(100)], key='lines_min', size=five_one),
            sg.T('Max:'), sg.Spin([i for i in range(100)], key='lines_max', size=five_one),
            sg.T('Normal:'), sg.Spin([i for i in range(100)], key='lines_normal', size=five_one),
        ],
        [sg.HorizontalSeparator(pad=(0, 10))],
        [sg.T('Width (cm)', size=spacer), 
            sg.T('Top Min:', size=eight), sg.Input('', key='width_min', size=eight), 
            sg.T('Top Max:', size=eight), sg.Input('', key='width_max', size=eight),
            sg.T('Bottom Min:', size=eight), sg.Input('', key='bottom_width_min', size=eight),
            sg.T('Bottom Max:', size=eight), sg.Input('', key='bottom_width_max', size=eight),
        ],
        [sg.T('Height (cm)', size=spacer), 
            sg.T('Inside Min:', size=eight), sg.Input('', key='height_min', size=eight),
            sg.T('Inside Max:', size=eight), sg.Input('', key='height_max', size=eight),
            sg.T('Outside Min:', size=eight), sg.Input('', key='bottom_height_min', size=eight),
            sg.T('Outside Max:', size=eight), sg.Input('', key='bottom_height_max', size=eight),
        ],
        [sg.T('Depth (cm)', size=spacer), 
            sg.T('Bottom:', size=eight), sg.Input('', key='depth_bottom', size=eight),
            sg.T('Top:', size=eight), sg.Input('', key='depth_top', size=eight)],
        [sg.HorizontalSeparator(pad=(0, 10))],
        [sg.T('Geometric Shape:', size=spacer), sg.Input('', key='geo_shape', expand_x=True)],
        [
            sg.T('Additional NT MSS?', size=spacer),
            sg.Checkbox('Yes', key='additional_nt_mss?', enable_events=True),
            sg.I('', key='additional_nt_mss', expand_x=True, disabled=True)
        ],
        [
            sg.T('Other Additional MSS?', size=spacer),
            sg.Checkbox('Yes', key='other_additional_mss?', enable_events=True),
            sg.I('', key='other_additional_mss', expand_x=True, disabled=True)
        ],
        [sg.T('Exterior Description', size=spacer), sg.Multiline('', key='exterior', expand_x=True, expand_y=True)],
        [sg.T('Condition', size=spacer), sg.Multiline('', key='condition', expand_x=True, expand_y=True)],
    ]

def foliation(spacer, five_one, big_range, WINDOWS: bool):
    if WINDOWS:
        row_height = 35
        justification = 'center'
    else:
        row_height = None
        justification = 'left'
    cat = [
        '-select-',
        'Front Inside Cover',
        'Back Inside Cover',
        # 'Blank',
        'Unnumbered',
        # 'Unnumbered Frontmatter', 
        # 'Unnumbered Backmatter',
        # 'Unnumbered Main Text',
        'Foliated',
        'Paginated',
        ]
    four = (4, 1)
    sections = [
        [sg.Button('Frontmatter', size=(15, 1), key='Frontmatter', expand_x=True, right_click_menu=['&Right', ['Frontmatter: Insert after Selected', 'Frontmatter: Insert at Beginning']])],
        [sg.Button('Body', size=(15, 1), key='Body', expand_x=True, right_click_menu=['&Right', ['Body: Insert after Selected', 'Body: Insert at Beginning']])],
        [sg.Button('Backmatter', size=(15, 1), key='Backmatter', expand_x=True, right_click_menu=['&Right', ['Backmatter: Insert after Selected', 'Backmatter: Insert at Beginning']])],
        [sg.Button('Other', size=(15, 1), key='Other', expand_x=True, right_click_menu=['&Right', ['Other: Insert after Selected', 'Other: Insert at Beginning']])],
        [sg.HorizontalSeparator(pad=(5, 20),)],
        [sg.Text('Add Subsection', justification='center', expand_x=True)],
        [sg.Drop(cat, default_value='-select-', k='folio_type', readonly=True, enable_events=True, expand_x=True)],
        [
            sg.pin(sg.T('Number: ', key='number_title', visible=False)),
            sg.pin(sg.Input('', k='number', size=four, enable_events=True, visible=False, expand_x=True), shrink=False, expand_x=True),
        ],
        [
            sg.pin(sg.T('Written: ', key='written_range_title', visible=False)), 
            sg.pin(sg.Input('', k='written_from', size=four, enable_events=True, visible=False)),
            sg.pin(sg.T('–', key='n-dash', visible=False)),
            sg.pin(sg.Input('', k='written_to', size=four, enable_events=True, visible=False))
        ],
        [sg.pin(sg.Button('    Add    ', key='Add', visible=False, right_click_menu=['&Right', ['Insert after Selected', 'Insert at Beginning']]), shrink=False, expand_x=True)],
    ]
    tree_col = [
        [sg.Tree(
                sg.TreeData(), 
                headings=['Folios/Pages', 'Landmarks'], 
                # expand_x=True, 
                expand_y=True, 
                key='foliation',
                auto_size_columns=True,
                show_expanded=True,
                justification=justification,
                # num_rows=10,
                row_height=row_height,
                col0_width=20,
                select_mode=sg.TABLE_SELECT_MODE_EXTENDED,
                right_click_menu=['&Right', ['Edit Selected', 'Remove Selected']],
                )],
    ]
    notes_col = [
        [sg.T('Numeration Notes')],
        [sg.Multiline('', expand_x=True, expand_y=True, k='numeration_note')],
    ]
    frame = [
        [
            sg.Column(sections),
            sg.Column(tree_col, expand_y=True),
            sg.Column(notes_col, expand_y=True)
        ],
        [    
            # sg.Drop(['Insert at End', 'Insert at Beginning', 'Insert after Selected'], default_value='Insert at End', k='insert_foliation', readonly=True),
            # sg.Button('Remove Selected', button_color='#ff6e52', size=(15, 1)),
        ],
        ]
    return [
        [
            sg.Text('Cover Images: '),
            sg.Checkbox('Front', k='cover_front'),
            sg.Checkbox('Back', k='cover_back'),
            sg.Checkbox('Edge', k='cover_edge'), 
            sg.Checkbox('Spine', k='cover_spine'), 
            sg.Checkbox('Top', k='cover_top'),
            sg.Checkbox('Bottom', k='cover_bottom'),
            sg.Checkbox('3D', k='cover_3d')
            ],
        # [sg.HorizontalSeparator()],
        [sg.Frame('Add Codex Sections', frame, border_width=8, expand_x=True, expand_y=True)],
        # [sg.HorizontalSeparator(pad=(0, 30))],
        [
            sg.Button('Calculate Total Images', 
            k='calculate'), sg.T('Total Images: '), 
            sg.T('0', k='total', background_color='#f0f0f0', size=(4, 1)),
            sg.Button('Create Spreadsheet', expand_x=True),
            # sg.Button('View All Folios', expand_x=True, right_click_menu=['&Right', ['View Decollated']]),
            ],
    ]

def content(spacer, big_range):
    five_one = (5, 1)
    return [
        [sg.T('Biblical Content Overview', size=spacer),
            sg.Check('Gospels', key='biblical_content_gospels'),
            sg.Check('Acts', key='biblical_content_acts'),
            sg.Check('Catholic', key='biblical_content_catholic'),
            sg.Check('Paul', key='biblical_content_paul'),
            sg.Check('Revelation', key='biblical_content_revelation'),
            sg.Check('Incomplete', key='biblical_content_incomplete')],
        [sg.T('Biblical Content Specific', size=spacer), sg.I('', key='biblical_content_specific', expand_x=True)],
        [sg.T('Language(s)', size=spacer),
            sg.Checkbox('Greek', key='language_greek'), 
            sg.Checkbox('Latin', key='language_latin'),
            sg.Checkbox('Coptic', key='language_coptic'),
            sg.Checkbox('Syriac', key='language_syriac'),
            sg.Checkbox("Ge'ez", key='language_geez'),
            sg.Checkbox('Georgian', key='language_georgian')],
        [sg.T('Script', size=spacer), sg.Checkbox('Majuscule', key='majuscule'), sg.Checkbox('Minuscule', key='minuscule')],
        [
            sg.T('Text', size=spacer), 
            sg.Radio('Continuous', 'text_type', key='continuous', enable_events=True), 
            sg.Radio('Lectionary:', 'text_type', key='lectionary', enable_events=True), 
            sg.Checkbox('Paschal Cycle', key='paschal', disabled=True), 
            sg.Checkbox('Sanctoral Cycle', key='sanctoral', disabled=True),
            sg.T('|'),
            sg.Checkbox('esk', key='esk', disabled=True),
            sg.Checkbox('sk', key='sk', disabled=True),
            sg.Checkbox('e', key='e', disabled=True),
            sg.Checkbox('k', key='k', disabled=True),
        ],
        [
            sg.T('Date', size=spacer),
            sg.T('Date Range Start:'), sg.Spin(big_range, key='date_range_start', size=five_one), 
            sg.T('Date Range End:'), sg.Spin(big_range, key='date_range_end', size=five_one),
            sg.T('Has Exact Year?'), sg.Check('Yes', key='exact_year?', enable_events=True),
            sg.Spin(big_range, key='exact_year', disabled=True, size=five_one),
        ],
       
        [sg.HorizontalSeparator()],
        [sg.Checkbox('Has Icons?', key='has_icon', size=spacer, enable_events=True), sg.Input('', key='icon_notes', expand_x=True, disabled=True)],
        [sg.Checkbox('Has Illuminations?', key='has_illumination', size=spacer, enable_events=True), sg.Input('', key='illumination_notes', expand_x=True, disabled=True)],
        [sg.Checkbox('Has Lection Marks?', key='has_lection', size=spacer, enable_events=True), sg.Input('', key='lection_notes', expand_x=True, disabled=True)],
        
        [sg.Checkbox('Has Etheses?', key='has_ektheses', size=spacer, enable_events=True), sg.Input('', key='ektheses_notes', expand_x=True, disabled=True)],
        [sg.Checkbox('Has OT Quotation Marks', key='has_otmarks', size=spacer, enable_events=True), sg.Input('', key='otmarks_notes', expand_x=True, disabled=True)],
        [sg.Checkbox('Has Neume?', key='has_neume', size=spacer, enable_events=True), sg.Input('', key='neume_notes', expand_x=True, disabled=True)],
        [sg.Checkbox('Has letter to Carpianus?', key='has_carpianus', size=spacer, enable_events=True), sg.Input('', key='carpianus_notes', expand_x=True, disabled=True)],
        [sg.Checkbox('Has Rubrication?', key='has_rubrication', size=spacer, enable_events=True), sg.Input('', key='rubrication_notes', expand_x=True, disabled=True)],
        [sg.Checkbox('Has Headings?', key='has_headings', size=spacer, enable_events=True), sg.Input('', key='headings_notes', expand_x=True, disabled=True)],
        [sg.Checkbox('Has Icons?', key='has_icons', size=spacer, enable_events=True), sg.Input('', key='icons_notes', expand_x=True, disabled=True)],
        [sg.Checkbox('Has Kephalaia?', key='has_kephalaia', size=spacer, enable_events=True), sg.Input('', key='kephalaia_notes', expand_x=True, disabled=True)],
    ]

def table_of_contents(spacer):
    title_column = [
        [sg.I('', key='toc_entry', expand_x=True)],
        [sg.Button('Add', key='add_toc'), sg.Stretch(), sg.Button('Sort', key='sort_toc'), sg.Button('Remove Selected', key='remove_toc', button_color='#ff6e52')],
        [sg.T(' ')],
        [sg.T(' ')],
        [sg.T(' ')],
        [sg.Stretch(), sg.Button('Import Table of Contents from Guide Sheet', key='import_toc'), sg.Stretch()],
    ]
    return [
        [sg.Column(title_column), sg.Listbox([], key='table_of_contents', expand_x=True, expand_y=True, select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED)],
    ]

def notable_features(spacer):
    commentary_options = [
        [
            sg.Checkbox('Framed', key='commentary_framed'), sg.Checkbox('Alternating', key='commentary_alternating'), sg.Checkbox('Different Color', key='commentary_color')
        ],
        [
            sg.Checkbox('Minuscule', key='commentary_minuscule'), sg.Checkbox('Majuscule', key='commentary_majuscule')
        ],
    ]
    return [
        [sg.Checkbox('Has Commentary?', key='has_commentary', size=spacer, enable_events=True), sg.Input('', key='commentary_notes', expand_x=True, disabled=True)], 
        [sg.T('', size=spacer), sg.Column(commentary_options)],
        [sg.T('Marginalia', size=spacer), sg.Multiline('', expand_x=True, k='marginalia', expand_y=True)],
        [sg.T('Other Notable Features', size=spacer), sg.Multiline('', expand_x=True, k='other_features', expand_y=True)],
    ]

def institution(spacer):
    twenty = (20, 1)
    former_owners = [
        [sg.B('Remove Selected', key='remove_former_institute', button_color='#ff6e52'), sg.Listbox([], key='former_owners', expand_x=True, expand_y=True, enable_events=True, select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED)],
        [
            sg.T('Owner:'), sg.I('', key='previous_owner', size=twenty),
            sg.T('Place:'), sg.I('', key='previous_place', size=twenty),
            sg.T('Shelf Number:'), sg.I('', key='previous_shelf', size=twenty),
            sg.T('Date'), sg.I('', key='date_sold', size=(10, 1)),
            sg.Button('Add', key='add_former_institute'),
        ],
    ]
    return [
        [sg.Text('Holding Institution/Individual', size=spacer, pad=(0, 5)), sg.I('', key='institution')],
        [sg.Text('Place', size=spacer, pad=(0, 5)), sg.I('', key='institution_place')],
        [sg.T('Shelf Number', size=spacer, pad=(0, 5)), sg.I('', key='shelf_number')],
        # [sg.HorizontalSeparator()],
        [sg.T("Institution's Description", size=spacer, pad=(0, 5)), sg.Multiline('', key='institution_description', expand_x=True, expand_y=True)],
        [sg.T('Additional Comments', size=spacer, pad=(0, 5)), sg.Multiline('', key='institution_comments', expand_x=True, expand_y=True)],
        [sg.HorizontalSeparator(pad=(0, 10))],
        [sg.Frame('Former Ownership', former_owners, expand_y=True, expand_x=True)],
    ]

def general(spacer):
    year, month, day = datetime.now().year, datetime.now().month, datetime.now().day
    tenbyone = (10, 1)
    return [
        [sg.T('Examinor', size=spacer), sg.I('', key='examiner')],
        [
            sg.T('Date Examined', size=spacer),
            sg.T('Year: '), sg.Spin([i for i in range(2000, 2031)], initial_value=year, key='year', size=tenbyone),
            sg.T('Month: '), sg.Spin([i for i in range(1, 13)], initial_value=month, key='month', size=tenbyone),
            sg.T('Day: '), sg.Spin([i for i in range(1, 32)], initial_value=day, key='day', size=tenbyone)
            ],
        [sg.HorizontalSeparator()],
        [sg.T('Imagers', size=spacer), sg.I('', key='imager')],
        [
            sg.T('Date Imaged', size=spacer),
            sg.T('Year: '), sg.Spin([i for i in range(2000, 2031)], initial_value=year, key='year_imaged', size=tenbyone),
            sg.T('Month: '), sg.Spin([i for i in range(1, 13)], initial_value=month, key='month_imaged', size=tenbyone),
            sg.T('Day: '), sg.Spin([i for i in range(1, 32)], initial_value=day, key='day_imaged', size=tenbyone)
            ],
        [sg.HorizontalSeparator()],
        [sg.T('General Comments', size=spacer), sg.Multiline('', key='general_comments', expand_x=True, expand_y=True)],
        [sg.T('Notes for Imaging Team\n(if not noted on the guide sheet)', size=(30, 2)), sg.Multiline('', key='notes_for_digitizers', expand_x=True, expand_y=True)],
    ]  

def submit_prepdoc(spacer):
    settings = es.get_settings()
    return [
        [sg.T('Guide Sheet:', size=spacer, pad=(0, 10)), sg.I('', key='guide_sheet', expand_x=True), sg.FileBrowse(initial_folder=settings['excel_folder'], file_types=(('Excel File', '*.xlsx'),))],
        [sg.T('Project Folder:', size=spacer, pad=(0, 10)), sg.I(settings['project_folder'], key='project_folder', expand_x=True), sg.FolderBrowse(initial_folder=settings['project_folder'])],
        [sg.Button('Package Prepdoc Files', pad=(0, 10), expand_x=True, key='package')],
    ]

def tabs(WINDOWS):
    spacer = (30, 1)
    big_range = [i for i in range(2000)]
    five_one = (5, 1)
    return [
        [sg.Tab('Cf. INTF', cf_intf(spacer))],
        [sg.Tab('Physical Observations', physical_observations(spacer, five_one, big_range))],
        [sg.Tab('Foliation', foliation(spacer, five_one, big_range, WINDOWS))],
        [sg.Tab('Quires', quires(spacer, big_range))],
        [sg.Tab('Content', content(spacer, big_range))],
        [sg.Tab('Notable', notable_features(spacer))],
        [sg.Tab('Table of Contents', table_of_contents(spacer))],
        [sg.Tab('Metadata', meta_data(spacer))],
        [sg.Tab('Institution', institution(spacer))],
        [sg.Tab('General', general(spacer))],
        [sg.Tab('Package', submit_prepdoc(spacer))],
    ]
    

def layout(WINDOWS: bool):
    twenty = (20, 1)
    return [
        [sg.TabGroup(tabs(WINDOWS), expand_y=True)],
        [
            sg.Button('Save As', size=twenty, expand_x=True),
            sg.Button('Quick Save'),
            sg.Button('Load from Saved File', expand_x=True),
            # sg.Button('Export to DOCX', size=twenty, expand_x=True), #TODO: Finish this function but also figure out how to count inside covers correctly.
            sg.Button('Exit'),                                         # Dan really likes the inside covers to be frontmatter even though this means we have a
        ]                                                              # "b" without a corresponding "a" and an "a" without a corresponding "b". I would 
    ]                                                                  # prefer if we could just call the front cover 0a A LEAST FOR THE PURPOSE OF IMAGING. 
