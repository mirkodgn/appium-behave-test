import os
from dotenv import load_dotenv
from appium import webdriver
from appium.options.android import UiAutomator2Options

load_dotenv()

def before_scenario(context, scenario):
    # Percorso dinamico dell'APK
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    apk_path = os.path.join(project_root, "app", os.getenv("APP_NAME"))

    # Configurazione Options leggendo tutto dal .env
    options = UiAutomator2Options()
    options.platform_name = os.getenv("PLATFORM_NAME")
    options.device_name = os.getenv("DEVICE_NAME")
    options.automation_name = os.getenv("AUTOMATION_NAME")
    options.app = apk_path
    
    # Se vuoi che l'app venga reinstallata pulita ogni volta:
    options.full_reset = True 

    # Avvio sessione
    server_url = os.getenv("APPIUM_SERVER")
    context.driver = webdriver.Remote(server_url, options=options)

# def after_scenario(context, scenario):
#     if hasattr(context, 'driver'):
#         context.driver.quit()