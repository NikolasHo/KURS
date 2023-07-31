### Helpers

import os
from datetime import datetime
from django.conf import settings



def get_subfolders(directory):
    subfolders = []
    for root, dirs, files in os.walk(directory):
        for dir in dirs:
            subfolders.append(dir)
    return subfolders


##### Settings

def get_backups():
    backup_directory = os.path.join(settings.BASE_DIR, 'backup')
    
     
    if not os.path.exists(backup_directory):
        os.makedirs(backup_directory)
    
    # Alle Dateinamen im Backup-Verzeichnis auflisten
    backup_files = os.listdir(backup_directory)
   
    # Liste für Backup-Dateinamen mit Datum initialisieren
    backup_list = []
    
    for file_name in backup_files:
        # Nur Backup-Dateien berücksichtigen (z.B. mit .sqlite3 am Ende)
        if file_name.endswith('.sqlite3'):
            # Das Datum aus dem Dateinamen extrahieren (Annahme: Dateinamen haben das Format "db_backup_YYYY-MM-DD_HH-MM-SS.sqlite3")
            date_string = file_name.split('_')[2].split('.')[0] + "_" + file_name.split('_')[3].split('.')[0]
            backup_date = datetime.strptime(date_string, "%Y-%m-%d_%H-%M-%S")
            formatted_date = backup_date.strftime("%Y%m%d_%H:%M:%S")
        
            # Dateinamen und Datum in die Liste hinzufügen
            backup_list.append((file_name, formatted_date))
        
    return backup_list
    