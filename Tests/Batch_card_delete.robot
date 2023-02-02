*** Settings ***
Library    OperatingSystem
Library    DateTime
Library    JSONLibrary
Library    ../Resources/libs/b2bwallet_rest_api_operations.py
Variables    ../Resources/libs/test_users.py
Variables    ../Resources/Components/REST_data/REST_variables.py
Resource    ../Resources/Components/Models/Batch_deletion_Model.robot

*** Variables ***
${virtual_cards_path}    /payment/v1/virtualCards
@{providers}    IXARIS
${state}    CA

*** Test Cases ***
01_Delete_cards_DEV 
    [Documentation]    This script deletes all the active cards of the specified providers 
    ...    in a time range of [today - one_month_ago, today - one_week_ago]
    ${env}=    Given Set Variable   DEV 
    ${report}=    When Delete old cards    ${env}    ${state}    ${providers}
    Then Log To Console    Final result ${report}
    Log To Console    \n

02_Delete_cards_PDT 
    [Documentation]    This script deletes all the active cards of the specified providers 
    ...    in a time range of [today - one_month_ago, today - one_week_ago]
    ${env}=    Given Set Variable   PDT 
    ${report}=    When Delete old cards    ${env}    ${state}    ${providers}
    Then Log To Console    Final result ${report}
    Log To Console    \n

03_Delete_cards_UAT 
    [Documentation]    This script deletes all the active cards of the specified providers 
    ...    in a time range of [today - one_month_ago, today - one_week_ago]
    ${env}=    Given Set Variable   UAT 
    ${report}=    When Delete old cards    ${env}    ${state}    ${providers}
    Then Log To Console    \nFinal result ${report}
    Log To Console    \n