import gdown
import time
import os
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

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
    """Chiude ostacoli UI usando refresh forzati e click diretti"""
    
    # Mappa degli ostacoli con selettori e coordinate di sicurezza (opzionali)
    # Le coordinate [x, y] sono indicative per un display 1080p, 
    # basate sugli XML inviati (tasto 'Salta' in basso a destra, 'Chiudi' in alto a destra)
    interrupts = [
        {"selector": (AppiumBy.ID, "com.google.android.youtube:id/skip_ad_button"), "name": "Salta Annuncio"},
        {"selector": (AppiumBy.ACCESSIBILITY_ID, "Chiudi"), "name": "Play Store"},
        {"selector": (AppiumBy.XPATH, "//android.widget.Button[@content-desc='Chiudi pannello annunci']"), "name": "Pannello Sponsorizzato"},
        {"selector": (AppiumBy.ID, "com.google.android.youtube:id/close_button"), "name": "Chat/Ads Close"}
    ]

    max_attempts = 5
    for i in range(max_attempts):
        found_in_round = False
        
        # 1. FORZA REFRESH: A volte Appium legge una cache vecchia del layout
        _ = driver.page_source 
        
        for item in interrupts:
            try:
                # Usiamo presence invece di clickable per essere più aggressivi
                element = WebDriverWait(driver, 1.5).until(
                    EC.presence_of_element_located(item["selector"])
                )
                
                # Se l'elemento è trovato, proviamo a cliccarlo
                print(f"[CLEAN] {item['name']} rilevato. Tento il click...")
                
                # Prova click standard, se fallisce usa tap sulle coordinate dell'elemento
                try:
                    element.click()
                except:
                    location = element.location
                    size = element.size
                    center_x = location['x'] + (size['width'] / 2)
                    center_y = location['y'] + (size['height'] / 2)
                    driver.tap([(center_x, center_y)])
                    print(f"[CLEAN] {item['name']} cliccato tramite coordinate.")

                time.sleep(2) # Tempo vitale per l'animazione di sparizione
                found_in_round = True
                break # Ricomincia il ciclo per vedere se è apparso altro
            except:
                continue
        
        if not found_in_round:
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
    """
    Entra nei dettagli della rete e la rimuove.
    Gestisce il refresh dinamico della lista Wi-Fi (StaleElement).
    """
    wait = WebDriverWait(driver, 15)
    
    print(f"\n[CLEANUP] Apertura impostazioni Wi-Fi per dimenticare: {ssid}")
    
    # 1. Apertura impostazioni tramite Intent
    driver.execute_script('mobile: startActivity', {
        'action': 'android.settings.WIFI_SETTINGS'
    })
    
    # Piccolo respiro per far stabilizzare la scansione delle reti
    time.sleep(2)

    try:
        # 2. Click sulla rete con logica di RETRY per Stale Element
        print(f"[CLEANUP] Cerco la rete '{ssid}' nella lista...")
        
        found_and_clicked = False
        for attempt in range(3):
            try:
                # Cerchiamo l'elemento (fresco di DOM) ad ogni tentativo
                network_row = wait.until(EC.presence_of_element_located(
                    (AppiumBy.XPATH, f"//*[@text='{ssid}']")
                ))
                network_row.click()
                print(f"[CLEANUP] Ingresso nei dettagli di {ssid} effettuato.")
                found_and_clicked = True
                break
            except StaleElementReferenceException:
                print(f"[DEBUG] Lista Wi-Fi aggiornata durante il click (Attempt {attempt + 1}). Riprovo...")
                time.sleep(1)
            except Exception as e:
                print(f"[DEBUG] Errore durante il click sulla rete: {e}")
                time.sleep(1)
        
        if not found_and_clicked:
            raise Exception(f"Impossibile selezionare la rete {ssid} (Elemento sempre Stale o non trovato).")

        # 3. Click su "Rimuovi questa rete" (Tasto Rosso nel menu dettagli)
        print("[CLEANUP] Cerco il tasto 'Rimuovi questa rete'...")
        
        # Usiamo l'Xpath testuale che è il più sicuro su ColorOS
        forget_xpath = "//*[@text='Rimuovi questa rete']"
        
        forget_btn = wait.until(EC.element_to_be_clickable((AppiumBy.XPATH, forget_xpath)))
        forget_btn.click()

        # 4. Gestione del Pop-up di conferma finale
        print("[CLEANUP] Gestione pop-up di conferma...")
        try:
            # Cerchiamo il tasto "Rimuovi" nel dialogo di sistema
            confirm_xpath = "//android.widget.Button[@text='Rimuovi' or @text='RIMUOVI']"
            
            confirm_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, confirm_xpath))
            )
            confirm_btn.click()
            print("[CLEANUP] Conferma rimozione completata.")
        except:
            print("[DEBUG] Nessun pop-up di conferma rilevato (forse rimossa direttamente).")

        print(f"[SUCCESS] Rete {ssid} rimossa dal dispositivo.")
        time.sleep(2)

    except Exception as e:
        print(f"[ERROR] Fallimento durante la rimozione della rete: {e}")
        # Salvataggio sorgente XML in caso di errore per debug
        with open("debug_cleanup_fail.xml", "w") as f:
            f.write(driver.page_source)
        raise