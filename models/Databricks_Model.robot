*** Settings *** 
Library    Collections
Library    JSONLibrary
Library    String
Library    REST
Library    OperatingSystem
Library    DateTime
Variables   ../resources/Databricks_API_conf.py
Resource    REST_API_Model.robot

*** Keywords ***
Run Job With Parameter  
    [Documentation]    Run databricks job to retrieve the exchange rates of a specific currency
    ...    Parameters :
    ...    - job_id : id of the job to run
    ...    - currency : input of the job to get the corresponding exchange rates
    ...    Return value :
    ...    - run_id : id of the job run
    [Arguments]    ${job_id}    ${currency}  
    &{headers}    Create Dictionary    Authorization=Bearer ${token}    Accept=application/json
    &{input_currency}    Create Dictionary    inputOriginCurrency=${currency}
    ${body}    Create Dictionary    job_id=${job_id}    notebook_params=${input_currency}
    ${response}    POST   ${databricks_url}/${databricks_api_endpoints}[run_job]    body=${body}    headers=&{headers} 
    Log     ${response}
    ${job_status}    Run Keyword And Return Status    REST_Check_Status_From_Response    200
    ${run_id}    IF    '${job_status}' == '${True}'    Get_Value_From_Response_byJsonPath    $.body.run_id    ${response}    ELSE    Fail    msg=Databricks job failed (job_id = ${job_id})
    Log     ${run_id}
    Log To Console     Job started, run in progress...
    Sleep    60s     Job started, run in progress...
    RETURN     ${run_id} 

Get Run Output
    [Documentation]    Retrieve the output field from databricks job run response (containing the exchange rates as a string)
    ...    Parameters :
    ...    - run_id : id of the job run 
    ...    Return value :
    ...    - run_output : result field of the job run (type = string)
    [Arguments]    ${run_id}
    &{headers}    Create Dictionary    Authorization=Bearer ${token}   Accept=application/json
    &{body}    Create Dictionary    run_id=${run_id} 
    ${run_status}    Set Variable    PENDING
    WHILE    '${run_status}' != 'TERMINATED'    limit=5
        Log To Console     Waiting for the job run to finish
        ${response}    GET   ${databricks_url}/${databricks_api_endpoints}[get_output]   query=&{body}    headers=&{headers}  
        Log     ${response}
        ${run_status}    Get_Value_From_Response_byJsonPath    $.body.metadata.state.life_cycle_state    ${response}
        Sleep    30s     Waiting for the job run to finish
    END
    ${result_state}    Get_Value_From_Response_byJsonPath    $.body.metadata.state.result_state     ${response} 
    IF    '${result_state}' != 'SUCCESS'    Fail    The job run failed. Please go to Databricks.
    ${run_output}    Get_Value_From_Response_byJsonPath    $.body.notebook_output.result    ${response}
    RETURN     ${run_output}

Format Run Output
    [Documentation]    Format the databrick run output from a string to a json list
    ...    Parameters :
    ...    - output : result field of the job run (type = string)
    ...    Return value :
    ...    - formatted_output_list : list of dict
    [Arguments]    ${output}
    @{exchange_rates}    Split String    ${output}    ,    1
    @{items} 	Split String	${exchange_rates}[1]    separator=}
    Remove From List    ${items}    -1
    Log List     ${items}    
    @{formatted_output_list}    Create List
    FOR    ${i}    IN    @{items}
        Log    ${i}
        ${i}    Set Variable    ${i}}
        ${i}    Convert String To JSON    ${i}
        Log    ${i}
        Append To List     ${formatted_output_list}    ${i}
    END
    Log List    ${formatted_output_list}
    RETURN    ${formatted_output_list}

Get Exchange Rates
    [Arguments]    ${original_currency}    ${preferred_currencies}=${EMPTY}
    ${date}    Get Current Date    result_format=%Y-%m-%d
    ${status}    Is Daily Exchange Rate Already Available    ${original_currency}    ${date}
    IF    ${status} == ${True}
        &{rate_dict}    Get Exchange Rates From Local    ${date}    ${original_currency}    ${preferred_currencies}     
    ELSE
        &{rate_dict}    Get Exchange Rates From Databricks    ${original_currency}    ${preferred_currencies} 
    END
    RETURN    &{rate_dict} 

Get Exchange Rates From Databricks
    [Documentation]    Get the exchange rates in EUR, USD and in the preferred currencies of a currency. 
    ...    The rates are retrieved by running a dedicated Databricks job and stored in a local file
    ...    Parameters :
    ...    - original_currency : currency to convert
    ...    - preferred_currencies : dict containing merchant and payment requestor preferred currencies
    ...    Return value :
    ...    - rate_dict : dictionary containing the exchange rates in EUR, USD and in the preferred currencies  
    [Arguments]    ${original_currency}    ${preferred_currencies}=${EMPTY}
    ${run_id}    Run Job With Parameter    ${exchange_rates_job_id}    ${original_currency} 
    ${output}    Get Run Output    ${run_id}
    Log    ${output} 
    ${rate_EUR}    Search For A Specific Exchange Rate    ${output}    ${original_currency}    EUR
    ${rate_USD}    Search For A Specific Exchange Rate    ${output}    ${original_currency}    USD 
    &{rate_dict}    Create Dictionary    rate_${original_currency}_EUR=${rate_EUR}    rate_${original_currency}_USD=${rate_USD}
    IF    &{preferred_currencies} != &{EMPTY}
        FOR     ${preferred_currency_type}    ${preferred_currency}    IN    &{preferred_currencies}
            ${rate_preferred_currency}    Search For A Specific Exchange Rate    ${output}    ${original_currency}    ${preferred_currency} 
            Set To Dictionary   ${rate_dict}    rate_${original_currency}_${preferred_currency}=${rate_preferred_currency}
        END
    END
    Log Dictionary      ${rate_dict} 
    ${current_date}    Get Current Date    result_format=%Y-%m-%d
    Append To File    ${EXECDIR}/${data_path}/exchange_rates.txt    ${\n}${current_date} : ${original_currency} : ${output}
    Get Exchange Rate Date    ${output}
    RETURN    &{rate_dict}

Get Exchange Rates From Local
    [Documentation]    Get the exchange rates in EUR, USD and in the preferred currencies of a currency. 
    ...    The rates are retrieved from a local file
    ...    Parameters :
    ...    - original_currency : currency to convert
    ...    - preferred_currencies : dict containing merchant and payment requestor preferred currencies
    ...    Return value :
    ...    - rate_dict : dictionary containing the exchange rates in EUR, USD and in the preferred currencies 
    [Arguments]    ${date}    ${original_currency}    ${preferred_currencies}=${EMPTY}  
    Log Many    ${date}    ${original_currency}       
    ${grep_line}    Grep File    ${EXECDIR}/${data_path}/exchange_rates.txt    ${date} : ${original_currency} :
    ${date}    ${original_currency}    ${rates}    Split String    ${grep_line}    ${SPACE}:${SPACE}    2  
    ${rate_EUR}    Search For A Specific Exchange Rate    ${rates}    ${original_currency}    EUR
    ${rate_USD}    Search For A Specific Exchange Rate    ${rates}    ${original_currency}    USD 
    &{rate_dict}    Create Dictionary    rate_${original_currency}_EUR=${rate_EUR}    rate_${original_currency}_USD=${rate_USD}
    IF    &{preferred_currencies} != &{EMPTY}
        FOR     ${preferred_currency_type}    ${preferred_currency}    IN    &{preferred_currencies}
            ${rate_preferred_currency}    Search For A Specific Exchange Rate    ${rates}    ${original_currency}    ${preferred_currency} 
            Set To Dictionary   ${rate_dict}    rate_${original_currency}_${preferred_currency}=${rate_preferred_currency}
        END
    END
    Log Dictionary      ${rate_dict}
    RETURN    ${rate_dict}   


Is Daily Exchange Rate Already Available
    [Documentation]
    [Arguments]    ${original_currency}    ${date}
    ${grep_line}    Grep File    ${EXECDIR}/${data_path}/exchange_rates.txt    ${date} : ${original_currency} :
    IF    '${grep_line}' == '${EMPTY}'    RETURN      ${False}    ELSE     RETURN    ${True}
    
Search For A Specific Exchange Rate
    [Documentation]    Get the exchange rate of a currency
    ...    Parameters :
    ...    - exchange_rates_output : raw result from the databrick job run
    ...    - original_currency : currency to convert
    ...    - selling_currency : output currency
    ...    Return value :
    ...    - exchange_rate : exchange rate of the original currency in the selling currency
    [Arguments]    ${exchange_rates_output}    ${original_currency}    ${selling_currency}   
    Log Many     ${original_currency}    ${selling_currency}
    IF    '${selling_currency}' != '${None}'
        ${selling_currency}    Convert To Upper Case    ${selling_currency}      
    END
    IF     '${original_currency}' == '${selling_currency}'
        ${exchange_rate}    Set Variable    1.00 
        RETURN    ${exchange_rate}
    END
    ${exchange_rates_list}    Format Run Output    ${exchange_rates_output}
    FOR    ${dict}     IN     @{exchange_rates_list} 
        IF    '${dict}[SellingCurrency]' == '${selling_currency}' 
            ${exchange_rate}    Get From Dictionary    ${dict}    OriginalRate 
            ${number_of_implied_decimals}    Get From Dictionary    ${dict}    NumberOfImpliedDecimals
            ${exchange_rate}    Evaluate    int(${exchange_rate})/pow(10,int(${number_of_implied_decimals}))
            RETURN    ${exchange_rate} 
        ELSE
            CONTINUE
        END       
    END
    ${exchange_rate}    Set Variable    NULL   
    RETURN    ${exchange_rate}

Get_Value_From_Response_byJsonPath
    [Documentation]     Retrieve a value from the json response body
    ...    Parameters :
    ...    - json_path : jsonPath to get value from (example $.data.card.cardNumber)
    ...    - response_body : response body
    [Arguments]    ${json_path}=None    ${response_body}=None
    Log Many    ${JsonPath}    ${response_body}    
    ${value}    Get Value From Json    ${response_body}     ${json_path}
    Log    ${value}[0]
    RETURN    ${value}[0]

Get Exchange Rate Date
    [Documentation]     Retrieve a value from the json response body
    ...    Parameters :
    ...    - json_path : jsonPath to get value from (example $.data.card.cardNumber)
    ...    - response_body : response body
    [Arguments]    ${output} 

    ${current_date}    Get Current Date    result_format=%Y-%m-%d
    ${current_exchange_rate_date}    ${output}    Split String    ${output}    ,    1
    ${current_exchange_rate_date}    Fetch From Left    ${current_exchange_rate_date}    @
    ${current_exchange_rate_date}    Convert Date    ${current_exchange_rate_date}    date_format=%d/%m/%Y    result_format=%Y-%m-%d 
    ${gap}    Subtract Date From Date    ${current_date}    ${current_exchange_rate_date}    exclude_millis=${True}
    ${gap}    Evaluate    int(${gap}/3600/24)
    IF    0<${gap}<=10
        Log    Exchange rates received are not up to date (${current_exchange_rate_date})    level=WARN    console=${True}
    ELSE IF    ${gap}>10  
        Log    Exchange rates received are more than 10 days old. The enrichment will not be performed    level=ERROR    console=${True}
    END
