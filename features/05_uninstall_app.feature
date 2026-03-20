Feature: Application Cleanup

  Scenario: Uninstall Sky Go application to clean the device
    Given the Appium automation session is active
    And the Sky Go application is installed on the device
    When I uninstall the Sky Go application
    Then the Sky Go application should no longer be present