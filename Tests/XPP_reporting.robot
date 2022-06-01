*** Settings ***
Documentation    /
Resource        ../Resources/Components/Models/REST_API_Model.robot
Variables       ../Resources/libs/test_users.py

*** Test Cases ***
01_Card_Creation
    ${vcn_id}    REST_Create_Card   ${APPUI1A01}    POST_new_VCN_full.json
    ${card_info}    REST_Get_Card_Info   ${APPUI1A01}     ${vcn_id}    
    Log    ${card_info}    