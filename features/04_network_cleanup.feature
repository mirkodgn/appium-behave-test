Feature: Final Device Cleanup

  Scenario: Disconnect and forget the testing Wi-Fi network
    Given the Appium automation session is active
    When I remove the Wi-Fi network used for testing from environment credentials
    Then the device should no longer be connected to that network