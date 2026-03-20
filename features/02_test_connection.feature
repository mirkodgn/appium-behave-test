Feature: Test connection and network performance
  Scenario: Network performance with Speedtest
  Given Speedtest application launched successfully
  When user taps on button "VAI"
  Then the values of "Download" and "Upload" should be extracted and saved