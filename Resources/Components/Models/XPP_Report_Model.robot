*** Settings ***
Library     String
Library    Collections
Library    JSONLibrary
Library    ../../../Resources/libs/lss_token_generator.py 
Resource    REST_API_Model.robot
Variables   ../../../Resources/libs/test_users.py
Variables   ../../../Resources/Components/XPP_data/reporting_data.py

*** Keywords ***

### PREPARATION ###
Set Projection Fields
    [Arguments]    ${json}    ${jsonpath}    @{fields_list}
    ${my_list}    Create List
    FOR    ${element}    IN    @{fields_list}
        ${dict}    Create Dictionary     fieldId=${element}   
        Append To List    ${my_list}    ${dict}       
        Log List    ${my_list} 
    END
    Log List    ${my_list}
    ${changed_json}    Update Value To Json   ${json}    ${jsonpath}    ${my_list}
    RETURN    ${changed_json} 
    

Set Sort
    [Arguments]    ${json}    ${jsonpath}     ${sort_list}
    ${changed_json}    Update Value To Json   ${json}    ${jsonpath}    ${sort_list}
    Log    ${changed_json}
    RETURN    ${changed_json} 

Set Time Range
    [Arguments]    ${json}    ${startFrom_dict}    ${spanTo_dict}
    ${changed_json}    Update Value To Json   ${json}    $.data.timeRange.startFrom   ${startFrom_dict}
    ${changed_json}    Update Value To Json   ${changed_json}    $.data.timeRange.spanTo   ${spanTo_dict}
    RETURN    ${changed_json} 

Set Filters
    [Arguments]    ${json}    ${jsonpath}    ${filters_list}    ${boolean_op}=${EMPTY}
    IF    '${boolean_op}' != '${EMPTY}'
        ${op_dict}    Create Dictionary    ${boolean_op}=${filters_list}
        ${json}    Update Value To Json    ${json}    ${jsonpath}    ${op_dict}
        ${jsonpath}    Set Variable     ${jsonpath}.${boolean_op}  
    END
    ${changed_json}    Update Value To Json   ${json}    ${jsonpath}    ${filters_list}
    Log List    ${filters_list}
    Log    ${changed_json}
    RETURN    ${changed_json}  

Set Report Name    
    [Arguments]    ${json}    ${name}
    ${changed_json}    Update Value To Json   ${json}    $.data.name   ${name}
    Log    ${changed_json}
    RETURN    ${changed_json} 

Set Report Type    
    [Arguments]    ${json}    ${report_type}
    ${changed_json}    Update Value To Json   ${json}    $.data.schema.reportType   ${report_type}
    Log    ${changed_json}
    RETURN    ${changed_json} 

Set Delivery Option
    [Arguments]    ${json}    ${delivery_option_dict}
    ${changed_json}    Update Value To Json   ${json}    $.data.delivery   ${delivery_option_dict}
    Log    ${changed_json}
    RETURN    ${changed_json} 

Create Snapshot
    [Arguments]    ${extra_args}
    Log List    ${extra_args}
    #Load JSON projection template
    ${json}    Load JSON From File    ${EXECDIR}/${snapshot_template_path}
    #Add projection fields
    ${changed_json}    Set Projection Fields     ${json}        $.data.configuration.schema.projection     @{snapshot_fields} 
    #Add sort value to projection
    @{snapshot_sort_list}    Create List     ${snapshot_sort}
    ${changed_json}    Set Sort    ${changed_json}    $.data.configuration.schema.sort     ${snapshot_sort_list}
    #Add timerange value to projection
    ${changed_json}    Set Time Range    ${changed_json}    ${startFrom_dict}   ${spanTo_dict}
    #Add filter values to projection
    Set To Dictionary    ${snapshot_filters_dict2}    args=${extra_args}
    @{filters_list}    Create List     ${snapshot_filters_dict1}     ${snapshot_filters_dict2}  
    ${changed_json}    Set Filters    ${changed_json}     $.data.configuration.filter     ${filters_list}    and 
    #Convert JSON dict to String
    ${changed_json_str}    Convert JSON To String    ${changed_json}
    Log    ${changed_json_str}
    RETURN    ${changed_json_str}


Create Configuration
    [Arguments]    ${extra_args}
    #Load JSON configuration template
    ${json}    Load JSON From File    ${EXECDIR}/${configuration_template_path}
    #Add configuration fields
    ${changed_json}    Set Projection Fields     ${json}    $.data.schema.projection     @{snapshot_fields} 
    #Add report name & report type to configuration
    ${changed_json}    Set Report Name    ${changed_json}    QAtestReport  
    ${changed_json}    Set Report Type    ${changed_json}    transactional
    #Add delivery option
    ${changed_json}    Set Delivery Option    ${changed_json}    ${configuration_delivery}  
    #Add timerange value 
    ${changed_json}    Set Time Range    ${changed_json}    ${startFrom_dict}   ${spanTo_dict}
    #Add filter values to projection
    #Add filters
    Set To Dictionary    ${snapshot_filters_dict2}    args=${extra_args}
    @{filters_list}    Create List     ${snapshot_filters_dict1}     ${snapshot_filters_dict2}  
    ${changed_json}    Set Filters    ${changed_json}     $.data.filter    ${filters_list}    and
    #Convert JSON dict to String
    ${changed_json_str}    Convert JSON To String    ${changed_json}
    Log    ${changed_json_str}
    RETURN    ${changed_json_str}

Create Report URI
    [Arguments]    ${configuration_response}
    ${href}    REST_Get_Value_From_Response_byJsonPath   $.data.self.href
    ${post_report_str}    Set Variable    {"data": {"href": "${href}" }}
    ${post_report_json}    Convert String To JSON    ${post_report_str} 
    RETURN    ${post_report_json} 

### XPP API ###
POST Snapshot
    [Arguments]    ${USER}    ${PHASE}    ${snapshot_json_str}   
    ${phase_letter}    Get Phase Letter    ${PHASE}
    ${json_response}    REST_Request    POST    ${USER}    LSS_Bearer    ${baseURL}/${SAP}${phase_letter}/reporting/snapshot${query_parameters}    ${snapshot_json_str}
    REST_Check_Status_From_Response    200
    Log    ${json_response}

POST Configuration
    [Arguments]    ${USER}    ${PHASE}    ${configuration_json_str}   
    ${phase_letter}    Get Phase Letter    ${PHASE}
    ${json_response}    REST_Request    POST    ${USER}    LSS_Bearer    ${baseURL}/${SAP}${phase_letter}/reporting/configurations${query_parameters}    ${configuration_json_str}
    REST_Check_Status_From_Response    201
    Log    ${json_response}
    RETURN    ${json_response}


POST Report
    [Arguments]    ${USER}    ${PHASE}    ${configuration_uri_json}   
    ${phase_letter}    Get Phase Letter    ${PHASE}
    ${json_response}    REST_Request    POST    ${USER}    LSS_Bearer    ${baseURL}/${SAP}${phase_letter}/reporting/reports${query_parameters}    ${configuration_uri_json}
    REST_Check_Status_From_Response    202
    Log    ${json_response}
    RETURN    ${json_response}

Get Report
    [Arguments]    ${USER}    ${PHASE}    ${uri}   
    ${phase_letter}    Get Phase Letter    ${PHASE}
    ${status}    Set Variable    ${EMPTY}     
    WHILE  '${status}' != 'generated'    limit=5
        ${json_response}    REST_Request    GET    ${USER}    LSS_Bearer    ${baseURL}/${uri}    
        REST_Check_Status_From_Response    200
        ${status}    REST_Get_Value_From_Response_byJsonPath   $.data.status
        Log    ${status} 
    END
    Log    ${json_response}
    RETURN    ${json_response}

Delete Configuration
    [Arguments]    ${USER}    ${PHASE}    ${uri}   
    ${phase_letter}    Get Phase Letter    ${PHASE}
    ${json_response}    REST_Request    DELETE    ${USER}    LSS_Bearer    ${baseURL}/${uri}
    REST_Check_Status_From_Response    204
    Log    ${json_response}
    RETURN    ${json_response}

### HELPERS ###
Get Phase Letter
    [Arguments]    ${phase}
    ${phase_letter}    Set Variable    ${phase}[0]
    ${phase_letter}    Convert To Upper Case    ${phase_letter} 
    RETURN    ${phase_letter}
    
Get URI
    [Arguments]    ${configuration_uri}
    ${phase_letter}    Get Phase Letter    ${PHASE}
    ${href}    REST_Get_Value_From_Response_byJsonPath   $.data.self.href
    ${URI}    Get Regexp Matches    ${href}   1A[A-Z]{9}${phase_letter}.*
    RETURN    ${URI}[0]

