*** Settings ***
Resource    ../models/REST_API_Model.robot
Resource    ../models/Kafka_Model.robot
Resource    ../models/AppEvent_Model.robot
Resource    ../models/Databricks_Model.robot
Variables   ../Resources/test_users.py

*** Variables ***
${PHASE}    dev

*** Test Cases ***
01_Kafka_Unprocessed_Topic_Test
    [Documentation]    Write and Read an event threw the unprocessed topic
    [Tags]    ready
    ${appEvent_str}    ${VCNID}    Prepare AppEvent    ${CURDIR}/../${data_path}/appEvent.json    merchant_code=AC
    ${appEvents_list}        Write & Read Event     ${PHASE}    unprocessed    unprocessed    ${appEvent_str}  
    Log List     ${appEvents_list}
    Should Contain    ${appEvents_list}    ${appEvent_str}    msg=AppEvent sent not found in the unprocessed topic consumer
    Set Test Message    *HTML* <b>AppEvent read from the Unprocesed topic </b> :\n${appEvent_str}\n\n     append=${True} 
    [Teardown]    Basic Teardown  ${consumer_group_id}

02_Kafka_Raw_Topic_Test
    [Documentation]    Write and Read an event threw the raw topic
    [Tags]    ready
    ${appEvent_str}    ${VCNID}    Prepare AppEvent    ${CURDIR}/../${data_path}/appEvent.json
    ${appEvents_list}    Write & Read Event     ${PHASE}    raw    raw    ${appEvent_str} 
    Log List     ${appEvents_list}
    Should Contain    ${appEvents_list}    ${appEvent_str}    msg=AppEvent sent not found in the raw topic consumer (VCNID=${VCNID})  
    Set Test Message    *HTML* <b>AppEvent read from the Raw topic </b> :\n${appEvent_str}\n\n     append=${True}   
    [Teardown]    Basic Teardown  ${consumer_group_id}

03_Kafka_Rich_Topic_Test
    [Documentation]    Write and Read an event threw the rich topic
    [Tags]    ready
    ${appEvent_str}    ${VCNID}    Prepare AppEvent    ${CURDIR}/../${data_path}/appEvent.json
    ${appEvents_list}    Write & Read Event     ${PHASE}    rich    rich    ${appEvent_str} 
    Log List     ${appEvents_list}
    Should Contain    ${appEvents_list}    ${appEvent_str}    msg=AppEvent sent not found in the rich topic consumer (VCNID=${VCNID}) 
    Set Test Message    *HTML* <b>AppEvent read from the Rich topic </b> :\n${appEvent_str}\n\n     append=${True}  
    [Teardown]    Basic Teardown  ${consumer_group_id}

04_Kafka_Unprocess_To_Rich_Topic_Test
    [Documentation]    Write an event into the unprocessed topic and read it from the rich topic
    [Tags]    ready
    ${appEvent_str}    ${VCNID}    Prepare AppEvent    ${CURDIR}/../${data_path}/appEvent.json
    ${appEvents_list}    Write & Read Event     ${PHASE}    unprocessed    rich    ${appEvent_str} 
    Log List     ${appEvents_list}
    ${appEvent}     Get Injected AppEvent By Id    ${appEvents_list}    ${VCNID}
    Should Not Be Empty    ${appEvent}     msg=AppEvent sent not found in the rich topic consumer (VCNID=${VCNID})
    Set Test Message    *HTML* <b>AppEvent read from the Rich topic after enrichment </b> :\n${appEvent}\n\n     append=${True}   
    [Teardown]    Basic Teardown  ${consumer_group_id}

05_Kafka_VCN_Creation_To_Unprocessed_Topic_Test
    [Documentation]    Create a VCN card and read the AppEvent generated from the unprocessed topic
    ...    Prerequisite : The VCC appEvents traffic should be redirected to the unprocessed kafka topic
    [Tags]    ready
    ${consumer_group_id}    Configure Consumer    ${PHASE}    unprocessed
    ${VCN_ID}    REST_Create_Card    ${phase}    ${APPUI1A01}    POST_new_VCN_10EUR.json 
    ${appEvents_list}    Read Data From Topic    ${consumer_group_id} 
    ${appEvent}     Get Injected AppEvent By Id    ${appEvents_list}    ${VCN_ID}
    Should Not Be Empty    ${appEvent}     msg=AppEvent sent not found in the unprocessed topic consumer (VCN_ID=${VCN_ID})
    Set Test Message    *HTML* <b>AppEvent read from the Unprocessed topic </b> :\n${appEvent}\n\n     append=${True}   
    [Teardown]     Basic Teardown    ${consumer_group_id} 

06_Kafka_VCN_Creation_To_Raw_Topic_Test
    [Documentation]    Create a VCN card and read from the raw topic
    ...    Prerequisite : The VCC appEvents traffic should be redirected to the unprocessed kafka topic
    [Tags]    ready
    ${consumer_group_id}    Configure Consumer    ${PHASE}    raw
    ${VCN_ID}    REST_Create_Card    ${phase}    ${APPUI1A01}    POST_new_VCN_10EUR.json
    Sleep    5
    ${appEvents_list}    Read Data From Topic    ${consumer_group_id}    expect_data=${False}   
    Log List     ${appEvents_list} 
    Should Not Contain    str(${appEvents_list})    ${VCN_ID}      
    [Teardown]     Basic Teardown    ${consumer_group_id} 


07_Kafka_VCN_Creation_To_Rich_Topic_Test
    [Documentation]    Create a VCN card and read the AppEvent generated from the rich topic
    ...    Prerequisite : The VCC appEvents traffic should be redirected to the unprocessed kafka topic
    [Tags]    ready
    ${consumer_group_id}    Configure Consumer    ${PHASE}    rich  
    ${VCN_ID}    REST_Create_Card    ${phase}    ${APPUI1A01}    POST_new_VCN_10EUR.json
    ${appEvents_list}    Read Data From Topic    ${consumer_group_id}     
    Log List     ${appEvents_list}
    ${appEvent}     Get Injected AppEvent By Id    ${appEvents_list}    ${VCN_ID}   
    Should Not Be Empty    ${appEvent}     msg=AppEvent sent not found in the rich topic consumer (VCN_ID=${VCN_ID})
    Set Test Message    *HTML* <b>AppEvent read from the Rich topic </b> :\n${appEvent}\n\n     append=${True}
    [Teardown]     Basic Teardown    ${consumer_group_id} 

08_Kafka_Recovery_Topic_Test
    [Documentation]    Write and Read an event threw the rich topic
    [Tags]    ready
    ${appEvent_str}    ${VCNID}    Prepare AppEvent    ${EXECDIR}/${data_path}/appEvent.json
    ${appEvents_list}    Write & Read Event     ${PHASE}    recovery    recovery    ${appEvent_str} 
    Log List     ${appEvents_list}
    Should Contain    ${appEvents_list}    ${appEvent_str}    msg=AppEvent sent not found in the rich topic consumer (VCNID=${VCNID}) 
    Set Test Message    *HTML* <b>AppEvent read from the Rich topic </b> :\n${appEvent_str}\n\n     append=${True}  
    [Teardown]    Basic Teardown  ${consumer_group_id}