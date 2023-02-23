*** Settings ***  
Library    Collections
Library    JSONLibrary
Library     REST 
Library    ../resources/lss_token_generator.py
Variables   ../resources/B2BWallet_REST_API_conf.py    


*** Keywords ***
REST_Create_Token
    [Documentation]  Create a token needed for request authorization  
    ...    Parameters :
    ...    - user : dictionary containing credentials information
    ...    Return value :
    ...    - token 
    [Arguments]    ${user}
    ${token}    Get 1 A Auth Token    ${user}
    RETURN    ${token}   
    
    
REST_Request
    [Documentation]  Send a request to the specified endpoint (URI) 
    ...    Parameters :
    ...    - phase : enironment
    ...    - method : POST, GET, PATCH or DELETE
    ...    - USER : dictionary containing credentials information
    ...    - URI : Uniform Resource Identifier
    ...    - body : data to send
    ...    Return value :
    ...    - response : response from the API endpoint targeted 
     [Arguments]    ${phase}    ${method}    ${USER}    ${URI}    ${body}=None
    ${token}    REST_Create_Token    ${USER} 
    Log To Console    method = ${method}, URI =${URI}, data=${body}
    Log Many    method = ${method}    URI =${REST_base_url}[${phase}]/${URI}    data=${body}
    #Headers preparation
    &{headers}    Create Dictionary    Authorization=1Aauth ${token}   Content-Type=application/json
    Log Dictionary    ${headers}  
    # Set Headers    ${headers} 
    #Sending request 
    IF    '${method}'=='POST'  
        ${response}    POST    ${REST_base_url}[${phase}]/${URI}    body=${body}    headers=&{headers}
    ELSE IF    '${method}'=='GET'
        ${response}    GET   ${REST_base_url}[${phase}]/${URI}   headers=&{headers} 
    ELSE IF    '${method}'=='PATCH'
        ${response}    PATCH   ${REST_base_url}[${phase}]/${URI}    body=${body}    headers=&{headers}
    ELSE IF    '${method}'=='DELETE'
        ${response}    DELETE   ${REST_base_url}[${phase}]/${URI}    headers=&{headers}
    ELSE
        Fail    method error (only POST, PATCH, GET or DELETE request accepted)
    END
    Log    ${response}
    RETURN   ${response} 
    

REST_Get_Value_From_Response_byJsonPath
    [Documentation]     Retrieve a value from the json response body
    ...    Parameters :
    ...    - json_path : json path to get value from example $.data.card.cardNumber
    ...    - response_body : response body
    ...    Return value :
    ...    - value : first value of the returned array
    [Arguments]    ${json_path}=None    ${response_body}=None
    Log Many    ${json_path}    ${response_body}    
    IF    ${response_body} == None
        ${response_body}    Object    response body
        ${response_body}    Set Variable     ${response_body}[0]
    END
    ${value}    Get Value From Json    ${response_body}     ${json_path}
    Log    ${value}[0]
    RETURN    ${value}[0]
 
REST_Check_Status_From_Response
    [Documentation]    Retrieve the status code from the response and check its value
    ...    Parameters :
    ...    - ${expected_status_code} : status code of the response
    [Arguments]    ${expected_status_code}
    ${status_code}    Integer   response status    ${expected_status_code}

REST_Create_Card
    [Documentation]     Create a VCN card using REST API
    ...    Parameters :
    ...    - phase : environment
    ...    - USER : dictionary containing credentials information
    ...    - json_filename : json file containing data for the card creation
    ...    - setup : True/False (to be set to True if this keyword is used for as a test set up)
    ...    Return value :
    ...    - vcn_id : id of the created card
    [Arguments]    ${phase}    ${USER}    ${json_filename}    ${setup}=${False}     
    REST_Request    ${phase}    POST    ${USER}    ${REST_virtual_cards_URI}    ${EXECDIR}/${data_path}/${json_filename} 
    REST_Check_Status_From_Response    201
    ${vcn_id}    REST_Get_Value_From_Response_byJsonPath      data.id
    IF  ${setup} == ${True}    Set Test Variable    ${vcn_id}    ELSE    RETURN    ${vcn_id}

REST_Update_Card
    [Documentation]     Update a VCN card using REST API
    ...    Parameters :
    ...    - phase : environment
    ...    - USER : dictionary containing credentials information
    ...    - VCN_ID : id of the card to update
    ...    - json_filename : json file containing data for the card update
    [Arguments]    ${phase}    ${USER}    ${VCN_ID}     ${json_filename}     
    REST_Request    ${phase}    PATCH    ${USER}    ${REST_virtual_cards_URI}/${VCN_ID}    ${EXECDIR}/${data_path}/${json_filename} 
    REST_Check_Status_From_Response    200 


