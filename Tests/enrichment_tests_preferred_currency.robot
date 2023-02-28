*** Settings ***
Resource    ../models/REST_API_Model.robot
Resource    ../models/Kafka_Model.robot
Resource    ../models/AppEvent_Model.robot
Resource    ../models/Databricks_Model.robot
Variables   ../Resources/test_users.py

*** Variables ***
${PHASE}    dev

*** Test Cases ***
01_Enrichment_Test_With_MerchantCode
    [Tags]     ready
    [Documentation]    Write an event into the unprocessed topic and check the enriched appEvent from the rich topic
    ${appEvent}    ${PRI}    Prepare AppEvent    ${CURDIR}/../${data_path}/appEvent.json    amount_str=100    currency=AUD    merchant_code=AC
    ${appEvents_list}    Write & Read Event     ${PHASE}    unprocessed    rich    ${appEvent} 
    Log List     ${appEvents_list}
    ${enriched_appEvent}     Get Injected AppEvent By Id    ${appEvents_list}    ${PRI}
    Should Not Be Empty    ${enriched_appEvent}     msg=AppEvent sent not found in the rich topic consumer (PRI=${PRI})
    Check Enriched AppEvent    ${appEvent}    ${enriched_appEvent}    
    [Teardown]    Basic Teardown  ${consumer_group_id}

02_Enrichment_Test_With_PaymentRequestor
    [Tags]     ready
    [Documentation]    Write an event into the unprocessed topic and check the enriched appEvent from the rich topic
    ${appEvent}    ${PRI}    Prepare AppEvent    ${CURDIR}/../${data_path}/appEvent.json    amount_str=100    currency=AUD    payment_requestor=AC
    ${appEvents_list}    Write & Read Event     ${PHASE}    unprocessed    rich    ${appEvent} 
    Log List     ${appEvents_list}
    ${enriched_appEvent}     Get Injected AppEvent By Id    ${appEvents_list}    ${PRI}
    Should Not Be Empty    ${enriched_appEvent}     msg=AppEvent sent not found in the rich topic consumer (PRI=${PRI})
    Check Enriched AppEvent    ${appEvent}    ${enriched_appEvent}    
    [Teardown]    Basic Teardown  ${consumer_group_id}

03_Enrichment_Test_With_MerchantCode_and_PaymentRequestor
    [Tags]     ready
    [Documentation]    Write an event into the unprocessed topic and check the enriched appEvent from the rich topic
    ${appEvent}    ${PRI}    Prepare AppEvent    ${CURDIR}/../${data_path}/appEvent.json    amount_str=100    currency=AUD    merchant_code=AC    payment_requestor=AH
    ${appEvents_list}    Write & Read Event     ${PHASE}    unprocessed    rich    ${appEvent} 
    Log List     ${appEvents_list}
    ${enriched_appEvent}     Get Injected AppEvent By Id    ${appEvents_list}    ${PRI}
    Should Not Be Empty    ${enriched_appEvent}     msg=AppEvent sent not found in the rich topic consumer (PRI=${PRI})
    Check Enriched AppEvent    ${appEvent}    ${enriched_appEvent}    
    [Teardown]    Basic Teardown  ${consumer_group_id}

04_Enrichment_Test_Without_MerchantCode_nor_PaymentRequestor
    [Tags]     ready
    [Documentation]    Write an event into the unprocessed topic and check the enriched appEvent from the rich topic
    ${appEvent}    ${PRI}    Prepare AppEvent    ${CURDIR}/../${data_path}/appEvent.json    amount_str=100    currency=AUD
    ${appEvents_list}    Write & Read Event     ${PHASE}    unprocessed    rich    ${appEvent} 
    Log List     ${appEvents_list}
    ${enriched_appEvent}     Get Injected AppEvent By Id    ${appEvents_list}    ${PRI}
    Should Not Be Empty    ${enriched_appEvent}     msg=AppEvent sent not found in the rich topic consumer (PRI=${PRI})
    Check Enriched AppEvent    ${appEvent}    ${enriched_appEvent}    
    [Teardown]    Basic Teardown  ${consumer_group_id}

05_Enrichment_Test_Without_Preferred_Currency
    [Tags]     ready
    [Documentation]    Write an event into the unprocessed topic and check the enriched appEvent from the rich topic
    ${appEvent}    ${PRI}    Prepare AppEvent    ${CURDIR}/../${data_path}/appEvent.json    amount_str=100    currency=AUD    merchant_code=AF    payment_requestor=AF
    ${appEvents_list}    Write & Read Event     ${PHASE}    unprocessed    rich    ${appEvent} 
    Log List     ${appEvents_list}
    ${enriched_appEvent}     Get Injected AppEvent By Id    ${appEvents_list}    ${PRI}
    Should Not Be Empty    ${enriched_appEvent}     msg=AppEvent sent not found in the rich topic consumer (PRI=${PRI})
    Check Enriched AppEvent    ${appEvent}    ${enriched_appEvent}    
    [Teardown]    Basic Teardown  ${consumer_group_id}

06_Enrichment_Test_With_Wrong_Preferred_Currency
    [Tags]     ready
    [Documentation]    Write an event into the unprocessed topic and check the enriched appEvent from the rich topic
    ${appEvent}    ${PRI}    Prepare AppEvent    ${EXECDIR}/${data_path}/appEvent.json    amount_str=100    currency=AUD    merchant_code=TEST_CURRENCY_CODE_WRONG_FORMAT    payment_requestor=TEST_CURRENCY_CODE_WRONG_FORMAT
    ${appEvents_list}    Write & Read Event     ${PHASE}    unprocessed    rich    ${appEvent} 
    Log List     ${appEvents_list}
    ${enriched_appEvent}     Get Injected AppEvent By Id    ${appEvents_list}    ${PRI}
    Should Not Be Empty    ${enriched_appEvent}     msg=AppEvent sent not found in the rich topic consumer (PRI=${PRI})
    Check Enriched AppEvent    ${appEvent}    ${enriched_appEvent}    
    [Teardown]    Basic Teardown  ${consumer_group_id}

07_Enrichment_Test_With_Lower_Case_Preferred_Currency
    [Tags]     ready
    [Documentation]    Write an event into the unprocessed topic and check the enriched appEvent from the rich topic
    ${appEvent}    ${PRI}    Prepare AppEvent    ${CURDIR}/../${data_path}/appEvent.json    amount_str=100    currency=AUD    merchant_code=TEST_CURRENCY_CODE_LOWER_CASE    payment_requestor=TEST_CURRENCY_CODE_LOWER_CASE
    ${appEvents_list}    Write & Read Event     ${PHASE}    unprocessed    rich    ${appEvent} 
    Log List     ${appEvents_list}
    ${enriched_appEvent}     Get Injected AppEvent By Id    ${appEvents_list}    ${PRI}
    Should Not Be Empty    ${enriched_appEvent}     msg=AppEvent sent not found in the rich topic consumer (PRI=${PRI})
    Check Enriched AppEvent    ${appEvent}    ${enriched_appEvent}    
    [Teardown]    Basic Teardown  ${consumer_group_id}

08_Enrichment_Test_With_Space_As_Preferred_Currency
    [Tags]     ready
    [Documentation]    Write an event into the unprocessed topic and check the enriched appEvent from the rich topic
    ${appEvent}    ${PRI}    Prepare AppEvent    ${CURDIR}/../${data_path}/appEvent.json    amount_str=100    currency=AUD    merchant_code=TEST_CURRENCY_CODE_SPACE    payment_requestor=TEST_CURRENCY_CODE_SPACE
    ${appEvents_list}    Write & Read Event     ${PHASE}    unprocessed    rich    ${appEvent} 
    Log List     ${appEvents_list}
    ${enriched_appEvent}     Get Injected AppEvent By Id    ${appEvents_list}    ${PRI}
    Should Not Be Empty    ${enriched_appEvent}     msg=AppEvent sent not found in the rich topic consumer (PRI=${PRI})
    Check Enriched AppEvent    ${appEvent}    ${enriched_appEvent}    
    [Teardown]    Basic Teardown  ${consumer_group_id}

09_Enrichment_Test_With_Two_Different_Preferred_Currencies
    [Tags]     ready
    [Documentation]    Write an event into the unprocessed topic and check the enriched appEvent from the rich topic
    ${appEvent}    ${PRI}    Prepare AppEvent    ${CURDIR}/../${data_path}/appEvent.json    amount_str=100    currency=AUD    merchant_code=TEST_CUSTOMER_CODE_DUPLICATED    payment_requestor=TEST_CUSTOMER_CODE_DUPLICATED
    ${appEvents_list}    Write & Read Event     ${PHASE}    unprocessed    rich    ${appEvent} 
    Log List     ${appEvents_list}
    ${enriched_appEvent}     Get Injected AppEvent By Id    ${appEvents_list}    ${PRI}
    Should Not Be Empty    ${enriched_appEvent}     msg=AppEvent sent not found in the rich topic consumer (PRI=${PRI})
    Check Enriched AppEvent    ${appEvent}    ${enriched_appEvent}    
    [Teardown]    Basic Teardown  ${consumer_group_id}