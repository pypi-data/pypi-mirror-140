import platform

import PySimpleGUI as sg

import prepify.py.backup as bu
import prepify.py.document_layout as dl
import prepify.py.export_to_docx as ed
import prepify.py.foliation as fo
import prepify.py.guide_sheet as gs
import prepify.py.read_doc_form as rdf
import prepify.py.load_liste as ll
from prepify.py import package
import prepify.py.quires as qu


if platform.system() == 'Windows':
    WINDOWS = True
    WINDOW_SIZE = (1000, 800)
else:
    WINDOW_SIZE = (600, 400)
    WINDOWS = False
#     import ctypes
#     ctypes.windll.shcore.SetProcessDpiAwarene(1)
  

def main_loop(window: sg.Window, foliation: fo.Foliation):
    view_liste = False
    timeout = None
    liste_window = None

    while True:
        event, values = window.read(timeout=timeout)

        if event in [sg.WIN_CLOSED, None, sg.WIN_X_EVENT]:
            break

        elif event == 'Save As':
            rdf.save_doc_data(values, window, foliation)
        elif event == 'Quick Save':
            rdf.quick_save(values, window, foliation)
        elif event == 'Load from Saved File':
            foliation = rdf.load_from_saved(window)

        # PARSE PREP DOC
        elif event in {'number', 'written_from', 'written_to'}:
            fo.enforce_spin(values, window)
            if event == 'number':
                if values['number'] != '':
                    window['Add'].update(visible=True)
                else:
                    window['Add'].update(visible=False)
            elif event in {'written_from', 'written_to'}:
                if values['written_from'] == '' or values['written_to'] == '':
                    window['Add'].update(visible=False)
                else:
                    window['Add'].update(visible=True)

        elif event in {'Add', 'Insert after Selected', 'Insert at Beginning'}:
            fo.submit_section(values, window, foliation, event)
            rdf.hide_all_folio_options(window)

        elif event == 'Remove Selected' and values['foliation'] != []:
            fo.remove_section(values, window, foliation)
            rdf.decolor_buttons(window, foliation.sections)
            # rdf.remove_selected_from_listbox(values, window, 'foliation')
            # fo.index_insert_at(window)

        elif event in {'Frontmatter', 'Body', 'Backmatter'}:
            fo.submit_main_section(values, window, event, foliation, 'Add')

        elif event in {'Frontmatter: Insert after Selected', 'Frontmatter: Insert at Beginning',
                        'Body: Insert after Selected', 'Body: Insert at Beginning',
                        'Backmatter: Insert after Selected', 'Backmatter: Insert at Beginning'}:
            items = event.split(': ')
            fo.submit_main_section(values, window, items[0], foliation, items[1])

        elif event == 'Other':
            fo.submit_other_section(values, window, foliation, 'Add')

        elif event in {'Other: Insert after Selected', 'Other: Insert at Beginning'}:
            items = event.split(': ')
            fo.submit_other_section(values, window, foliation, items[1])

        elif event == 'calculate' and foliation.sections != []:
            foliation.calculate_total_images(values, window)
        elif event == 'Create Spreadsheet' and foliation.sections != []:
            try:
                foliation.create_xslx()
                fo.open_excel()
            except IndexError:
                print('There are no folios to add')
        elif event == 'Add Quire':
            qu.add_quire(values, window)
        elif event == 'remove_quire' and values['quire_structure'] != []:
            rdf.remove_selected_from_listbox(values, window, 'quire_structure')
        elif event == 'Export to DOCX':
            data = rdf.get_doc_data(values, window)
            ed.to_docx(data)
        elif event in ('refresh_description', 'ga_number'):
            ll.load_cf_intf(values, window)
            rdf.load_cf_csntm(values, window)
        elif event == 'import_toc':
            gs.import_toc(window)
        elif event == 'add_toc':
            rdf.add_toc_entry(values, window)
        elif event == 'remove_toc':
            rdf.remove_selected_from_listbox(values, window, 'table_of_contents')

        elif event == 'package':
            package.package(values, window)
        elif event == 'add_former_institute':
            rdf.add_former_institute(values, window)
        elif event == 'remove_former_institute':
            rdf.remove_selected_from_listbox(values, window, 'former_owners')
        elif event == 'sort_toc':
            rdf.sort_toc(window)
        elif event == 'Edit Selected':
            if len(values['foliation']) != 1:
                continue
            sel = foliation.get_section_by_index(values['foliation'][0])
            if not sel:
                continue
            if sel['main_section']:
                sg.popup_ok('Main Sections cannot be edited. Instead, replace and remove.', title='FYI')
                continue
            foliation_values = fo.edit_foliation_window(sel['foliation_type'], sel.get('number', ''), sel.get('written_from', ''), sel.get('written_to', ''))
            if not foliation_values:
                continue
            foliation_values['foliation'] = values['foliation']
            fo.submit_section(foliation_values, window, foliation, 'replace')

    # on exit
        elif event in (sg.WINDOW_CLOSE_ATTEMPTED_EVENT, None, 'Exit', sg.WIN_X_EVENT):
            if values['ga_number'] == '':
                break
            if sg.popup_yes_no('Do you really want to exit?', title='Confirm Exit') == 'Yes':
                bu.prune_failsafe()
                rdf.save_doc_data(values, window, save_temp=True)
                break

        ##################
        # disable/enable #
        ##################
        elif event == 'exact_year?':
            has_exact_year = not values['exact_year?']
            window['exact_year'].update(disabled=has_exact_year)
        elif event in rdf.DISABLED:
            elem = event.replace('has_', '')
            elem = f'{elem}_notes'
            window[elem].update(disabled=not values[event])
        elif event in ('lectionary', 'continuous'):
            v = not values['lectionary']
            window['paschal'].update(disabled=v)
            window['sanctoral'].update(disabled=v)
            window['sk'].update(disabled=v)
            window['esk'].update(disabled=v)
            window['e'].update(disabled=v)
            window['k'].update(disabled=v)
        elif event == 'additional_nt_mss?':
            window['additional_nt_mss'].update(disabled=not values['additional_nt_mss?'])
        elif event == 'other_additional_mss?':
            window['other_additional_mss'].update(disabled=not values['other_additional_mss?'])
        elif event == 'folio_type':
            rdf.hide_unhide_foliation(values, window)


        #####################
        # View Liste Window #
        #####################
        elif event == 'view_liste':
            view_liste = True
            timeout = 100
            liste_entry = ll.get_full_liste(values)
            liste_window = sg.Window('Full Liste Entry', ll.full_liste_layout(liste_entry), size=WINDOW_SIZE)
        if view_liste:
            ev2, _, = liste_window.read(timeout=100)
            if ev2 in ('Close', sg.WIN_CLOSED, sg.WIN_X_EVENT, None):
                liste_window.close()
                view_liste = False
                timeout = None
    try:
        liste_window.close()
    except:
        pass

def main():
    sg.set_options(font=('Helvetica', '14'), dpi_awareness=True)
    sg.theme('LightBrown3')
    window = sg.Window(
        'Prepify v0.5.1', dl.layout(WINDOWS), 
        resizable=True, 
        enable_close_attempted_event=True,
        debugger_enabled=False,
        )
    foliation = fo.Foliation()
    
    try:
        main_loop(window, foliation)
    except Exception as e:
        print('Catastrophic Crash Caught')
        # try:
        values = window.read()
        save_path = rdf.save_doc_data(values, window, foliation, crashed=True)
        sg.popup_ok(f'Prepify crashed for a reason unknown to DF.\nThe prepdoc in progress was saved in the same folder as Prepify and named "{save_path}".\nIt is unlikely that your data was lost.\n(For David: {e})', title='BUMMER')
        # except Exception as e:
        #     sg.popup_ok(f"I'm verry sorry. Prepify crashed in a way that DF did not anticipate.\nAny entered data was not saved.\n(For David: {e})")
    try:
        window.close()
    except:
        pass # window already destroyed

if __name__ == '__main__':
    main()
