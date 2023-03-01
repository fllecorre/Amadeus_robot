*** Settings ***
Library           OperatingSystem
Library           String
Library           JSONLibrary
Library           Collections
Library           DebugLibrary
Library           DateTime
Library           CSVLibrary
Library           ../../../Resources/libs/lss_token_generator.py  
Resource          B2bWalletUI_REST_API_Model.robot


*** Keywords ***
Suite_Setup
    [Documentation]    Prerequisite actions to be performed before the test case execution
    [Arguments]   ${PHASE}    ${USER}     ${TABMODE}    	@{keywords}
    # Get Portal Version
    Log    ${keywords}
    Import Locators As Variables
    FOR    ${keyword}    IN    @{keywords}
        Log    ${keyword} 
        # Start kassette process, generate new token and go to the requested url (threw proxy)
        IF   'kassette' in '${keyword}'
            ${kassette_config_file}    Set Variable    ${keyword}
            ${PROXY}    Start kassette Process    proxy/${kassette_config_file}
            Generate auth Token    ${PHASE}    ${USER} 
            ${BaseUrl}    Get Base Url     ${PHASE}   ${SUPPIER_URL_LIST}
            Log    ${BaseUrl}
            Go To b2bwallet Page    ${BaseUrl}  ${TABMODE}  ${PROXY}   
        # Generate a new token and go to the requested url 
        ELSE IF    '${keyword}' == 'token' 
            Generate auth Token    ${PHASE}    ${USER}     
            ${BaseUrl}    Get Base Url     ${PHASE}   ${SUPPIER_URL_LIST}
            Log    ${BaseUrl}
            Go To b2bwallet Page    ${BaseUrl}  ${TABMODE}
        END
    END

Test_Setup
    [Documentation]    Prerequisite actions to be performed before the test case execution
    ...    Phase:    Environment 
    ...    User :    User 
    ...    NAV_URL:  Url to navigate to
    ...    keywords : list of keywords to perform some actions as prerequisite of the test  
    [Arguments]      ${PHASE}   ${USER}   ${NAV_URL}     @{keywords}
    Log    ${keywords}
    FOR    ${keyword}    IN    @{keywords}
        Log    ${keyword}
        IF     'createCard' in '${keyword}' 
            ${keyword}     ${cards_number}     ${status}    Split String    ${keyword}    :  
            ${VCN_ID_list}    REST_Create_Card   ${USER}   ${cards_number}     POST_new_VCN_full.json    ${status}
            IF     ${cards_number} == 1 
                ${VCN_ID}    Set Variable    ${VCN_ID_list}[0]
                Set Test Variable    ${VCN_ID}
            ELSE
                Set Test Variable    ${VCN_ID_list}
            END     
        ELSE   
            Fail     Test setup error : keyword not found  
        END
    END
    IF    	${NAV_URL} != '${EMPTY}' 	 Navigate To b2bwallet Page    ${PHASE}    ${NAV_URL}
       
Test_Teardown
    [Documentation]    Actions to be performed after the test case execution
    [Arguments]    ${USER}=None    ${VCN_ID}=None    @{keywords}
    FOR    ${keyword}    IN    @{keywords}
        # Terminate the kassette process
        IF   '${keyword}' == 'kassette' 
            Terminate Process   
        # Delete the  virtual card created for the test  
        ELSE IF    '${keyword}' == 'deleteCard'  
            REST_Delete_Card    ${USER}    ${VCN_ID}
        ELSE 
            Fail     Test teardown error : keyword not found  
        END
    END

Go To b2bwallet Page
    [Documentation]    Open the checkout page
    ...    Parameters:
    ...    - url:  page url
    ...    - Tablet mode: TRUE or FALSE
    [Arguments]    ${url}    ${TABMODE}    ${PROXY}=OFF

    # Set the proxy option
    ${proxy_conf}    Set Variable If    '${PROXY}' == 'ON'    { 'server': 'localhost:8080', 'bypass': '<-loopback>' }    None
    # Set the tablet mode option
    ${tabmode_conf}    Set Variable If    '${TABMODE}' == 'TRUE'    {'width': 680, 'height': 768}    None 
    
    New Browser    chromium    headless=False    proxy=${proxy_conf}
    New Context    viewport=${tabmode_conf}    ignoreHTTPSErrors=True
    New Page    ${url}
    
    Local Storage Set Item    auth    ${Local_storage_auth}
    
Navigate To b2bwallet Page
    [Documentation]    Open the checkout page
    ...    Parameters:
    ...    - phase
    ...    - Url list
    ...    Return:
    ...    - b2b wallet page displayed
    [Arguments]    ${PHASE}    ${URL_LIST}  
    ${BaseUrl}    Get Base Url    ${PHASE}    ${URL_LIST} 
    Log    ${Local_storage_auth}
    New Page    ${BaseUrl}
    Wait Until Keyword Succeeds	     3x	     3s	     Go to    ${BaseUrl}
    Wait Until Network Is Idle

Check Get to B2B Portal
    [Documentation]    fill xpp login page password
    ...    Login in XPP
    Wait For Elements State    ${search_criteria_input_field_locator}    visible

Get Base Url
    [Documentation]    Reply the url regarding the phase entered
    [Arguments]    ${phase}    ${product}
    RETURN    ${product}[${phase}]

Go To XPP Page
    [Documentation]    Open the checkout page
    ...    Parameters:
    ...    - url: the payment page url
    ...    - Tablet mode: TRUE or FALSE
    ...    Return:
    ...    - Page displayed
    [Arguments]    ${url}    ${TABMODE}    ${PROXY}=OFF
    # Set the proxy option
    ${proxy_conf}    Set Variable If    '${PROXY}' == 'ON'    { 'server': 'localhost:8080', 'bypass': '<-loopback>' }    None
    # Set the tablet mode option
    ${tabmode_conf}    Set Variable If    '${TABMODE}' == 'TRUE'    {'width': 680, 'height': 768}    {'width': 1024, 'height': 768} 
    
    New Browser    chromium    headless=True    proxy=${proxy_conf}
    New Context    viewport=${tabmode_conf}    ignoreHTTPSErrors=True
    New Page    ${url}
    
Generate auth Token
    [Documentation]    Generate an LSS auth token to access XPP UI
    [Arguments]    ${phase}    ${USER}   

    # Generate auth token for XPP
    ${Local_storage_auth}    build authlocalStorage    ${PHASE}    ${USER}
    ${Local_storage_auth}    Replace String    ${Local_storage_auth}    '    \\"
    Set Global Variable    ${Local_storage_auth}
    Log    ${Local_storage_auth}

Fill Xpp login page user
    [Documentation]    fill xpp login page
    ...    Login in XPP
    [Arguments]    ${user}    ${organisation}
    Type Text    ${XPP_LOGIN_INPUT_USER_locator}    ${user}
    Type Text    ${XPP_LOGIN_INPUT_ORGANISATION_locator}    ${organisation}
    Take Screenshot    fullPage=True
    Click    ${XPP_LOGIN_NEXT_BUTTON_locator}
    Wait For Elements State    ${XPP_LOGIN_INPUT_PASSWORD_locator}    visible

Fill Xpp login page password
    [Documentation]    fill xpp login page password
    ...    Login in XPP
    [Arguments]    ${password}
    Type Text    ${XPP_LOGIN_INPUT_PASSWORD_locator}    ${password}
    Click    ${XPP_LOGIN_LOGIN_BUTTON_locator}
    Check Get to B2B Portal

Import Locators As Variables 
    ${json_locators}    Load JSON From File    ${JSON_LOCATORS_FILE_PATH}   
    Log    ${json_locators} 
    Convert JSON TO Variables File    ${json_locators}
    Import Variables    ${EXECDIR}/${PYTHON_LOCATORS_FILE_PATH}
    Remove File    ${EXECDIR}/${PYTHON_LOCATORS_FILE_PATH}

Convert JSON To Variables File
    [Arguments]    ${json_object}
    BuiltIn.Log    ${json_object}
    FOR   ${json_key}    ${json_value}    IN    &{json_object}
        FOR    ${key}    ${value}    IN    &{json_value}
            Append To File    ${PYTHON_LOCATORS_FILE_PATH}   ${key}="${value}"\n    
        END
    END

Check Locators From File
    [Arguments]    ${json_key}    ${excludes}=${EMPTY}
    ${json_locators}    Load JSON From File    ${JSON_LOCATORS_FILE_PATH}
    ${json_values}    Get Value From JSON    ${json_locators}    $..${json_key}
    Log Many    ${json_key}    ${json_values}    
    FOR  ${key}    ${value}    IN    &{json_values}[0]
        IF   $key in $excludes    CONTINUE 
        Get Element States    ${value}    contains    visible  
    END    

Check_key_List_Present
    [Documentation]    Takes value and list in entry and returns result TRUE or FALSE if Key entered is present
    [Arguments]    ${entry}    @{list}

    ${Result}    Set Variable     'FALSE'
    List Should Contain Value    ${list}    ${entry} 

JSON Create Body For Card Creation
    [Documentation]    Create a JSON body for card creation (based on a json template)
    ...    Parameters:
    ...    - json_template_filepath : path to the json template
    ...    - status : status of the card to create
    [Arguments]    ${json_template_filepath}    ${status}    
    ${json_template}     Load JSON From File    ${json_template_filepath}  
    ${changed_json}   ${random_reservationID}    JSON Set Custom ReservationID    ${json_template}
    ${changed_json}    JSON Set Card Status    ${changed_json}    ${status}
    Set Test Variable    ${random_reservationID}
    RETURN     ${changed_json}

JSON Set Custom ReservationID
    [Documentation]    Add a random reservationID to json
    ...    Parameters:
    ...    - json : json content to customize
    [Arguments]    ${json}       
    ${random_reservationID}	    Generate Random String    6
    ${changed_json}     Update Value To Json    ${json}    $.data.bookingInfo.reservationID    ${random_reservationID}
    RETURN   ${changed_json}    ${random_reservationID}  
    
JSON Set Card Status
    [Documentation]    Add a particular card amount to json (in order to change the status of the card)
    ...    Parameters:
    ...    - json : json content to customize
    ...    - status : status of the card to create
    [Arguments]    ${json}    ${status}        
    ${custom_value}    Set Variable If   
    ...    '${status}' == 'INACTIVE'    88.03   
    ...    '${status}' == 'DELETED'     88.04
    ...    '${status}' == 'ACTIVE'      1.00 
    ${changed_json}    Update Value To Json    ${json}    $.data.fundsTransfers.[0].amount.value    ${custom_value}
    RETURN   ${changed_json}

JSON_Delete_Data 
    [Arguments]    ${card_body_filepath}    ${json_path}    
    ${json}     Load JSON From File    ${card_body_filepath}
    ${changed_json}     Delete Object From Json    ${json}     ${json_path} 
    Log Dictionary    ${changed_json}
    ${changed_json_str}    Convert JSON To String    ${changed_json}
    Remove File    ${card_body_filepath}
    Create File    ${card_body_filepath}    ${changed_json_str} 

Get Portal Version
    New Browser    chromium    headless=True   
    New Page   ${SENTINEL_URL_LIST}[${PHASE}]
    ${portal_version}    Get Text    xpath=//td[contains(b,"VCC")]/../td[2]
    Log    ${portal_version}
    Set Suite Metadata    Environment    ${PHASE}
    Set Suite Metadata    Portal Version    ${portal_version}
    Close Browser

Translate Number Of Purchase
    [Arguments]    ${number_of_purchase} 
    ${number_of_purchase}    Convert To Integer    ${number_of_purchase}  
    ${use}    Set Variable If    
    ...    ${number_of_purchase} == 1    Single use
    ...    ${number_of_purchase} > 1    Multiple use
    [Return]    ${use}

Convert Month Name To Month Number
    [Arguments]     ${long_month_name}   
    ${datetime_object}     Evaluate     datetime.datetime.strptime("${long_month_name}" , "%B")
    ${month_number}     Set Variable     ${datetime_object.month}
    RETURN    ${month_number} 