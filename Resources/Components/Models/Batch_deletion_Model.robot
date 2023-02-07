*** Settings ***
Variables    ../REST_data/REST_variables.py
Variables    ../../../Resources/libs/test_users.py
Library    ../../../Resources/libs/b2bwallet_rest_api_operations.py
Library    Collections
Library    DateTime

*** Keywords ***
Check Get Card List
    [Documentation]    Performs a Get/virtualCards for a specific time frame,
    ...    checks if the response's status is 200
    ...    and returns the card list retrieved
    ...    Confluence url: https://rndwww.nce.amadeus.net/confluence/pages/viewpage.action?pageId=861225058

    [Arguments]    ${url}    ${user}    ${time_frame}    ${status}
    ${status}    ${card_list}    Get Card List    ${url}    ${user}    ${time_frame}    ${status}
    Should Be Equal    ${status}    ${200}
    RETURN    ${card_list}

Check Deleted Cards
    [Documentation]    Deletes a list of cards using their ids, 
    ...    returning a list of tuples composed by:
    ...    - the status_code of the operation
    ...    - the message related to the operation
    ...    - the id of the involved card

    [Arguments]    ${url}    ${user}    ${ids}
    @{deleted_cards}=    Delete Cards    ${url}    ${user}    ${ids}
    Check Deleted Cards Status    ${deleted_cards}
    RETURN    ${deleted_cards}

Delete old cards
    [Documentation]    Based on the selected provider(s) 
    ...    it deletes all the cards in a time range of [today - one_month_ago, today - one_week_ago]
    [Arguments]    ${env}    ${state}    ${providers}
    ${base_url}=  Get From Dictionary    ${REST_base_url}    ${env}
    @{time_frames}=    Get Time Frames
    @{report}=    Create List
    FOR    ${frame}    IN    @{time_frames}
        ${next_frame}=    Add Time To Date    ${frame}    1 hour    result_format=%Y-%m-%dT%H-%M-%S
        Log To Console    \n Analizing time frame ${frame}, ${next_frame}
        ${card_list}    Check Get Card List    ${base_url}${REST_virtual_cards_URI}    ${APPUI1A01}    ${frame}    ${state}
        IF    'errors' in ${card_list}
            Log To Console    \n No cards found in the current time frame
            CONTINUE
        END
        @{ids}=    Get Ids From Card List    ${providers}    ${card_list}
        @{deleted_cards}=    Check Deleted Cards    ${base_url}${REST_virtual_cards_URI}    ${APPUI1A01}    ${ids}
        Log To Console    \n deleted_cards: ${deleted cards}
        @{report}=    Append    ${report}    ${deleted_cards}
    END
    ${final_frame}=    Add Time To Date    ${time_frames}[-1]    1 hour    result_format=%Y-%m-%dT%H-%M-%S
    Log To Console    \n Start date: ${time_frames}[0], End date: ${final_frame}
    Log To Console    \n report: ${report}
    ${pretty_report}=    Interpret Report    ${report}
    RETURN    ${pretty_report}