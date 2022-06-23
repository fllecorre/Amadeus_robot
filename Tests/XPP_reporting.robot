*** Settings ***
Documentation    /
Resource        ../Resources/Components/Models/REST_API_Model.robot
Resource        ../Resources/Components/Models/QA_Proxy_Model.robot
Resource        ../Resources/Components/Models/XPP_Report_Model.robot

*** Variables ***
${PHASE}    DEV
${USER}    ${FLECORRE}
${provider}    Apiso 

*** Test Cases ***
01_Card_Creation
    ${vcn_id}    REST_Create_Card   ${APPUI1A01}    POST_new_VCN_full.json
    ${card_info}    REST_Get_Card_Info   ${APPUI1A01}     ${vcn_id}    
    Log    ${card_info}  

02_GetCardBLOB
    ${vcn_id}    REST_Create_Card   ${APPUI1A01}    POST_new_VCN_full.json
    ${BLOB}    Get VCN_BOM    ${USER}    ${PHASE}    ${vcn_id}
    ${first_dict}    Create Dictionary    Amount=689.01    Currency=EUR    
    ${expected_BLOB}    Create Dictionary    AvailableBalance=${first_dict}
    Check VCN BLOB    ${BLOB}    ${expected_BLOB}

03_E2E_Case
    ${vcn_id}    REST_Create_Card   ${APPUI1A01}    POST_new_VCN_full.json
    #Create Report + expected BOM
    #Move report to Inbox
    Check File Location    ${USER}    ${PHASE}     Inbox    Filename
    Check File Location    ${USER}    ${PHASE}     Inbox    Filename.STATUS_OK
    ${BLOB}    Get VCN BOM    ${USER}    ${PHASE}    ${vcn_id}
    Check VCN BLOB    ${BLOB}    ${BLOB_expected}
    #File Clean up
    #AppEvent Generation (CAPLAQ)
    #XPP Reporting (Snapshot, Configuration, Report File)
    #Clean up

04_XPP_Reporting_Create_Snapshot
    #Load JSON projection
    ${json}    Load JSON From File    ${EXECDIR}/Resources/Components/Models/report_projection.json
    #Add sort value to projection
    ${changed_json}    Set Sort    ${json}     Timestamp    ascending
    #Add timerange value to projection
    ${startFrom_dict}    Create Dictionary    time=now    roundTo=d
    ${spanTo_dict}    Create Dictionary    time=now  
    ${changed_json}    Set Time Range    ${changed_json}    ${startFrom_dict}   ${spanTo_dict}
    #Add filter values to projection
    @{args_list}    Create List    Payment/B2BWallet/VirtualCard    
    ${dict}    Create Dictionary    fieldId=Type     operator=in    args=@{args_list} 
    ${filters_list}    Create List    ${dict}
    ${changed_json}    Set Filters    ${changed_json}     ${filters_list}
    Log     ${changed_json}


05_XPP_Reporting_POST_Snapshot
    POST_Snapshot