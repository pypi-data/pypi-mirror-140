import json
from pathlib import Path

import PySimpleGUI as sg

RESOURCES = Path(__file__).parent.parent.joinpath('resources').as_posix()

def get_settings():
    try:
        with open(f'{RESOURCES}/settings.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        settings = {'excel_folder': '',
                    'prepdoc_folder': '',
                    'project_folder': ''}
        with open(f'{RESOURCES}/settings.json', 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4)
        return settings

def update_settings(setting: str, value: str):
    '''"excel_folder", "prepdoc_folder", "project_folder"'''
    settings = get_settings()
    settings[setting] = value
    try:
        with open(f'{RESOURCES}/settings.json', 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        sg.popup_ok(f'Failed to update the settings file.\n(For David: {e})')