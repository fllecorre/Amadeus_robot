*** Settings ***
Resource    ../models/REST_API_Model.robot
Resource    ../models/Kafka_Model.robot
Resource    ../models/AppEvent_Model.robot
Resource    ../models/Databricks_Model.robot
Variables   ../resources/test_users.py

*** Variables ***
${PHASE}    dev

*** Test Cases ***
01_Enrichment_Test_With_Fake_AppEvent_EUR
    [Tags]     ready
    [Documentation]    Write an event into the unprocessed topic and check the enriched appEvent from the rich topic
    ${appEvent}    ${PRI}    Prepare AppEvent    ${CURDIR}/../${data_path}/appEvent.json    amount_str=100    currency=EUR
    ${appEvents_list}    Write & Read Event     ${PHASE}    unprocessed    rich    ${appEvent} 
    Log List     ${appEvents_list}
    ${enriched_appEvent}     Get Injected AppEvent By Id    ${appEvents_list}    ${PRI}
    Should Not Be Empty    ${enriched_appEvent}     msg=AppEvent sent not found in the rich topic consumer (PRI=${PRI})
    Check Enriched AppEvent    ${appEvent}    ${enriched_appEvent}    
    [Teardown]    Basic Teardown  ${consumer_group_id}

02_Enrichment_Test_With_Fake_AppEvent_USD
    [Tags]     ready
    [Documentation]    Write an event into the unprocessed topic and check the enriched appEvent from the rich topic
    ${appEvent}    ${PRI}    Prepare AppEvent    ${CURDIR}/../${data_path}/appEvent.json    amount_str=100    currency=USD
    ${appEvents_list}    Write & Read Event     ${PHASE}    unprocessed    rich    ${appEvent} 
    Log List     ${appEvents_list}
    ${enriched_appEvent}     Get Injected AppEvent By Id    ${appEvents_list}    ${PRI}
    Should Not Be Empty    ${enriched_appEvent}     msg=AppEvent sent not found in the rich topic consumer (PRI=${PRI})
    Check Enriched AppEvent    ${appEvent}    ${enriched_appEvent}    
    [Teardown]    Basic Teardown  ${consumer_group_id}

03_Enrichment_Test_With_Fake_AppEvent_CAD
    [Tags]     ready
    [Documentation]    Write an event into the unprocessed topic and check the enriched appEvent from the rich topic
    ${appEvent}    ${PRI}    Prepare AppEvent    ${CURDIR}/../${data_path}/appEvent.json    amount_str=100    currency=CAD
    ${appEvents_list}    Write & Read Event     ${PHASE}    unprocessed    rich    ${appEvent} 
    Log List     ${appEvents_list}
    ${enriched_appEvent}     Get Injected AppEvent By Id    ${appEvents_list}    ${PRI}
    Should Not Be Empty    ${enriched_appEvent}     msg=AppEvent sent not found in the rich topic consumer (PRI=${PRI})
    Check Enriched AppEvent    ${appEvent}    ${enriched_appEvent}    
    [Teardown]    Basic Teardown  ${consumer_group_id}

04_Enrichment_Test_With_VCN_Creation_min
    [Tags]    ready
    [Documentation]    Create a VCN card and check the enriched appEvent generated from the rich topic
    ...    Prerequisite : The VCC appEvents traffic should be redirected to the unprocessed kafka topic
    ${unprocessed_consumer_group_id}    Configure Consumer    ${PHASE}    unprocessed
    ${rich_consumer_group_id}    Configure Consumer    ${PHASE}    rich  
    ${VCN_ID}    REST_Create_Card    ${phase}    ${APPUI1A01}    POST_new_VCN_10EUR.json
    Check Enrichment    ${unprocessed_consumer_group_id}    ${rich_consumer_group_id}    ${VCN_ID}  
    [Teardown]    Basic Teardown  ${unprocessed_consumer_group_id}    ${rich_consumer_group_id}

05_Enrichment_Test_With_VCN_Creation_FULL
    [Tags]    ready
    [Documentation]    Create a VCN card and check the enriched appEvent generated from the rich topic
    ...    Prerequisite : The VCC appEvents traffic should be redirected to the unprocessed kafka topic
    ${unprocessed_consumer_group_id}    Configure Consumer    ${PHASE}    unprocessed
    ${rich_consumer_group_id}    Configure Consumer    ${PHASE}    rich  
    ${VCN_ID}    REST_Create_Card    ${phase}    ${APPUI1A01}    POST_new_VCN_10EUR_full.json
    Check Enrichment    ${unprocessed_consumer_group_id}    ${rich_consumer_group_id}    ${VCN_ID}  
    [Teardown]    Basic Teardown  ${unprocessed_consumer_group_id}    ${rich_consumer_group_id}


06_Enrichment_Test_With_VCN_Creation_USD
    [Tags]    ready
    [Documentation]    Create a VCN card and check the enriched appEvent generated from the rich topic
    ...    Prerequisite : The VCC appEvents traffic should be redirected to the unprocessed kafka topic
    ${unprocessed_consumer_group_id}    Configure Consumer    ${PHASE}    unprocessed
    ${rich_consumer_group_id}    Configure Consumer    ${PHASE}    rich  
    ${VCN_ID}    REST_Create_Card    ${phase}    ${APPUI1A01}    POST_new_VCN_10USD.json
    Check Enrichment    ${unprocessed_consumer_group_id}    ${rich_consumer_group_id}    ${VCN_ID}  
    [Teardown]    Basic Teardown  ${unprocessed_consumer_group_id}    ${rich_consumer_group_id}

07_Enrichment_Test_With_VCN_Creation_CAD
    [Tags]    ready
    [Documentation]    Create a VCN card and check the enriched appEvent generated from the rich topic
    ...    Prerequisite : The VCC appEvents traffic should be redirected to the unprocessed kafka topic
    ${unprocessed_consumer_group_id}    Configure Consumer    ${PHASE}    unprocessed
    ${rich_consumer_group_id}    Configure Consumer    ${PHASE}    rich  
    ${VCN_ID}    REST_Create_Card    ${phase}    ${APPUI1A01}    POST_new_VCN_10CAD.json
    Check Enrichment    ${unprocessed_consumer_group_id}    ${rich_consumer_group_id}    ${VCN_ID}  
    [Teardown]    Basic Teardown  ${unprocessed_consumer_group_id}    ${rich_consumer_group_id}


08_Enrichment_Test_With_VCN_Update
    [Tags]    ready
    [Documentation]    Create a VCN card and check the enriched appEvent generated from the rich topic
    ...    Prerequisite : The VCC appEvents traffic should be redirected to the unprocessed kafka topic
    [Setup]     REST_Create_Card    ${phase}    ${APPUI1A01}   POST_new_VCN_10EUR.json    setup=${True}       
    ${unprocessed_consumer_group_id}    Configure Consumer    ${PHASE}    unprocessed    
    ${rich_consumer_group_id}    Configure Consumer    ${PHASE}    rich  
    REST_Update_Card    ${phase}    ${APPUI1A01}    ${VCN_ID}    PATCH_VCN.json
    ${reservation_ID}    REST_Get_Value_From_Response_byJsonPath    $.data.bookingInfo.reservationID
    Check Enrichment    ${unprocessed_consumer_group_id}    ${rich_consumer_group_id}    ${VCN_ID}    ${reservation_ID}  
    [Teardown]    Basic Teardown  ${unprocessed_consumer_group_id}    ${rich_consumer_group_id}