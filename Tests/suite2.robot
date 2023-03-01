*** Settings ***
Resource    ../resources/Components/Models/B2bWalletUI_PlaywrightModel_Technical.robot
Variables    ../Resources/libs/test_users.py

*** Variables ***
${phase}    DEV 

*** Test Cases ***
TC3 REST Create A Card
    [Tags]    regression    smoke_test
    ${VCN_ID_list}    REST_Create_Card   ${APPUI1A01}   1    POST_new_VCN_full.json

TC4 REST Create And Delete A Card
    [Tags]    regression    
    ${VCN_ID_list}    REST_Create_Card   ${APPUI1A01}   1    POST_new_VCN_full.json
    REST_Delete_Card    ${APPUI1A01}    ${VCN_ID_list}[0]