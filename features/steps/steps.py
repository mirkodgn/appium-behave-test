from behave import given, when, then
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.common.appiumby import AppiumBy
import time
import re
import os
from utils.utils import *

@given('the device is ready for a new installation')
def step_impl(context):
    current_dir = os.path.dirname(os.path.abspath(__file__)) # features/steps
    project_root = os.path.abspath(os.path.join(current_dir, "..", "..")) # root del progetto
    
    # Costruiamo il path dell'APK
    apk_path = os.path.join(project_root, "app", os.getenv("APP_NAME"))
    
    print(f"\n[INFO] Path calcolato: {apk_path}")

    if not os.path.exists(apk_path):
        raise Exception(f"L'APK non esiste al percorso: {apk_path}. Controlla la posizione della cartella 'app'!")

    try:
        print(f"[INFO] Installazione dell'APK...")
        context.driver.install_app(apk_path)
        print("[SUCCESS] App installata correttamente.")
    except Exception as e:
        raise Exception(f"Errore critico durante l'installazione: {e}")

@when('I launch the Sky Go app for the first time')
def step_impl(context):
    app_id = "it.sky.anywhere"
    # Activity iniziale standard (StartupActivity è solitamente quella che gestisce il primo avvio)
    app_activity = "com.bskyb.skygo.features.startup.StartupActivity"
    
    print(f"[INFO] Lancio dell'app {app_id}...")

    try:
        # Lanciamo l'attività di startup
        context.driver.execute_script('mobile: startActivity', {
            'component': f"{app_id}/{app_activity}"
        })
        
        wait = WebDriverWait(context.driver, 20)
        wait.until(lambda d: d.current_package == app_id)
        print(f"[SUCCESS] Sky Go è attivo.")

    except Exception as e:
        print(f"[WARNING] StartActivity fallito, provo activate_app genertico: {e}")
        context.driver.activate_app(app_id)
    
@then('the first page of the app is displayed correctly')
def step_impl(context):
    wait = WebDriverWait(context.driver, 15)
    
    print("In attesa del caricamento dell'interfaccia utente...")
    
    # Questo comando aspetta che l'app sia 'stabile' e visibile
    try:
        cookie = wait.until(
            EC.presence_of_element_located((AppiumBy.XPATH, '//android.widget.ScrollView[@resource-id="PrivacyOptionsSummaryColumn"]'))
        )
        print("L'applicazione è pronta e la schermata Privacy è visibile.")
    except Exception:
        print("L'app ci sta mettendo troppo a caricare o è crashata all'avvio.")
        raise

#---SPEEDTEST TEST---

@given('Speedtest application launched successfully')
def step_impl(context):
    speedtest_package = "org.zwanoo.android.speedtest"
    
    print(f"\n[INFO] Passaggio all'app Speedtest: {speedtest_package}")
    
    try:
        # Verifichiamo se l'app è installata prima di provare ad aprirla
        if not context.driver.is_app_installed(speedtest_package):
            raise Exception(f"L'app {speedtest_package} non è installata sul dispositivo!")

        # Attiviamo l'app (la porta in primo piano)
        context.driver.activate_app(speedtest_package)
        
        # Speedtest a volte è lento a caricare la UI dopo lo splash screen
        wait = WebDriverWait(context.driver, 25)
        
        # Cerchiamo il pulsante "VAI". 
        # Proviamo a cercarlo per ID o Testo (VAI / GO)
        print("[DEBUG] Ricerca del pulsante VAI...")
        
    except Exception as e:
        print(f"[ERRORE] Impossibile avviare Speedtest: {e}")
        raise

@when('user taps on button "VAI"')
def step_impl(context):
    print("\n[INFO] Tentativo di avvio dello Speedtest...")
    
    # Definiamo i selettori che abbiamo trovato
    accessibility_id = "Start a Speedtest"
    resource_id = "org.zwanoo.android.speedtest:id/go_button"
    
    try:
        # Se lo abbiamo già trovato nel GIVEN (usando context.go_button), lo usiamo direttamente
        if hasattr(context, 'go_button') and context.go_button:
            button = context.go_button
        else:
            # Altrimenti lo cerchiamo ora (fallback)
            wait = WebDriverWait(context.driver, 15)
            button = wait.until(
                EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, accessibility_id))
            )
        
        # Esecuzione del click
        button.click()
        print("[SUCCESS] Pulsante 'VAI' cliccato con successo.")
        
    except Exception as e:
        print(f"[ERRORE] Impossibile cliccare sul pulsante VAI: {e}")
        # Se fallisce per Accessibility ID, proviamo un ultimo tentativo disperato con l'ID
        try:
            print("[DEBUG] Tento il click tramite Resource ID...")
            context.driver.find_element(AppiumBy.ID, resource_id).click()
        except:
            print("[ERRORE] Anche il tentativo con Resource ID è fallito.")
            raise

@then('the values of "Download" and "Upload" should be extracted and saved')
def step_impl(context):
    wait = WebDriverWait(context.driver, 45, poll_frequency=0.5)
    print("\n[INFO] Monitoraggio dinamico dei risultati...")

    try:
        # 1. Definiamo una funzione interna per il controllo dinamico
        def results_are_ready(driver):
            try:
                # Cerchiamo i contenitori
                d_cont = driver.find_element(AppiumBy.ID, "org.zwanoo.android.speedtest:id/download_result_view")
                u_cont = driver.find_element(AppiumBy.ID, "org.zwanoo.android.speedtest:id/upload_result_view")
                
                # Estraiamo i testi
                d_val = d_cont.find_element(AppiumBy.ID, "org.zwanoo.android.speedtest:id/txt_test_result_value").text
                u_val = u_cont.find_element(AppiumBy.ID, "org.zwanoo.android.speedtest:id/txt_test_result_value").text

                # CONDIZIONE DI USCITA: 
                # I valori devono essere numerici e diversi da "0", "-" o vuoti
                # Usiamo una regex semplice per verificare che ci sia almeno un numero
                if re.match(r"^[1-9]\d*", d_val) and re.match(r"^[1-9]\d*", u_val):
                    return d_val, u_val
                return False
            except:
                return False

        # 2. Avviamo il loop di attesa intelligente
        # wait.until restituirà la tupla (download, upload) non appena la funzione sopra ritorna True
        download_value, upload_value = wait.until(results_are_ready)

        # 3. Scrittura immediata (senza sleep aggiuntivi!)
        with open("report_speedtest.txt", "a") as f:
            f.write(f"Test del {time.ctime()}: Download {download_value}, Upload {upload_value}\n")

        print("-" * 30)
        print(f"✅ RISULTATI ESTRATTI IN TEMPO REALE")
        print(f"DOWNLOAD: {download_value} Mbps")
        print(f"UPLOAD:   {upload_value} Mbps")
        print("-" * 30)

    except Exception as e:
        print(f"[ERRORE] Test di rete troppo lento o UI non riconosciuta: {e}")
        raise

#---YOUTUBE TEST---

@given('the YouTube application is launched correctly')
def step_impl(context):
    app_id = "com.google.android.youtube"
    # Il link profondo alla home di YouTube
    home_deep_link = "https://www.youtube.com"
    
    print(f"\n[INFO] Lancio YouTube tramite Deep Link...")

    try:
        # 1. Chiudiamo Sky Go per evitare sovrapposizioni
        context.driver.terminate_app("it.sky.anywhere")
        
        # 2. Forza l'apertura tramite URL (Deep Linking)
        # Questo comando dice ad Android: "Apri l'app che gestisce questo URL"
        context.driver.get(home_deep_link)
        
        # 3. Verifica del pacchetto
        wait = WebDriverWait(context.driver, 15)
        wait.until(lambda d: d.current_package == app_id)
        
        print("[SUCCESS] YouTube è stato aperto correttamente tramite Deep Link.")
        time.sleep(2) # Pausa per stabilizzare la UI

    except Exception as e:
        print(f"[WARNING] Deep Link fallito, provo il metodo standard...")
        try:
            context.driver.activate_app(app_id)
        except:
            raise Exception("Impossibile aprire YouTube. Controlla se l'app è disabilitata o bloccata.")

    except Exception as e:
        print(f"[ERRORE] Lancio fallito: {e}")
        # Fallback rapido nel caso l'activity fallisca
        context.driver.activate_app(app_id)

@when('the user selects the first video from the home feed')
def step_impl(context):
    wait = WebDriverWait(context.driver, 15)
    print("[INFO] Searching for the first organic video...")

    # Cerchiamo tutti i video nel feed 'results'
    # Utilizziamo un selettore che punta ai titoli dei video o ai contenitori cliccabili
    # Dall'XML, i video hanno content-desc dettagliati
    try:
        # XPATH che esclude i video contenenti la parola 'Sponsorizzato' (Sponsorizzato in italiano)
        video_selector = "//android.view.ViewGroup[contains(@content-desc, 'riproduci video') and not(contains(@content-desc, 'Sponsorizzato'))]"
        
        first_video = wait.until(EC.element_to_be_clickable((AppiumBy.XPATH, video_selector)))
        print(f"[DEBUG] Video found: {first_video.get_attribute('content-desc')[:50]}...")
        first_video.click()
        
    except Exception as e:
        print(f"[ERRORE] Could not find a valid video: {e}")
        raise

@then('the video should start playing and the playback time should increase')
def step_impl(context):
    # Pulizia finale post-click (per chat o ads pre-roll)
    clean_youtube_ui(context.driver)
    
    wait = WebDriverWait(context.driver, 20)
    print("[INFO] Verifica progresso video...")

    try:
        # 1. Tocco per mostrare la SeekBar
        context.driver.tap([(540, 500)])
        
        # 2. Lettura tempo iniziale dalla SeekBar (content-desc)
        seek_bar = wait.until(EC.presence_of_element_located((AppiumBy.XPATH, "//android.widget.SeekBar")))
        t1_desc = seek_bar.get_attribute("content-desc")
        print(f"[DEBUG] Tempo T1: {t1_desc}")
        
        # 3. Attesa riproduzione effettiva
        time.sleep(10)
        
        # 4. Lettura tempo finale
        context.driver.tap([(540, 500)])
        t2_desc = seek_bar.get_attribute("content-desc")
        print(f"[DEBUG] Tempo T2: {t2_desc}")
        
        # 5. Assert: le stringhe descrittive devono differire
        assert t1_desc != t2_desc, f"Il video è fermo! ({t1_desc})"
        
        # Log del risultato pulito
        match = re.search(r"^(.*?)\s+di", t2_desc)
        pos = match.group(1) if match else t2_desc
        print(f"[SUCCESS] Connessione OK! Video in riproduzione a: {pos}")

    except Exception as e:
        print(f"[ERRORE] Playback non confermato: {e}")
        raise