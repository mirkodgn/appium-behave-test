from behave import given, when, then

@given('l\'app viene installata e avviata sul device')
def step_impl(context):
    # Se arriviamo qui senza errori, significa che Appium 
    # ha già installato e aperto l'app correttamente.
    assert context.driver is not None
    print("App installata e lanciata con successo!")