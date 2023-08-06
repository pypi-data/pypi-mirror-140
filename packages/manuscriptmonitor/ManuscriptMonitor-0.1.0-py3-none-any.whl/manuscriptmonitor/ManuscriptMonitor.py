import json
import re
import time
from pathlib import Path
import sys

import pandas as pd
import PySimpleGUI as sg
from rich.live import Live
from rich.table import Table
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class Watcher:
    def __init__(self, directory, handler=FileSystemEventHandler()):
        self.observer = Observer()
        self.handler = handler
        self.directory = directory

    def run(self):
        self.observer.schedule(
            self.handler, self.directory, recursive=True)
        self.observer.start()
        print(f"\nManuscript Monitor started in {self.directory}\n")
        try:
            while True:
                time.sleep(.2)
        except:
            self.observer.stop()
        self.observer.join()
        print("\nManuscript Monitor Terminated\n")

class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        created = event.src_path
        if created.endswith('.iiq'):
            # print(created)
            created = re.sub(r'[/\\].+[/\\]', '', created).replace('P', '').replace('M', '')
            created = created.replace('C:', '').replace('.txt', '')
            created = re.sub(r'_.+_', '', created)
            created = created.replace('.iiq', '')
            created = created.lstrip('0')
            # print(created)
            if created == 'a' or created == 'b':
                created = f'0{created}'
            ######################
            ### business logic ###
            ######################
            prev, now, next = get_rows(created)
            global live
            live.update(generate_table(prev, now, next))
            ######################

def generate_table(prev_row: dict, now_row: dict, next_row: dict) -> Table:
    """Make a new table."""
    table = Table()
    table.add_column('Landmark')
    table.add_column('Actual Folio')
    table.add_column('Notes for Imagers')

    table.add_row(f"{prev_row.get('Landmark')}", f"{prev_row.get('Actual Folio')}", f"{prev_row.get('Notes for Imagers')}")
    table.add_row(f'[bold green]{now_row.get("Landmark")}', f'[bold green]{now_row.get("Actual Folio")}', f'[bold green]{now_row.get("Notes for Imagers")}')
    table.add_row(f"{next_row.get('Landmark')}", f"{next_row.get('Actual Folio')}", f"{next_row.get('Notes for Imagers')}")
    return table

def get_rows(just_captured: dict):
    prev = {}
    now = {}
    next = {}
    for i, d in enumerate(guide_dict):
        if d['Image #'] == just_captured:
            prev = d
            try:
                now = guide_dict[i+1]
            except:
                pass
            try:
                next = guide_dict[i+2]
            except:
                pass

    return prev, now, next

def get_folders():
    try:
        with open('settings.json', 'r') as f:
            settings = json.load(f)
        settings['last_folder']
        settings['excel_folder']
    except:
        settings = {'last_folder': '', 'excel_folder': ''}
    capture_output = sg.popup_get_folder('', no_window=True, initial_folder=settings['last_folder'])
    if not capture_output:
        sys.exit()
    excel_file = sg.popup_get_file('', no_window=True, initial_folder=settings['excel_folder'], file_types=(('Excel File', '*.xlsx'),))
    if not excel_file:
        sys.exit()
    excel_folder = Path(excel_file).parent.as_posix()
    settings['last_folder'] = capture_output
    settings['excel_folder'] = excel_folder
    with open('settings.json', 'w') as f:
        json.dump(settings, f)
    return capture_output, excel_file

def get_spreadsheet_data(excel_file):
    df = pd.read_excel(excel_file)
    df = df.fillna('')
    list_of_dicts = df.to_dict('records')
    return list_of_dicts


capture_output, excel_file = get_folders()
guide_dict = get_spreadsheet_data(excel_file)

if __name__ == "__main__":
    with Live(generate_table({}, {}, {}), refresh_per_second=5) as live:
        w = Watcher(capture_output, MyHandler())
        w.run()

def main():
    global live
    with Live(generate_table({}, {}, {}), refresh_per_second=5) as live:
        w = Watcher(capture_output, MyHandler())
        w.run()    
