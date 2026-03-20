Feature: Install and launch the application
  Scenario: Verify that the application can be installed and launched for the first time
    Given the device is ready for a new installation
    When I launch the Sky Go app for the first time
    Then the first page of the app is displayed correctly