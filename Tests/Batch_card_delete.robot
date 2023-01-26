*** Settings ***
Resource        ../Resources/Components/Models/Batch_deletion_Model.robot
Library        ../Resources/libs/b2bwallet_rest_api_operations.py
Library    OperatingSystem
Variables        ../Resources/libs/test_users.py


*** Test Cases ***
01_Get_cards_list_ok
    &{params_dict}=    Create Dictionary    state=CA	creationBeginDate=2023-01-01    creationEndDate=2023-12-01
    Check Get Card List Status    UAT    ${APPUI1A01}    ${params_dict}