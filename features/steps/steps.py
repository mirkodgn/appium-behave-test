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
    
