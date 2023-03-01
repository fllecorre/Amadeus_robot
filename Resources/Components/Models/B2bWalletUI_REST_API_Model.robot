*** Settings ***
Variables    ../REST_data/REST_variables.py
Library     REST    ${REST_base_url}[${PHASE}]

*** Keywords ***
REST_Create_Token
    [Documentation]  Create a token needed for request authorization  
    [Arguments]    ${user}
    ${token}    Get 1 A Auth Token    ${user}
    Set Global Variable    ${token}   
    
    
REST_Request
    [Documentation]  Send a request to the specified endpoint (URI) 
    ...    Parameters :
    ...    - ${method} : POST, GET, PATCH or DELETE
    ...    - ${URI} : Uniform Resource Identifier
    ...    - ${body} : data to send
     [Arguments]    ${method}    ${USER}    ${URI}    ${body}=None
    REST_Create_Token    ${USER} 
    Log To Console    method = ${method}, URI =${URI}, data=${body}
    Log Many    method = ${method}    URI =${URI}    data=${body}
    #Headers preparation
    &{headers}    Create Dictionary    Authorization=1Aauth ${token}   Content-Type=application/json
    Log Dictionary    ${headers}  
    # Set Headers    ${headers} 
    #Sending request 
    IF    '${method}'=='POST'  
        ${response}    POST    ${URI}    body=${body}    headers=&{headers}
    ELSE IF    '${method}'=='GET'
        ${response}    GET   ${URI}    headers=&{headers} 
    ELSE IF    '${method}'=='PATCH'
        ${response}    PATCH   ${URI}    body=${body}    headers=&{headers}
    ELSE IF    '${method}'=='DELETE'
        ${response}    DELETE   ${URI}    headers=&{headers}
    ELSE
        Fail    method error (only POST, PATCH, GET or DELETE request accepted)
    END
    Log    ${response}
    RETURN   ${response} 
    

REST_Check_JSON_Response
    [Documentation]     Check the json response (body) matches expected values (or expected patterns if no expected value is provided)
    ...    Parameters :
    ...    - ${dict} : dictionnary containing the expected values
    [Arguments]    ${dict}=None
    ${response_body}    Object    response body   
    IF    ${dict} == None
        # Check the response matches a given pattern
        &{pattern_dict}    REST_Get_Pattern_To_Check
        FOR    ${key}    ${pattern}    IN    &{pattern_dict}
            ${value}    REST_Get_Value_From_Response_byJsonPath    $.data.[0].${key}    ${response_body}[0]
            Run Keyword And Continue On Failure    Should Match Regexp    ${value}    ${pattern}                   
        END    
    ELSE
        # Check the response matches given values
        FOR    ${key}    ${expected_value}    IN    &{dict}
            ${value}    REST_Get_Value_From_Response_byJsonPath    ${key}    ${response_body}
            Run Keyword And Continue On Failure    Should Be Equal As Strings    ${value}    ${expected_value}
        END
    END

REST_Get_Value_From_Response_byJsonPath
    [Documentation]     Retrieve a value from the json response body
    ...    Parameters :
    ...    - JsonPath : jsonPath to get value from example $.data.card.cardNumber
    ...    - response_body : response body
    [Arguments]    ${JsonPath}=None    ${response_body}=None
    Log Many    ${JsonPath}    ${response_body}    
    IF    ${response_body} == None
        ${response_body}    Object    response body
        ${response_body}    Set Variable     ${response_body}[0]
    END
    ${value}    Get Value From Json    ${response_body}     ${JsonPath}
    Log    ${value}[0]
    RETURN    ${value}[0]

REST_Get_Response_As_Dict
    ${response_body}    Object    response body
    ${response_data}    Get Value From Json    ${response_body}[0]     $.data
    Log Dictionary    ${response_data}[0]
    [Return]    ${response_data}[0]
    
REST_Check_Status_From_Response
    [Documentation]    Retrieve the status code from the response and check its value
    ...    Parameters :
    ...    - ${expected_status_code} : status code of the response
    [Arguments]    ${expected_status_code}
    ${status_code}    Integer   response status    ${expected_status_code}

REST_Get_Pattern_To_Check
    [Documentation]    Retrieve the patterns dictionary to check according the tag of the test
    ${test_tag}    Get From List    ${TEST TAGS}    0
    IF    '${test_tag}'=='pattern_card_list'
        &{pattern}    Copy Dictionary    ${pattern_card_list}
    ELSE IF    '${test_tag}'=='pattern_card_creation'
        &{pattern}    Copy Dictionary    ${pattern_card_creation}
    ELSE IF    '${test_tag}'=='pattern_account'
        &{pattern}    Copy Dictionary    ${pattern_account}
    ELSE IF    '${test_tag}'=='pattern_card'
        &{pattern}    Copy Dictionary    ${pattern_card}
    END
    RETURN   &{pattern}

REST_Create_Card
    [Documentation]    Card creation using REST 
    ...    Parameters :
    ...    - USER : credentials for token creation
    ...    - number : number of card to create  
    ...    - body_filename : filename of the json template   
    ...    - status : status of the card to create
    [Arguments]    ${USER}    ${number}   ${body_filename}    ${status}=ACTIVE     
    @{VCN_ID_list}    Create List
    ${body_template}    Set Variable    ${EXECDIR}/${bodies_path}/${body_filename}
    ${json_body}    JSON Create Body For Card Creation    ${body_template}    ${status}      
         
    FOR    ${i}    IN RANGE    1    ${number}+1
        REST_Request    POST    ${USER}    ${REST_virtual_cards_URI}    ${json_body}
        REST_Check_Status_From_Response    201
        ${vcn_id}    REST_Get_Value_From_Response_byJsonPath      $.data.id
        Append To List    ${VCN_ID_list}    ${vcn_id} 
    END 
    RETURN     ${VCN_ID_list}  

REST_Delete_Card
    [Arguments]    ${USER}    ${VCN_ID}     
    REST_Request    DELETE    ${USER}    ${REST_virtual_cards_URI}/${VCN_ID}
    REST_Check_Status_From_Response    200

REST_Delete_Cards
    [Arguments]    ${USER}    @{VCN_ID_list}    
    FOR    ${VCN_ID}    IN    @{VCN_ID_list}
        REST_Request    DELETE    ${USER}    ${REST_virtual_cards_URI}/${VCN_ID}
        REST_Check_Status_From_Response    200
    END    