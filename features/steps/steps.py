from behave import given, when, then
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.common.appiumby import AppiumBy

@given('the device is ready for a new installation')
def step_impl(context):
    # Verifichiamo che il driver sia stato inizializzato
    if context.driver is None:
        raise Exception("Errore: Il driver Appium non è stato inizializzato nel before_scenario.")
    
    # Facciamo una chiamata veloce al server per vedere se il device risponde
    # 'current_package' ci dice qual è l'app aperta in questo momento
    try:
        package = context.driver.current_package
        print(f"[DEBUG] Device connesso. App attuale: {package}")
    except Exception as e:
        raise Exception(f"Il dispositivo non risponde ai comandi Appium: {e}")
    
@then('the application is launched for the first time')
def step_impl(context):
    # Diamo all'app fino a 15 secondi per caricarsi e mostrare il primo elemento
    # Sostituiremo 'ID_DELLA_PRIMA_SCHERMATA' con quello vero trovato con l'Inspector
    wait = WebDriverWait(context.driver, 15)
    
    print("In attesa del caricamento dell'interfaccia utente...")
    
    # Questo comando aspetta che l'app sia 'stabile' e visibile
    try:
        # ESEMPIO: Aspetta che l'elemento con un certo ID sia presente
        # Sostituisci "ID_REALE_TROVATO" con quello che vedi in Appium Inspector
        cookie = wait.until(
            EC.presence_of_element_located((AppiumBy.XPATH, '//android.widget.ScrollView[@resource-id="PrivacyOptionsSummaryColumn"]'))
        )
        print("L'applicazione è pronta e la schermata Privacy è visibile.")
    except Exception:
        print("L'app ci sta mettendo troppo a caricare o è crashata all'avvio.")
        raise

#---

@given('l\'applicazione Speedtest è stata avviata correttamente')
def step_impl(context):
    # ID recuperato dal tuo comando ADB
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
        # Di solito Ookla usa un'Accessibility ID o un testo specifico.
        # Proviamo a cercarlo per ID o Testo (VAI / GO)
        print("[DEBUG] Ricerca del pulsante VAI...")
        
        # Tipico ID del tasto VAI in Speedtest (può variare, ma spesso è questo):
    #     go_button_selector = (AppiumBy.ID, "org.zwanoo.android.speedtest:id/go_button")
        
    #     # Se l'ID fallisce, usiamo una strategia di riserva col testo
    #     try:
    #         context.go_button = wait.until(EC.element_to_be_clickable(go_button_selector))
    #     except:
    #         print("[DEBUG] ID non trovato, provo con il testo 'VAI'...")
    #         context.go_button = wait.until(
    #             EC.element_to_be_clickable((AppiumBy.XPATH, "//*[contains(@text, 'VAI') or contains(@text, 'GO')]"))
    #         )
        
    #     print("[SUCCESS] Speedtest pronto. Pulsante VAI individuato.")
        
    except Exception as e:
        print(f"[ERRORE] Impossibile avviare Speedtest: {e}")
        # Salviamo uno screenshot per vedere cosa è apparso (magari un pop-up?)
        #context.driver.save_screenshot("speedtest_launch_error.png")
        raise
    
