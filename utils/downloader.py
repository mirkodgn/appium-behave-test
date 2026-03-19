import os
import gdown

def download_file_from_google_drive(file_id, destination):
    """Scarica l'APK da Google Drive usando gdown"""
    url = f'https://drive.google.com/uc?id={file_id}'
    print(f"\n--- Avvio download APK da Google Drive (ID: {file_id}) ---")
    
    # gdown scarica il file. Se il download fallisce, output sarà None
    output = gdown.download(url, destination, quiet=False, fuzzy=True)
    
    if not output:
        raise Exception("Errore critico: il download dell'APK è fallito.")
    print(f"--- Download completato con successo: {destination} ---\n")