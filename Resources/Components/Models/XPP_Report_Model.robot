*** Settings ***
Library    String
Library    Collections
Library    JSONLibrary
Library    DateTime
Library    ../../../Resources/libs/lss_token_generator.py 
Resource    REST_API_Model.robot
Variables   ../../../Resources/libs/test_users.py
Variables   ../../../Resources/Components/XPP_data/reporting_data.py
Resource     Import_file_Model.robot
Resource    QA_Proxy_Model.robot

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
    Log     ${changed_json}
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
    Log    ${changed_json}
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
    Log    ${post_report_json}
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
    Log    ${phase_letter}
    RETURN    ${phase_letter}
    
Get URI
    [Arguments]    ${configuration_uri}
    ${phase_letter}    Get Phase Letter    ${PHASE}
    ${href}    REST_Get_Value_From_Response_byJsonPath   $.data.self.href
    ${URI}    Get Regexp Matches    ${href}   1A[A-Z]{9}${phase_letter}.*
    Log    ${URI} 
    RETURN    ${URI}[0]

Check Report Resource Content
    [Arguments]    ${report_resource}
    Log     ${report_resource}
    ${method}    REST_Get_Value_From_Response_byJsonPath    $.body.data.self.methods.[0]    ${report_resource} 
    Should Be Equal As Strings     ${method}    GET
    ${trigger}    REST_Get_Value_From_Response_byJsonPath    $.body.data.trigger    ${report_resource} 
    Should Be Equal As Strings     ${trigger}    manual
    ${stats}    REST_Get_Value_From_Response_byJsonPath    $.body.data.stats    ${report_resource} 
    Should Contain Any   ${stats}     duration    total      failed    
    ${status}    REST_Get_Value_From_Response_byJsonPath    $.body.data.status   ${report_resource} 
    Should Be Equal As Strings     ${status}    generated
    ${report_file_location}    REST_Get_Value_From_Response_byJsonPath    $.body.data.reportFileLocation   ${report_resource} 
    Should Not Be Empty    ${report_file_location}
    ${file_name}    REST_Get_Value_From_Response_byJsonPath    $.body.data.fileName   ${report_resource} 
    Should Not Be Empty    ${file_name}
    ${change_log}    REST_Get_Value_From_Response_byJsonPath    $.body.data.configuration.changeLog   ${report_resource} 
    Should Contain Any   ${change_log}     lastUpdateTime    lastUpdateBy        
    ${triggered_at}    REST_Get_Value_From_Response_byJsonPath    $.body.data.triggeredAt   ${report_resource} 
    ${current_date}    Get Current Date    result_format=%Y-%m-%d 
    ${triggered_at}    Convert Date    ${triggered_at}    result_format=%Y-%m-%d 
    Should Be Equal    ${triggered_at}     ${current_date}    
    ${time_range_start_from}    REST_Get_Value_From_Response_byJsonPath    $.body.data.timeRange.startFrom.time   ${report_resource} 
    ${time_range_start_from}    Convert Date    ${time_range_start_from}    result_format=%Y-%m-%d 
    Should Be Equal    ${time_range_start_from}     ${current_date}    
    ${time_range_span_to}    REST_Get_Value_From_Response_byJsonPath    $.body.data.timeRange.spanTo.time   ${report_resource} 
    ${time_range_span_to}    Convert Date    ${time_range_span_to}    result_format=%Y-%m-%d 
    Should Be Equal    ${time_range_span_to}     ${current_date} 

Check Report Content
    [Arguments]    ${report_resource}     ${expected_headers}    ${expected_values_list}
    Log Many    ${report_resource}    ${expected_headers}    ${expected_values_list}
    ${report_file_location}    REST_Get_Value_From_Response_byJsonPath    $.body.data.reportFileLocation   ${report_resource} 
    Log    ${report_file_location} 
    Set SSL Verify    ${False}
    ${response}    GET    ${report_file_location}
    Log    ${response}   
    ${content}    REST_Get_Value_From_Response_byJsonPath    $.body    ${response}
    Log    ${content}
    ${report_lines}    Get Line Count    content
    Should Be True    ${report_lines} >= 2     message=report empty
    Log    ${report_lines} 
    FOR    ${line}    IN RANGE    0    ${report_lines} 
        ${content}    Get Line    ${content}     ${line} 
        IF    ${line} == 0 
            ${expected_headers}    Evaluate    ','.join(map(str, ${expected_headers}))
            Should Be Equal As Strings    ${content}    ${expected_headers}
        ELSE
            ${index}    Evaluate    int(${line}-1)
            ${expected_content}    Evaluate    ','.join(map(str, ${expected_values_list}[${index}]))
            Should Be Equal As Strings    ${content}    ${expected_content}  
        END  
    END

Generate XPP Report
    [Arguments]    ${USER}    ${PHASE}     ${extra_args_list} 
    Log List    ${extra_args_list}    
    ${snapshot}    Create Snapshot    ${extra_args_list}
    POST Snapshot    ${USER}    ${PHASE}    ${snapshot}    
    ${configuration}    Create Configuration    ${extra_args_list}
    ${configuration_response}    POST Configuration    ${USER}    ${PHASE}    ${configuration} 
    ${configuration_uri_json}    Create Report URI    ${configuration_response}
    ${report_reponse}    POST Report     ${USER}    ${PHASE}    ${configuration_uri_json} 
    ${URI}    Get URI    ${report_reponse}

    ${report}    Get Report    ${USER}    ${PHASE}    ${URI} 
    RETURN     ${report}    ${configuration} 
    
Check XPP Report
    [Arguments]    ${report}    ${expected_headers}    ${expected_values}
    Check Report Resource Content    ${report}
    Check Report Content    ${report}     ${expected_headers}    ${expected_values}
    
XPP_Report_Cleaning
    [Arguments]    ${USER}    ${PHASE}    ${configuration}=None
    Clean Import File Storage
    IF     '${configuration}' != 'None'    Run Keyword And Warn On Failure    Delete Configuration    ${USER}    ${PHASE}    ${configuration}

Get Expected Values From Transactions
    [Arguments]    ${transactions_list}    ${snapshot_fields}     ${card_info_dict}   
    Log Dictionary    ${card_info_dict} 
    @{expected_values_list}    Create List
    FOR     ${transaction}    IN     @{transactions_list}   
        @{list}    Create List 
        Log     ${transaction}
        ${transaction_type}    REST_Get_Value_From_Response_byJsonPath    $.Type    ${transaction}
        FOR     ${field}    IN    @{snapshot_fields}
            IF    '${field}' == 'Timestamp'
                ${TIMESTAMP}    REST_Get_Value_From_Response_byJsonPath    $.TransactionDateTime.Processed    ${transaction}
                Append To List    ${list}    ${TIMESTAMP}
            ELSE IF    '${field}' == 'VCNID'
                Append To List    ${list}    ${card_info_dict}[vcn_id]
            ELSE IF    '${field}' == 'ExternalCardReference'
                Append To List    ${list}    ${card_info_dict}[vcn_trid]
            ELSE IF    '${field}' == 'LinkCode'
                Append To List    ${list}    ${provider}
            ELSE IF    '${field}' == 'TransactionType' 
                Append To List    ${list}    ${transaction_type}
            ELSE IF    '${field}' == 'Amount'
                ${Amount}    REST_Get_Value_From_Response_byJsonPath    $.AmountRequested.Amount    ${transaction}
                Append To List    ${list}    ${Amount} 
            ELSE IF    '${field}' == 'Currency'
                ${Currency}    REST_Get_Value_From_Response_byJsonPath    $.AmountRequested.Currency    ${transaction}
                Append To List    ${list}    ${Currency} 
            ELSE IF    '${field}' == 'Status'
                ${status}    REST_Get_Value_From_Response_byJsonPath    $.TransactionStatus.ActionStatus    ${transaction}
                Append To List    ${list}    ${status} 
            END
            Log List    ${list}
        END
        Append To List    ${expected_values_list}    ${list}
        Log    ${expected_values_list}
    END
    Sort Expected Values List    ${expected_values_list}
    RETURN    ${expected_values_list}


Get Transactions From Expected BOM
    [Arguments]    ${expected_BOM}
    ${transactions_list}    REST_Get_Value_From_Response_byJsonPath    $.Transactions   ${expected_BOM}
    Log List    ${transactions_list}
    ${transactions_length}    Get Length    ${transactions_list} 
    ${payment_transactions_list}    REST_Get_Value_From_Response_byJsonPath    $.PaymentTransactions   ${expected_BOM}
    Log List    ${payment_transactions_list}
    ${payment_transactions_length}    Get Length    ${payment_transactions_list} 
    ${all_transactions_list}    Combine Lists    ${transactions_list}    ${payment_transactions_list} 
    Log List    ${all_transactions_list}
    RETURN     ${all_transactions_list} 
     


Sort Expected Values List
    [Arguments]    ${expected_values_list}
    #${reference_list}    Create List    CREATION    AUTHORISATION    SETTLEMENT    CANCELLATION    
    ${sorted_expected_values_list}    Create list    
    FOR    ${list}    IN     @{expected_values_list} 
        Log    ${list}
        IF    'CREATION' in ${list}    Insert Into List    ${sorted_expected_values_list}    0    ${list}  
        IF    'AUTHORISATION' in ${list}    Insert Into List    ${sorted_expected_values_list}    1    ${list} 
        IF    'SETTLEMENT' in ${list}    Insert Into List    ${sorted_expected_values_list}    2    ${list} 
        IF    'CANCELLATION' in ${list}    Insert Into List    ${sorted_expected_values_list}    3    ${list}   
        Log List    ${sorted_expected_values_list}
    END
    Log List    ${sorted_expected_values_list}