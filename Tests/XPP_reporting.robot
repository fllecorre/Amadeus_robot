*** Settings ***
Resource        ../Resources/Components/Models/REST_API_Model.robot
Resource        ../Resources/Components/Models/QA_Proxy_Model.robot
Resource        ../Resources/Components/Models/XPP_Report_Model.robot
Variables        ../Resources/Components/Models/snapshot_data.py

*** Variables ***
${PHASE}    DEV
${USER}    ${FLECORRE}
${provider}    Apiso 

*** Test Cases ***
#Card Creation
01_Card_Creation
    ${vcn_id}    REST_Create_Card   ${APPUI1A01}    POST_new_VCN_full.json
    ${card_info}    REST_Get_Card_Info   ${APPUI1A01}     ${vcn_id}    
    Log    ${card_info}  

#Get & Check BLOB (to rework)
02_GetCardBLOB
    ${vcn_id}    REST_Create_Card   ${APPUI1A01}    POST_new_VCN_full.json
    ${BLOB}    Get VCN_BOM    ${USER}    ${PHASE}    ${vcn_id}
    ${first_dict}    Create Dictionary    Amount=689.01    Currency=EUR    
    ${expected_BLOB}    Create Dictionary    AvailableBalance=${first_dict}
    Check VCN BLOB    ${BLOB}    ${expected_BLOB}

#Create Report

#Move report to Inbox

#File Clean up

#AppEvent Generation (CAPLAQ)

#XPP Reporting => Create & POST Snapshot
03_XPP_Reporting_Create_Post_Snapshot
    @{list}    Create List    aa     bb     cc     dd     ee     ff     gg     
    ${snapshot}    Create Snapshot    ${list}
    POST Snapshot    ${USER}    ${PHASE}    ${snapshot} 

#XPP Reporting =>  Configuration

#XPP Reporting =>  Report File

#Clean up