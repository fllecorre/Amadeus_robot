*** Settings ***
Library     String
Library    Collections
Library    JSONLibrary
Library    ../../../Resources/libs/lss_token_generator.py 
Resource    REST_API_Model.robot
Variables   ../../../Resources/libs/test_users.py
Variables   ../../../Resources/Components/Models/snapshot_data.py


*** Variables ***
${SAP}    1ASIUAPSGUI
${query_parameters}    ?merchant=APS_OFF_NCE1A095X
${baseURL}   https://paypages.dev.payment.amadeus.com:443 

*** Keywords ***
Set Projection Fields
    [Arguments]    ${json}    @{fields_list}
    ${my_list}    Create List
    FOR    ${element}    IN    @{fields_list}
        ${dict}    Create Dictionary     fieldId=${element}   
        Append To List    ${my_list}    ${dict}       
        Log List    ${my_list} 
    END
    Log List    ${my_list}
    ${changed_json}    Update Value To Json   ${json}    $.data.configuration.schema.projection   ${my_list}
    RETURN    ${changed_json} 
    

Set Sort
    [Arguments]    ${json}    ${sort_list}
    ${changed_json}    Update Value To Json   ${json}    $.data.configuration.schema.sort   ${sort_list}
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
    Log List    ${filters_list}
    RETURN    ${changed_json}  

Create Snapshot
    [Arguments]    ${extra_args}
    Log List    ${extra_args}
    #Load JSON projection template
    ${json}    Load JSON From File    ${EXECDIR}/${snapshot_template_path}
    #Add projection fields
    ${changed_json}    Set Projection Fields     ${json}    @{snapshot_fields} 
    #Add sort value to projection
    @{snapshot_sort_list}    Create List     ${snapshot_sort}
    ${changed_json}    Set Sort    ${changed_json}    ${snapshot_sort_list}
    #Add timerange value to projection
    ${changed_json}    Set Time Range    ${changed_json}    ${startFrom_dict}   ${spanTo_dict}
    #Add filter values to projection
    Set To Dictionary    ${snapshot_filters_dict2}    args=${extra_args}
    @{filters_list}    Create List     ${snapshot_filters_dict1}     ${snapshot_filters_dict2}  
    ${changed_json}    Set Filters    ${changed_json}     ${filters_list}
    #Convert JSON dict to String
    ${changed_json_str}    Convert JSON To String    ${changed_json}
    Log    ${changed_json_str}
    RETURN    ${changed_json_str}

POST Snapshot
    [Arguments]    ${USER}    ${PHASE}    ${snapshot_json_str}   
    ${phase_letter}    Get Phase Letter    ${PHASE}
    ${json_response}    REST_Request    POST    ${USER}    LSS_Bearer    ${baseURL}/${SAP}${phase_letter}/reporting/snapshot${query_parameters}    ${snapshot_json_str}
    REST_Check_Status_From_Response    200
    Log    ${json_response}

Get Phase Letter
    [Arguments]    ${phase}
    ${phase_letter}    Set Variable    ${phase}[0]
    ${phase_letter}    Convert To Upper Case    ${phase_letter} 
    RETURN    ${phase_letter}
    



    