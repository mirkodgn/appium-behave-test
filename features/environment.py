import os

#carica variabili scritte nel file .env
from dotenv import load_dotenv

from appium import webdriver
from appium.options.android import UiAutomator2Options

#gestione download di file (piccoli o grandi) ospitati su Google Drive
from utils.utils import *

load_dotenv()

def before_all(context):
    """Configurazione iniziale eseguita una sola volta"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app_folder = os.path.join(project_root, "app")
    apk_name = os.getenv("APP_NAME")
    
    if not apk_name:
        raise Exception("ERRORE: APP_NAME non trovato nel file .env")
        
    apk_path = os.path.join(app_folder, apk_name)
    
    # Creiamo la cartella 'app' se non esiste
    if not os.path.exists(app_folder):
        os.makedirs(app_folder)

    # Scarichiamo l'APK solo se NON esiste
    if not os.path.exists(apk_path):
        drive_id = os.getenv("DRIVE_FILE_ID")
        if not drive_id:
            raise Exception("ERRORE: DRIVE_FILE_ID non trovato nel file .env")
        download_file_from_google_drive(drive_id, apk_path)
    else:
        print(f"\n[INFO] APK già presente in {apk_path}. Salto il download.\n")

def before_scenario(context, scenario):
    options = UiAutomator2Options()
    options.platform_name = os.getenv("PLATFORM_NAME", "Android")
    options.device_name = os.getenv("DEVICE_NAME", "Android Device")
    options.automation_name = os.getenv("AUTOMATION_NAME", "UiAutomator2")
    
    # Usiamo 'noReset' per evitare che Appium pulisca i dati delle app ogni volta
    options.set_capability("noReset", True)
    # Impediamo ad Appium di cercare un'activity di default all'avvio del driver
    options.set_capability("autoLaunch", False) 

    try:
        context.driver = webdriver.Remote(os.getenv("APPIUM_SERVER"), options=options)
    except Exception as e:
        print(f"ERRORE: Impossibile connettersi al server Appium: {e}")
        raise

def after_scenario(context, scenario):
    """Chiude la sessione alla fine di ogni test"""
    if hasattr(context, 'driver'):
        context.driver.quit()