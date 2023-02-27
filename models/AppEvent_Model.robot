*** Settings ***
Library    Collections
Library    String
Library    DateTime
Library    JSONLibrary
Library    deepdiff
Library    CSVLibrary
Resource   Kafka_Model.robot
Resource   Databricks_Model.robot


*** Keywords ***
Prepare AppEvent
    [Documentation]    Build an VCC AppEvent from a template
    ...    Parameters :
    ...    - path_to_appEvent_file : path to to the VCC appEvent template 
    ...    - amount_str : amount value 
    ...    - currency : currency value
    ...    - merchant_code : merchant_code value (not mandatory)
    ...    - payment_requestor : payment_requestor value (not mandatory)
    ...    Return value :
    ...    - appEvent_str : resulting appEvent in a string format
    ...    - VCNID : fake VCNID of the AppEvent
    [Arguments]    ${path_to_appEvent_file}     ${amount_str}=10    ${currency}=EUR    ${merchant_code}=${None}    ${payment_requestor}=${None}
        
    ${appEvent_dict}    Load JSON From File    ${path_to_appEvent_file}
    ${VCNID_suffixe}    Generate Random String    length=4    chars=[UPPER][NUMBERS]
    ${VCNID}    Set Variable    2222${VCNID_suffixe}
    ${current_epoch_time}    Get Current Date    result_format=epoch
    ${updated_appEvent_dict}    Update Value To Json    ${appEvent_dict}    $.VCNID    ${VCNID}
    ${updated_appEvent_dict}    Update Value To Json    ${updated_appEvent_dict}    $.Amount    ${amount_str}
    ${updated_appEvent_dict}    Update Value To Json    ${updated_appEvent_dict}    $.Currency    ${currency}
    ${updated_appEvent_dict}    Update Value To Json    ${updated_appEvent_dict}    $.Epoch    ${current_epoch_time}

    IF    '${merchant_code}' != '${None}'
        ${object_to_add}	Create Dictionary	MerchantCode=${merchant_code}
        ${updated_appEvent_dict}    Add Object To Json    ${updated_appEvent_dict}     $    ${object_to_add}
    END
    IF    '${payment_requestor}' != '${None}'        
        ${object_to_add}	Create Dictionary	PaymentRequestor=${payment_requestor}
        ${updated_appEvent_dict}    Add Object To Json    ${updated_appEvent_dict}     $    ${object_to_add}
    END
   
    ${VCNID}    Get Value From Json    ${updated_appEvent_dict}    $.VCNID
    ${appEvent_str}    Convert JSON To String    ${updated_appEvent_dict}
    Log    ${appEvent_str}
    RETURN    ${appEvent_str}    ${VCNID}[0]

Get Injected AppEvent By Id
    [Documentation]    Retrieve a specific AppEvent from a list of appEvents
    ...    Parameters :
    ...    - appEvents_list : list of AppEvents 
    ...    - ID : ID parameter can be either VCN_ID or PRI (to identify the AppEvent)
    ...    - other_identifier (not mandatory): other identifier that can be used in addition to the ID parameter 
    ...    Return value :
    ...    - appEvent : targeted appEvent    
    [Arguments]    ${appEvents_list}    ${ID}    ${other_identifier}=None
    FOR    ${appEvent}    IN    @{appEvents_list}
        IF    '${other_identifier}' == '${None}'
            IF    '${ID}' in '${appEvent}' 
                Log    ${appEvent}
                RETURN    ${appEvent}
            END
        ELSE 
            IF    ('${ID}' and '${other_identifier}') in '${appEvent}'    
                Log    ${appEvent}
                RETURN    ${appEvent}
            END
        END     
    END
    RETURN    ${EMPTY}

Check Enrichment
    [Documentation]    Retrieve and check an enriched appEvent
    ...    Parameters :
    ...    - unprocessed_consumer_group_id : id of the unprocessed kafka topic consumer (to get the injected AppEvent)
    ...    - rich_consumer_group_id : id of the rich kafka topic consumer (to get the enriched AppEvent)
    ...    - ID : ID parameter can be either VCN_ID or PRI (to identify the AppEvent)
    ...    - other_identifier (not mandatory): other identifier that can be used in addition to the ID parameter  
    [Arguments]    ${unprocessed_consumer_group_id}    ${rich_consumer_group_id}     ${ID}    ${other_identifier}=None    
    ${appEvents_list}    Read Data From Topic    ${unprocessed_consumer_group_id}     
    Log List     ${appEvents_list}
    ${enriched_appEvents_list}    Read Data From Topic    ${rich_consumer_group_id}
    Log List     ${enriched_appEvents_list}
    ${appEvent}     Get Injected AppEvent By Id    ${appEvents_list}    ${ID}    ${other_identifier}    
    ${enriched_appEvent}     Get Injected AppEvent By Id    ${enriched_appEvents_list}    ${ID}    ${other_identifier}    
    Should Not Be Empty    ${appEvent}     msg=AppEvent sent not found in the rich topic consumer (ID=${ID})
    Should Not Be Empty    ${enriched_appEvent}     msg=AppEvent sent not found in the rich topic consumer (ID=${ID})
    Check Enriched AppEvent    ${appEvent}    ${enriched_appEvent} 
       

Check Enriched AppEvent
    [Documentation]    Compare the original and the enriched AppEvent and check the currencies conversions
    ...    Parameters :
    ...    - appEvent : original appEvent
    ...    - enriched_appEvent : enriched appEvent (containing new fields)
    [Arguments]    ${appEvent}    ${enriched_appEvent}  ${check_conversion}=OFF 
    &{original_fields}    Get Original Field From AppEvent    ${appEvent} 
    &{new_fields}    Get New Fields From AppEvent    ${enriched_appEvent}
    ${customer_preferred_currency}    Get Customer Preferred Currency    &{original_fields}
    Check AppEvents Diff    ${appEvent}    ${enriched_appEvent}    ${original_fields}    ${customer_preferred_currency} 
    Check Conversion    ${original_fields}    ${new_fields}    ${customer_preferred_currency} 
   
Check AppEvents Diff
    [Documentation]    Check differences between original and enriched appEvents
    ...    Parameters :
    ...    - appEvent : original appEvent
    ...    - enriched_appEvent : enriched appEvent (containing new fields)
    ...    - original_fields : some fields from the original appEvents
    ...    - customer_preferred_currency : dict containing merchant and payment requestor preferred currencies
    [Arguments]    ${appEvent}    ${enriched_appEvent}     ${original_fields}    ${customer_preferred_currency} 
    ${diff}    Evaluate    deepdiff.DeepDiff(${appEvent}, ${enriched_appEvent}, ignore_order=False)
    Log     ${diff}
    ${appEvent}    Convert String To Json    ${appEvent}
    ${merchant_preferred_currency_status}    Is Preferred Currency Valid    ${customer_preferred_currency}[merchant_preferred_currency]
    ${payment_requestor_preferred_currency_status}    Is Preferred Currency Valid    ${customer_preferred_currency}[payment_requestor_preferred_currency]    
    
    IF    '${merchant_preferred_currency_status}'=='${False}' and '${payment_requestor_preferred_currency_status}'=='${False}'
        Dictionary Should Contain Item     ${diff}    dictionary_item_added    [root['AmountInEUR'], root['AmountInUSD']]
    ELSE IF    '${merchant_preferred_currency_status}'=='${False}'     
        Dictionary Should Contain Item     ${diff}    dictionary_item_added    [root['AmountInEUR'], root['AmountInPaymentRequestorPreferredCurrency'], root['AmountInUSD'], root['PaymentRequestorPreferredCurrency']]
    ELSE IF    '${payment_requestor_preferred_currency_status}'=='${False}'
         Dictionary Should Contain Item     ${diff}    dictionary_item_added    [root['AmountInEUR'], root['AmountInMerchantPreferredCurrency'], root['AmountInUSD'], root['MerchantPreferredCurrency']]    
    ELSE
        Dictionary Should Contain Item     ${diff}    dictionary_item_added    [root['AmountInEUR'], root['AmountInMerchantPreferredCurrency'], root['AmountInPaymentRequestorPreferredCurrency'], root['AmountInUSD'], root['MerchantPreferredCurrency'], root['PaymentRequestorPreferredCurrency']]  
    END
    Dictionary Should Not Contain Key     ${diff}    dictionary_item_removed     msg=*HTML* Field(s) removed from the original appEvent, see <b>'dictionary_item_removed'</b> in : \n${diff}    
    Dictionary Should Not Contain Key   ${diff}    values_changed    msg=*HTML* Value(s) changed from the original appEvent, see <b>'values_changed'</b> in : \n${diff}   
    Set Test Message    *HTML* <b>Original AppEvent</b> :\n${appEvent}\n\n     append=${True}   
    Set Test Message    *HTML* <b>Enriched AppEvent</b> :\n${enriched_appEvent}\n\n    append=${True}

Get Original Field From AppEvent
    [Documentation]    Get fields from the original appEvent 
    ...    Parameters :
    ...    - appEvent : original appEvent
    ...    Return value :
    ...    - original_fields : dictionary containing some fields and values from the original appEvent
    [Arguments]    ${appEvent} 
    ${appEvent}    Convert String To Json    ${appEvent} 
    ${amount}    Get Value From Json    ${appEvent}     $.Amount    fail_on_empty=${True}
    ${currency}    Get Value From Json    ${appEvent}     $.Currency    fail_on_empty=${True}
    ${payment_requestor}    Get Value From Json    ${appEvent}     $.PaymentRequestor    fail_on_empty=${False}
    ${merchant_code}    Get Value From Json    ${appEvent}     $.MerchantCode    fail_on_empty=${False}
    #Length of non mandatory fields
    ${payment_requestor_len}     Get Length    ${payment_requestor}
    ${merchant_code_len}     Get Length    ${merchant_code}
    &{original_fields}    Create Dictionary 
    ...   amount=${amount}[0]   
    ...   currency=${currency}[0] 
    IF    ${payment_requestor_len} != 0  Set To Dictionary    ${original_fields}     payment_requestor=${payment_requestor}[0]
    IF    ${merchant_code_len} != 0    Set To Dictionary    ${original_fields}    merchant_code=${merchant_code}[0]
    RETURN    &{original_fields}

Get New Fields From AppEvent
    [Documentation]    Get fields from the original appEvent 
    ...    Parameters :
    ...    - appEvent : enriched appEvent
    ...    Return value :
    ...    - new_fields : dictionary containing  new fields and values from the enriched appEvent
    [Arguments]    ${appEvent}
    ${appEvent}    Convert String To Json    ${appEvent} 
    ${amount_in_USD}    Get Value From Json    ${appEvent}     $.AmountInUSD    fail_on_empty=${True}
    ${amount_in_EUR}    Get Value From Json    ${appEvent}     $.AmountInEUR    fail_on_empty=${True}
    ${payment_requestor_preferred_currency}    Get Value From Json    ${appEvent}     $.PaymentRequestorPreferredCurrency    fail_on_empty=${False}
    ${merchant_preferred_currency}    Get Value From Json    ${appEvent}     $.MerchantPreferredCurrency    fail_on_empty=${False}
    ${amount_in_payment_requestor_preferred_currency}    Get Value From Json    ${appEvent}     $.AmountInPaymentRequestorPreferredCurrency    fail_on_empty=${False}
    ${amount_in_merchant_preferred_currency}    Get Value From Json    ${appEvent}     $.AmountInMerchantPreferredCurrency    fail_on_empty=${False}
    #Length of non mandatory fields
    ${payment_requestor_preferred_currency_len}     Get Length    ${payment_requestor_preferred_currency}
    ${merchant_preferred_currency_len}     Get Length    ${merchant_preferred_currency}
    ${amount_in_payment_requestor_preferred_currency_len}     Get Length    ${amount_in_payment_requestor_preferred_currency}
    ${amount_in_merchant_preferred_currency_len}     Get Length    ${amount_in_merchant_preferred_currency}
    
    &{new_fields}    Create Dictionary 
    ...   amount_in_USD=${amount_in_USD}[0]    
    ...   amount_in_EUR=${amount_in_EUR}[0]    
    IF    ${payment_requestor_preferred_currency_len} != 0   Set To Dictionary    ${new_fields}    payment_requestor_preferred_currency=${payment_requestor_preferred_currency}[0]    
    IF    ${merchant_preferred_currency_len} != 0    Set To Dictionary    ${new_fields}    merchant_preferred_currency=${merchant_preferred_currency}[0]
    IF    ${amount_in_payment_requestor_preferred_currency_len} != 0   Set To Dictionary    ${new_fields}    amount_in_payment_requestor_preferred_currency=${amount_in_payment_requestor_preferred_currency}[0]
    IF    ${amount_in_merchant_preferred_currency_len} != 0    Set To Dictionary    ${new_fields}    amount_in_merchant_preferred_currency=${amount_in_merchant_preferred_currency}[0]  
    RETURN    &{new_fields}

Check Values Format
    [Documentation]    Check values format of new fields
    ...    Parameters :
    ...    - new_fields : dictionary containing  new fields and values from the enriched appEvent
     [Arguments]    &{new_fields}
    FOR     ${field}    ${value}    IN    &{new_fields} 
        IF    '${field}' == 'amount_in_USD' or '${field}' == 'amount_in_EUR'
            Check Decimal Length    ${value}   2    msg=Amount in USD : decimal length of ${value} is not correct : expected = 2 (.xx)
        END
        IF    '${field}' == 'payment_requestor_preferred_currency' or '${field}' == 'merchant_preferred_currency'
            Should Match Regexp    ${value}    [A-Z]{3}    msg=Expected format of the customer preferred currency ${value} is not correct : expected = XXX (ex : USD)
        END
        IF    '${field}' == 'amount_in_payment_requestor_preferred_currency' or '${field}' == 'amount_in_merchant_preferred_currency'
            Check Decimal Length    ${value}    3    msg=Amount Customer Preferred Currency : decimal length of ${value} is not correct : expected = 3 (.xxx)
        END
    END     

Check Conversion
    [Documentation]    Check conversion of the amount in USD, EUR and in preferred currency
    ...    Parameters :
    ...    - original_fields : dictionary containing some fields and values from the original appEvent
    ...    - new_fields : dictionary containing  new fields and values from the enriched appEvent
    ...    - customer_preferred_currency : dict containing merchant and payment requestor preferred currencies
    [Arguments]    ${original_fields}    ${new_fields}    ${customer_preferred_currency} 
    &{exchange_rates_dict}    Get Exchange Rates    ${original_fields}[currency]     ${customer_preferred_currency}   
    ${merchant_preferred_currency}    Set Variable    ${customer_preferred_currency}[merchant_preferred_currency]
    ${payment_requestor_preferred_currency}    Set Variable    ${customer_preferred_currency}[payment_requestor_preferred_currency]
    #AmountInUSD
    ${expected_amount_in_USD}    Evaluate    round(${original_fields}[amount]*${exchange_rates_dict}[rate_${original_fields}[currency]_USD], 2)
    Should Be Equal As Numbers    ${new_fields}[amount_in_USD]    ${expected_amount_in_USD}    msg=Error in USD conversion : actual = ${new_fields}[amount_in_USD], expected = ${expected_amount_in_USD}    values=False 
    Set Test Message    *HTML*<b>Amount</b> = ${original_fields}[amount]\n<b>Currency</b> = ${original_fields}[currency]\n<b>Exchange rate USD</b> = ${exchange_rates_dict}[rate_${original_fields}[currency]_USD]\n<b>Amount in USD</b> = ${new_fields}[amount_in_USD]\n    append=${True}
    #AmountInEUR
    ${expected_amount_in_EUR}    Evaluate    round(${original_fields}[amount]*${exchange_rates_dict}[rate_${original_fields}[currency]_EUR], 2)
    Should Be Equal As Numbers    ${new_fields}[amount_in_EUR]    ${expected_amount_in_EUR}    msg=Error in EUR conversion : actual = ${new_fields}[amount_in_EUR], expected = ${expected_amount_in_EUR}    values=False
    Set Test Message    *HTML*<b>Exchange rate EUR</b> = ${exchange_rates_dict}[rate_${original_fields}[currency]_EUR]\n<b>Amount in EUR</b> = ${new_fields}[amount_in_EUR]\n    append=${True}
    #AmounInPaymentRequestorPreferredCurrency
    IF    '${payment_requestor_preferred_currency}' != '${None}' and '${exchange_rates_dict}[rate_${original_fields}[currency]_${payment_requestor_preferred_currency}]' != 'NULL'
        ${expected_amount_in_payment_requestor_preferred_currency}    Evaluate    round(${original_fields}[amount]*${exchange_rates_dict}[rate_${original_fields}[currency]_${payment_requestor_preferred_currency}], 3)
        Should Be Equal As Numbers    ${new_fields}[amount_in_payment_requestor_preferred_currency]    ${expected_amount_in_payment_requestor_preferred_currency}      msg=Error in ${payment_requestor_preferred_currency} conversion : actual = ${new_fields}[amount_in_payment_requestor_preferred_currency], expected = ${original_fields}[amount]*${exchange_rates_dict}[rate_${original_fields}[currency]_${payment_requestor_preferred_currency}]
        Set Test Message    *HTML*<b>Exchange rate ${payment_requestor_preferred_currency}</b> = ${exchange_rates_dict}[rate_${original_fields}[currency]_${payment_requestor_preferred_currency}]\n<b>Amount in Payment Requestor Preferred Currency</b> = ${new_fields}[amount_in_payment_requestor_preferred_currency]\n    append=${True}
    ELSE
        #Dictionary Should Not Contain Key    ${new_fields}    amount_in_payment_requestor_preferred_currency
        No Operation
    END
    #AmounInMerchantPreferredCurrency
    IF    '${merchant_preferred_currency}' != '${None}' and '${exchange_rates_dict}[rate_${original_fields}[currency]_${merchant_preferred_currency}]' != 'NULL'
        ${expected_amount_in_merchant_preferred_currency}    Evaluate    round(${original_fields}[amount]*${exchange_rates_dict}[rate_${original_fields}[currency]_${merchant_preferred_currency}], 3)
        Should Be Equal As Numbers    ${new_fields}[amount_in_merchant_preferred_currency]    ${expected_amount_in_merchant_preferred_currency}      msg=Error in ${merchant_preferred_currency} conversion : actual = ${new_fields}[amount_in_merchant_preferred_currency], expected = ${original_fields}[amount]*${exchange_rates_dict}[rate_${original_fields}[currency]_${merchant_preferred_currency}] 
        Set Test Message    *HTML*<b>Exchange rate ${merchant_preferred_currency}</b> = ${exchange_rates_dict}[rate_${original_fields}[currency]_${merchant_preferred_currency}]\n<b>Amount in Merchant Preferred Currency</b> = ${new_fields}[amount_in_merchant_preferred_currency]\n    append=${True} 
    ELSE
        #Dictionary Should Not Contain Key    ${new_fields}    amount_in_merchant_preferred_currency
        No Operation
    END

Get Customer Preferred Currency
    [Documentation]    Retrieve the customer preferred currency from configuration file. 
    ...    Looking for match between the CustomerCode from the configuration file and the merchantCode/PaymentRequestor from the AppEvent
    ...    Parameters :
    ...    - original_fields : dictionary containing some fields and values from the original appEvent
    ...    Return value :
    ...    - preferred_currency : dict containing merchant and payment requestor preferred currencies
    [Arguments]    &{original_fields}
    @{customer_preferred_currency_list}    Read Csv File To Associative        ${CURDIR}/../${data_path}/preferred_currency_per_customer.csv
    Log    ${customer_preferred_currency_list}
    ${is_merchant_code_present}    Run Keyword And Return Status    Get From Dictionary    ${original_fields}    merchant_code    
    ${is_payment_requestor_present}    Run Keyword And Return Status    Get From Dictionary    ${original_fields}    payment_requestor    
    &{preferred_currency}    Create Dictionary
    IF     '${is_merchant_code_present}' == '${True}'
        FOR    ${dict}     IN     @{customer_preferred_currency_list} 
          
            IF    '${dict}[CustomerCode]' == '${original_fields}[merchant_code]' and '${dict}[CustomerPreferredCurrency]' != '${EMPTY}'
                
                ${merchant_preferred_currency}    Get From Dictionary    ${dict}    CustomerPreferredCurrency
                Set To Dictionary    ${preferred_currency}    merchant_preferred_currency=${merchant_preferred_currency}
                BREAK
            ELSE
                Set To Dictionary    ${preferred_currency}    merchant_preferred_currency=${None}
            END   
        END  
    ELSE
        Set To Dictionary    ${preferred_currency}    merchant_preferred_currency=${None}
    END 
    IF    '${is_payment_requestor_present}' == '${True}'   
        FOR    ${dict}     IN     @{customer_preferred_currency_list} 
            IF    '${dict}[CustomerCode]' == '${original_fields}[payment_requestor]' and '${dict}[CustomerPreferredCurrency]' != '${EMPTY}'  
                ${payment_requestor_preferred_currency}    Get From Dictionary    ${dict}    CustomerPreferredCurrency
                Set To Dictionary    ${preferred_currency}    payment_requestor_preferred_currency=${payment_requestor_preferred_currency}
                BREAK
            ELSE
                Set To Dictionary    ${preferred_currency}    payment_requestor_preferred_currency=${None}
            END 
        END
    ELSE
        Set To Dictionary    ${preferred_currency}    payment_requestor_preferred_currency=${None}
    END     
    ${dict_length} =  Get Length  ${preferred_currency}
    IF    ${dict_length} != 0    RETURN    ${preferred_currency}

Is Preferred Currency Valid  
     [Documentation]    Check the validity of the currency retrieved from the configuration file
    ...    Parameters :
    ...    - currency : preferred currency from the configuration file
    ...    Return value :
    ...    - True/False
    [Arguments]    ${currency}
    ${status_letter_case}    Run Keyword And Return Status    Should Match Regexp    ${currency}    [A-Za-z]{3} 
    ${status_wrong_currency}    Run Keyword And Return Status    Should Not Match Regexp    ${currency}    [X]{3}     
    IF     '${status_letter_case}' == '${False}' or '${status_wrong_currency}' == '${False}'    RETURN     ${False}  
    RETURN    ${True} 

Check Decimal Length
    [Documentation]    Comparison between the value decimal length and the expected decimal length
    ...    Parameters :
    ...    - float : actual value
    ...    - expected_decimal_length : expected decimal length of the value
    ...    - error_msg :  customed error message if mismatch the actual and expected result
    [Arguments]    ${float}    ${expected_decimal_length}    ${error_msg}=None    
    ${is_float}    Evaluate    isinstance(${float}, float)
    ${str}    Convert To String    ${float}
    ${decimal}    Fetch From Right    ${str}    .    
    ${decimal_length}    Get Length    ${decimal}
    Should Be Equal As Integers    ${decimal_length}    ${expected_decimal_length}    msg=${error_msg}

