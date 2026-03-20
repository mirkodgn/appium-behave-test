import gdown
import time
import os
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def download_file_from_google_drive(file_id, destination):
    """Scarica l'APK da Google Drive usando gdown"""
    url = f'https://drive.google.com/uc?id={file_id}'
    print(f"\n--- Avvio download APK da Google Drive (ID: {file_id}) ---")
    
    # gdown scarica il file. Se il download fallisce, output sarà None
    output = gdown.download(url, destination, quiet=False, fuzzy=True)
    
    if not output:
        raise Exception("Errore critico: il download dell'APK è fallito.")
    print(f"--- Download completato con successo: {destination} ---\n")

def clean_youtube_ui(driver):
    """Chiude ricorsivamente gli ostacoli usando attese brevi ma attive"""
    interrupts = [
        (AppiumBy.ID, "com.google.android.youtube:id/skip_ad_button", "Salta Annuncio"),
        (AppiumBy.ACCESSIBILITY_ID, "Chiudi", "Play Store"),
        (AppiumBy.XPATH, "//android.widget.Button[@content-desc='Chiudi pannello annunci']", "Pannello Sponsorizzato"),
        (AppiumBy.ID, "com.google.android.youtube:id/close_button", "Chat/Ads Close")
    ]
    
    max_attempts = 5
    # Spostiamo il tasto "Salta" in cima perché è il più critico
    
    for i in range(max_attempts):
        found = False
        for selector, value, name in interrupts:
            try:
                # Usiamo un WebDriverWait molto breve (2 secondi) invece di find_elements.
                # Questo permette di "beccare" il tasto anche se appare con un leggero ritardo.
                element = WebDriverWait(driver, 2.0).until(
                    EC.element_to_be_clickable((selector, value))
                )
                print(f"[CLEAN] {name} rilevato e cliccato.")
                element.click()
                time.sleep(1) # Tempo per l'animazione di chiusura
                found = True
                break 
            except:
                # Se non appare entro 2 secondi, passa al prossimo controllo
                continue
        
        if not found:
            break