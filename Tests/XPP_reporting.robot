*** Settings ***
Resource        ../Resources/Components/Models/REST_API_Model.robot
Resource        ../Resources/Components/Models/QA_Proxy_Model.robot
Resource        ../Resources/Components/Models/XPP_Report_Model.robot


*** Variables ***
${PHASE}    DEV
${USER}    ${APPUI1A01}
${QA_PROXY_USER}    ${MY_USER}      
${provider}    Apiso 

*** Test Cases ***
#Card Creation
01_Card_Creation
    ${vcn_id}    REST_Create_Card   ${USER}    POST_new_VCN_full.json
    ${card_info}    REST_Get_Card_Info   ${USER}     ${vcn_id}    
    Log    ${card_info}  
    ${vcn_trid}    REST_Get_Value_From_Response_byJsonPath    $.history.[0].id    ${card_info}
    Log To Console    ${vcn_trid}

#Get & Check BOM (to rework)
02_GetCardBOM
    ${vcn_id}    REST_Create_Card   ${USER}    POST_new_VCN_full.json
    ${actual_bom}    Get VCN_BOM    ${QA_PROXY_USER}    ${PHASE}    ${vcn_id}
    ${expected_bom_str}    Set Variable   {"Provider": "IXARIS", "MaxNumberOfAuthors": 1, "StaticCardInformation": {"PAN": "554756XXXXXX1566", "Type": "CREDIT", "Vendor": "CA"}}  
    ${expected_bom_json}    Convert String To JSON    ${expected_bom_str}
    ${result}     VerifyCardBom    ${actual_bom}     ${expected_bom_json}    
    IF    ${result} == 1    Fail    Mismatch detected : see VerifyCardBom keywords log to get more details 

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

#Clean up

 