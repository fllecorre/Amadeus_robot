*** Settings ***
Library    Collections
Library    JSONLibrary
Library           ../../../Resources/libs/lss_token_generator.py 
Resource    REST_API_Model.robot
Variables       ../../../Resources/libs/test_users.py


*** Variables ***

*** Keywords ***

Set Sort
    [Arguments]    ${json}    ${field}    ${order}
    ${changed_json}    Update Value To Json   ${json}    $.data.configuration.schema.sort.fieldId   ${field}
    ${changed_json}    Update Value To Json   ${changed_json}    $.data.configuration.schema.sort.order   ${order}
    Log    ${changed_json}
    RETURN    ${changed_json} 

Set Time Range
    [Arguments]    ${json}    ${startFrom_dict}    ${spanTo_dict}
    ${changed_json}    Update Value To Json   ${json}    $.data.timeRange.startFrom   ${startFrom_dict}
    ${changed_json}    Update Value To Json   ${changed_json}    $.data.timeRange.spanTo   ${spanTo_dict}
    RETURN    ${changed_json} 

Set Filters
    [Arguments]    ${json}    ${filters_list}
    ${changed_json}    Update Value To Json   ${json}    $.data.configuration.schema.filter   ${filters_list}
    RETURN    ${changed_json}  

  
POST_Snapshot
    [Arguments]    ${USER}    ${PHASE}    ${snapshot_json} 
    
    ${SAP}
    ${suffixe}    Set Variable    D
    ${query_parameters}    Catenate   ?merchant=    APS_OFF_NCE1A095X
    
    ${json_response}    REST_Request    POST    ${USER}    ${SAP}${suffixe}/reporting/snapshot${query_parameters}    ${snapshot_json}
    REST_Check_Status_From_Response    200

    



    