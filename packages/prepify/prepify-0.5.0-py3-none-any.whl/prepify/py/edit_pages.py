

import PySimpleGUI as sg

def table_from_guide(guide: list[dict]):
    table = []
    for row in guide:
        table.append(
            [
                # row['Image #'], 
                row['Landmark'], 
                row['Actual Folio'], 
                # row['Contents'], 
                # row['Notes for Imagers'], 
                # row['Notes']
            ]
                    )
    return table

def layout():  
    headings = [
        # 'Image #',
        'Landmark', 
        'Actual Folio', 
        # 'Contents', 
        # 'Notes for Imagers', 
        # 'Notes',
        ]

    return [[
        sg.Table(
            [[]], 
            headings=headings, 
            num_rows=30, 
            alternating_row_color='#e6d3a8',
            key='folios_table',
            # enable_click_events=True,
            bind_return_key=True,
            pad=(10, 10),
            # hide_vertical_scroll=True,
            justification='center',
            )
        ]]

def edit_pages(sections: list):
    return sg.Window('View Guide', layout(), debugger_enabled=False)
    # window.read()
    # window.close()
    # del window
