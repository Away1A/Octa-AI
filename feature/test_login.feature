Feature: GIK Attendance
  Scenario: User open my Attendance page
    Given the user is on the giktalent homepage
    When the user navigates to the login page
    And the user fills the username field with value hendiana with a delay of 1.0 seconds for each element
    And the user fills the password field with value Garuda12345 with a delay of 1.0 seconds for each element
    And the user clicks on login under the username and password field
    Then the login is successful and the user is redirected to the main page
