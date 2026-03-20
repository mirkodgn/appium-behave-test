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

# def setup_wifi(driver, ssid, password):
#     """Configura il Wi-Fi navigando nell'interfaccia di sistema"""
#     wait = WebDriverWait(driver, 15)
    
#     print(f"\n[WIFI] Apertura impostazioni Wi-Fi per: {ssid}")
    
#     # 1. Forza l'apertura della pagina Wi-Fi tramite Intent di sistema
#     driver.execute_script('mobile: startActivity', {
#         'action': 'android.settings.WIFI_SETTINGS'
#     })
    
#     try:
#         # 2. Cerchiamo la rete nella lista
#         # Usiamo un selettore che cerca il testo esatto dell'SSID
#         wifi_network_xpath = f"//android.widget.TextView[@text='{ssid}']"
        
#         # Scorriamo finché non troviamo la rete (se necessario)
#         # Per ora proviamo il click diretto se visibile
#         network_element = wait.until(EC.element_to_be_clickable((AppiumBy.XPATH, wifi_network_xpath)))
#         network_element.click()
#         print(f"[WIFI] Rete {ssid} selezionata.")
        
#         # 3. Inserimento Password
#         # Solitamente il campo password ha la classe EditText
#         password_field = wait.until(EC.presence_of_element_located((AppiumBy.CLASS_NAME, "android.widget.EditText")))
#         password_field.send_keys(password)
#         print("[WIFI] Password inserita.")
        
#         # 4. Click sul tasto Connetti o Partecipa
#         # Cerchiamo un bottone che contenga "Connetti", "Partecipa" o "OK"
#         connect_button_xpath = "//*[@text='Connetti' or @text='PARTECIPA' or @text='OK' or @text='Salva']"
#         driver.find_element(AppiumBy.XPATH, connect_button_xpath).click()
        
#         print("[WIFI] Pulsante connetti premuto. Attesa stabilizzazione...")
#         time.sleep(5) # Tempo per negoziare la connessione
        
#     except Exception as e:
#         print(f"[WIFI] Errore durante la configurazione: {e}")
#         # Se la rete risulta già "Connessa", Appium potrebbe non trovare i campi. 
#         # In quel caso consideriamo il setup riuscito.
#         if "Connesso" in driver.page_source:
#             print("[WIFI] Il dispositivo risulta già connesso alla rete.")
#         else:
#             raise

import time
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# def setup_wifi(driver, ssid, password):
#     """Configura il Wi-Fi navigando nelle impostazioni di sistema (ColorOS/OPPO/Realme)"""
#     wait = WebDriverWait(driver, 15)
    
#     print(f"\n[WIFI] Apertura impostazioni Wi-Fi per la rete: {ssid}")
    
#     # 1. Forza l'apertura della pagina Wi-Fi tramite Intent di sistema
#     driver.execute_script('mobile: startActivity', {
#         'action': 'android.settings.WIFI_SETTINGS'
#     })
    
#     try:
#         # 2. Cerchiamo la rete nella lista usando il testo esatto dell'SSID
#         print(f"[WIFI] Ricerca SSID '{ssid}' nella lista...")
#         wifi_network_xpath = f"//android.widget.TextView[@text='{ssid}']"
        
#         network_element = wait.until(EC.element_to_be_clickable((AppiumBy.XPATH, wifi_network_xpath)))
#         network_element.click()
#         print(f"[WIFI] Rete selezionata.")
        
#         # 3. Inserimento Password
#         # Il campo password ha resource-id "android:id/input" nel tuo XML
#         password_field = wait.until(EC.presence_of_element_located((AppiumBy.ID, "android:id/input")))
#         password_field.send_keys(password)
#         print("[WIFI] Password inserita correttamente.")

#         # TRUCCO: Nascondiamo la tastiera per assicurarci che non copra i tasti in alto
#         if driver.is_keyboard_shown():
#             driver.hide_keyboard()
#             time.sleep(1)
        
#         # 4. Click sul tasto di conferma (Spunta "Accedi" in alto a destra)
#         # Basato sul tuo XML: id 'com.coloros.wirelesssettings:id/menu_save' e desc 'Accedi'
#         print("[WIFI] Clicco sul tasto di conferma 'Accedi'...")
        
#         try:
#             # Tentativo primario con ID specifico ColorOS
#             confirm_btn = wait.until(EC.element_to_be_clickable(
#                 (AppiumBy.ID, "com.coloros.wirelesssettings:id/menu_save")
#             ))
#             confirm_btn.click()
#         except:
#             # Fallback con Accessibility ID (content-desc)
#             confirm_btn = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Accedi")
#             confirm_btn.click()
            
#         print("[SUCCESS] Configurazione Wi-Fi inviata. Attesa connessione...")
        
#         # 5. Attesa per l'ottenimento dell'indirizzo IP
#         time.sleep(7) 
        
#     except Exception as e:
#         print(f"[WIFI] Nota: Procedura interrotta o errore. Verifico se già connesso.")
#         # Se la rete era già salvata, potremmo essere già dentro.
#         # Se non vediamo errori bloccanti, lasciamo proseguire il test.
#         if ssid in driver.page_source:
#              print(f"[WIFI] Il dispositivo sembra già configurato per {ssid}.")
#         else:
#             raise Exception(f"Errore durante il setup Wi-Fi: {e}")

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