Url : http://172.22.201.22:3002/login, http://172.22.201.22:3002/transaction/create
Feature: Transaction complete

  Scenario: User login and create transaction
    Given I am on the login page
    When I enters username "reza_reza" and password "Pass2323@"
    And I clicks the Log In button
    Then the system displays the "Create Transaction" page

    When I am on the "Create Transaction" page
    And I click "Active Directory" on radio button with column label "Email CC"
    And I click "Active Directory" on radio button with column label "Requestor Source"
    And I click the "Role" dropdown field [1]
    And I enter "Foreman" in the Role field
    
    When I click the "Module Name" dropdown field [2]
    And I enter "Plan Mine Closure" in the Module Name field
  
    When I click the "Requestor" dropdown field [5]
    And I enter value "Atthoriq" in the Requestor field
    And I enter on keyboard
    Then the "Requestor" dropdown field is filled with "Atthoriq"
    
    And I enter "2000" in the "Amount of Transaction" field

    And I click the "Submit" button
    Then the system saves the transaction