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

def setup_wifi(driver, ssid, password):
    """Configura il Wi-Fi attivandolo se necessario (ColorOS/OPPO/Realme)"""
    wait = WebDriverWait(driver, 15)
    
    print(f"\n[WIFI] Apertura impostazioni Wi-Fi...")
    
    # 1. Forza l'apertura della pagina Wi-Fi
    driver.execute_script('mobile: startActivity', {
        'action': 'android.settings.WIFI_SETTINGS'
    })
    
    try:
        # 2. CONTROLLO STATO WI-FI (Basato sul tuo XML)
        print("[WIFI] Verifica se il Wi-Fi è attivo...")
        wifi_switch_id = "com.coloros.wirelesssettings:id/switchWidget"
        
        # Cerchiamo lo switch
        wifi_switch = wait.until(EC.presence_of_element_located((AppiumBy.ID, wifi_switch_id)))
        
        # Se il testo è "Non attivato", dobbiamo accenderlo
        if wifi_switch.text == "Non attivato":
            print("[WIFI] Wi-Fi disattivato. Attivazione in corso...")
            wifi_switch.click()
            # Attendiamo che la lista delle reti compaia (buffering del sistema)
            time.sleep(5) 
        else:
            print("[WIFI] Wi-Fi già attivo.")

        # 3. RICERCA DELLA RETE NELLA LISTA
        print(f"[WIFI] Ricerca SSID '{ssid}'...")
        wifi_network_xpath = f"//android.widget.TextView[@text='{ssid}']"
        
        # Attendiamo che la rete specifica appaia nella lista
        network_element = wait.until(EC.element_to_be_clickable((AppiumBy.XPATH, wifi_network_xpath)))
        network_element.click()
        print(f"[WIFI] Rete {ssid} selezionata.")
        
        # 4. INSERIMENTO PASSWORD
        # Il campo password ha resource-id "android:id/input"
        password_field = wait.until(EC.presence_of_element_located((AppiumBy.ID, "android:id/input")))
        password_field.send_keys(password)
        print("[WIFI] Password inserita.")

        # Nascondiamo la tastiera per liberare la visuale sul tasto Accedi
        if driver.is_keyboard_shown():
            driver.hide_keyboard()
            time.sleep(1)
        
        # 5. CLICK TASTO CONFERMA "ACCEDI" (In alto a destra)
        print("[WIFI] Conferma connessione...")
        try:
            confirm_btn = wait.until(EC.element_to_be_clickable(
                (AppiumBy.ID, "com.coloros.wirelesssettings:id/menu_save")
            ))
            confirm_btn.click()
        except:
            # Fallback se l'ID cambiasse ma il content-desc restasse "Accedi"
            driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Accedi").click()
            
        print(f"[SUCCESS] Richiesta di connessione a {ssid} inviata.")
        time.sleep(7) # Attesa per rilascio IP
        
    except Exception as e:
        # Se la rete era già connessa, l'eccezione verrà gestita qui
        if ssid in driver.page_source:
             print(f"[WIFI] Il dispositivo risulta già connesso a {ssid}.")
        else:
            print(f"[WIFI] Errore durante la procedura: {e}")
            raise

def forget_wifi(driver, ssid):
    """Entra nei dettagli della rete e la rimuove (ColorOS/OPPO/Realme)"""
    wait = WebDriverWait(driver, 15)
    
    print(f"\n[CLEANUP] Apertura impostazioni Wi-Fi per: {ssid}")
    driver.execute_script('mobile: startActivity', {
        'action': 'android.settings.WIFI_SETTINGS'
    })
    
    try:
        # 1. Click sulla rete connessa (Kineton02)
        print(f"[CLEANUP] Entro nei dettagli di '{ssid}'...")
        # Cerchiamo la riga che ha il testo dell'SSID
        network_row = wait.until(EC.element_to_be_clickable(
            (AppiumBy.XPATH, f"//*[@text='{ssid}']")
        ))
        network_row.click()
        time.sleep(2) # Attesa caricamento pagina dettagli

        # 2. Click su "Rimuovi questa rete" usando il TESTO
        print("[CLEANUP] Cerco il tasto 'Rimuovi questa rete'...")
        
        # Proviamo prima col testo esatto, poi con una ricerca parziale
        forget_selectors = [
            (AppiumBy.XPATH, "//*[@text='Rimuovi questa rete']"),
            (AppiumBy.XPATH, "//*[contains(@text, 'Rimuovi')]"),
            (AppiumBy.ID, "com.coloros.wirelesssettings:id/forget_btn") # Fallback ID
        ]

        found_btn = False
        for selector, value in forget_selectors:
            try:
                # Usiamo un timeout brevissimo per ogni tentativo
                btn = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((selector, value)))
                btn.click()
                print(f"[CLEANUP] Tasto rimosso cliccato con: {value}")
                found_btn = True
                break
            except:
                continue
        
        if not found_btn:
            raise Exception("Impossibile trovare il tasto per rimuovere la rete.")

        # 3. Gestione Pop-up di conferma
        print("[CLEANUP] Gestione eventuale conferma...")
        try:
            # ColorOS spesso mostra un secondo tasto "Rimuovi" in rosso nel pop-up
            confirm_btn = WebDriverWait(driver, 4).until(EC.element_to_be_clickable(
                (AppiumBy.XPATH, "//android.widget.Button[@text='Rimuovi' or @text='RIMUOVI']")
            ))
            confirm_btn.click()
            print("[CLEANUP] Conferma rimozione cliccata.")
        except:
            print("[DEBUG] Nessun pop-up di conferma apparso.")

        print(f"[SUCCESS] Rete {ssid} dimenticata.")

    except Exception as e:
        print(f"[ERROR] Fallimento cleanup: {e}")
        # Salviamo l'XML di errore per vedere cosa vedeva Appium in quel momento
        with open("error_layout_cleanup.xml", "w") as f:
            f.write(driver.page_source)
        raise