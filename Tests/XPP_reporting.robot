*** Settings ***
Resource        ../Resources/Components/Models/REST_API_Model.robot
Resource        ../Resources/Components/Models/QA_Proxy_Model.robot
Resource        ../Resources/Components/Models/XPP_Report_Model.robot


*** Variables ***
${PHASE}    DEV
${USER}    ${APPUI1A01}
${provider}    Apiso 

*** Test Cases ***
#Card Creation
01_Card_Creation
    ${vcn_id}    REST_Create_Card   ${APPUI1A01}    POST_new_VCN_full.json
    ${card_info}    REST_Get_Card_Info   ${APPUI1A01}     ${vcn_id}    
    Log    ${card_info}  
    ${vcn_trid}    REST_Get_Value_From_Response_byJsonPath    $.history.[0].id    ${card_info}
    Log To Console    ${vcn_trid}

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

04_XPP_Reporting
    @{list}    Create List    aa     bb     cc     dd     ee     ff     gg  
    ${snapshot}    Create Snapshot    ${list}
    POST Snapshot    ${USER}    ${PHASE}    ${snapshot}    
    ${configuration}    Create Configuration    ${list}
    ${configuration_response}    POST Configuration    ${USER}    ${PHASE}    ${configuration} 
    ${configuration_uri_json}    Create Report URI    ${configuration_response}
    ${report_reponse}    POST Report     ${USER}    ${PHASE}    ${configuration_uri_json} 
    ${URI}    Get URI    ${report_reponse}
    Log To Console    ${URI}
    ${report}    Get Report    ${USER}    ${PHASE}    ${URI} 
    Check Report Generation Status     ${report}

#Clean up