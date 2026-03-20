Feature: Connectivity Check via YouTube
  Scenario: Verify internet connection by playing the first available video
    Given the YouTube application is launched correctly
    When the user selects the first non-sponsored video from the home feed
    #Then the video should start playing and the playback time should increase