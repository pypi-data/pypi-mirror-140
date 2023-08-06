import json
import os

from natsort import natsorted

import prepify.py.read_doc_form as rdf


def prune_failsafe():
    filenames = natsorted(os.listdir(), reverse=True)
    filenames = [f for f in filenames if f.startswith('failsafe')]
    for i, f in enumerate(filenames):
        if i >= 9:
            try:
                os.remove(f)
            except Exception as e:
                print(f'Failed to delete {f} because {e}')

def auto_save(values: dict, window):
    to_save = rdf.get_doc_data(values, window)
    with open(f'{values["csntm_id"]}.json', 'w', encoding='utf-8') as f:
        json.dump(to_save, f, ensure_ascii=False, indent=4)

