*** Settings ***
Library     ../../../Resources/libs/b2bwallet_rest_api_operations.py


*** Keywords ***

Check Get Card List Status
    [Documentation]    Check status of get card list
    [Arguments]    ${phase}    ${user}    ${params}
    ${response}    Get Card List    ${phase}    ${user}    ${params}
    Should Be Equal    ${response}    200
