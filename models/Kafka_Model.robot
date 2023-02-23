*** Settings ***
Library    String
Library    Collections
Library    ConfluentKafkaLibrary
Library    JSONLibrary
Resource    Kafka_Model.robot
Variables   ../resources/kafka_conf.py

*** Keywords ***
Configure Consumer
    [Documentation]    Open a kakfa consumer to read event
    ...    Parameters :
    ...    - PHASE : environment
    ...    - consumer_topic_name : name of the topic
    ...    Return value :
    ...    - consumer_group_id : id of the consumer group open
    [Arguments]    ${PHASE}    ${consumer_topic_name} 
    ${consumer_group_id}    Create Consumer     server=${SERVER}    port=${PORT}
    ${consumer_topic_name}    Get Topic Full Name    ${PHASE}    ${consumer_topic_name}
    Subscribe Topic    ${consumer_group_id}    ${consumer_topic_name}
    ${message}    Poll    ${consumer_group_id}    decode_format=utf-8 
    RETURN    ${consumer_group_id} 

Configure Producer
    [Documentation]    Open a kakfa producer to inject event
    ...    Parameters :
    ...    - PHASE : environment
    ...    Return value :
    ...    - producer_group_id : id of the producer group open
    [Arguments]    ${PHASE}
    ${producer_group_id}    Create Producer     server=${SERVER}    port=${PORT}
    RETURN    ${producer_group_id}

Write Data Into Topic
    [Documentation]    Inject data in a kakfa producer
    ...    Parameters :
    ...    - producer_group_id : id of the producer group open
    ...    - topic : topic fullname
    ...    - data : data to inject
    [Arguments]    ${producer_group_id}    ${topic}    ${data}
    Log Many    ${producer_group_id}    ${topic}    ${data}
    Produce  group_id=${producer_group_id}  topic=${topic}  value=${data}  
    Wait Until Keyword Succeeds  5x  1s  All Messages Are Delivered  ${producer_group_id}
    Sleep  1sec  # if next command is polling messages in thread we need to wait a second

Read Data From Topic
    [Documentation]    Read data in a kakfa consumer
    ...    Parameters :
    ...    - consumer_group_id : id of the consumer group open
    ...    - expect_data : True/False   (to check whether data should be read or not from the consumer)
    ...    Return value :
    ...    - message_list : list of data read from the consumer
    [Arguments]    ${consumer_group_id}    ${expect_data}=${True}
    ${message_list}    Poll    ${consumer_group_id}    max_records=15    decode_format=utf-8     
    Log List    ${message_list}
    IF     ${expect_data} == ${True}    Should Not Be Empty    ${message_list}    msg=No data read from the consumer
    RETURN    ${message_list}

Write & Read Event
    [Documentation]    Inject then Read data 
    ...    Parameters :
    ...    - PHASE : environment
    ...    - producer_topic_name : topic from where to inject data
    ...    - consumer_topic_name : topic from where to read data
    ...    - data : data to inject
    ...    Return value :
    ...    - events_list : list of data read from the consumer
    [Arguments]    ${PHASE}    ${producer_topic_name}    ${consumer_topic_name}        ${data}
    Log Many    ${PHASE}    ${consumer_topic_name}    ${producer_topic_name}    ${data}  
    #Creation of a consumer client
    ${consumer_group_id}     Configure Consumer    ${PHASE}     ${consumer_topic_name}
    Set Test Variable    ${consumer_group_id}
    #Creation of a producer client
    ${producer_group_id}     Configure Producer    ${PHASE} 
    #Write data into Producer
    Log    ${data}
    ${producer_topic_name}    Get Topic Full Name    ${PHASE}    ${producer_topic_name}
    Write Data Into Topic    ${producer_group_id}    ${producer_topic_name}    ${data}
    #Read data from Consumer
    ${events_list}    Read Data From Topic    ${consumer_group_id}    
    Log List    ${events_list}
    RETURN    ${events_list}

All Messages Are Delivered
    [Documentation]    Wait for all messages in the producer queue to be delivered
    ...    Parameters :
    ...    - producer_id : id of the producer group open
    [Arguments]  ${producer_id}
    ${count}  Flush  ${producer_id}
    Log  Reaming messages to be delivered: ${count}
    Should Be Equal As Integers  ${count}  0

Get Topic Full Name
    [Documentation]    Get the topic fullname form the topic
    ...    Parameters :
    ...    - phase : dev/pdt
    ...    - topic : unprocessed/raw/rich
    ...    Return value :
    ...    - topic_name : topic fullname
    [Arguments]    ${phase}    ${topic_name}
    Log    ${topic_name}
    ${topic_fullname}    Set Variable If    '${topic_name}'=='rich'     ${cluster}.${phase}.${topics}[${topic_name}]    ${phase}.${topics}[${topic_name}] 
    RETURN     ${topic_fullname} 
    
Basic Teardown
    [Documentation]    Unsubscribe and close the open kafka consumer
    ...    Parameters :
    ...    - group_id : list of consumer ids open
    [Arguments]  @{group_id}
    FOR     ${consumer_id}    IN     @{group_id}   
        Unsubscribe  ${consumer_id}
        Close Consumer  ${consumer_id}
    END