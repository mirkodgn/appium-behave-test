Feature: Initial Device Configuration

  Scenario: Connect the device to the dedicated Wi-Fi network
    Given the Appium automation session is active
    When I configure the Wi-Fi connection using environment credentials
    Then the device should be connected to the internet