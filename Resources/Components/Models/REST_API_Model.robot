*** Settings ***
Library    Collections
Library    JSONLibrary
Variables   ../REST_data/REST_variables.py 
Library     ../../../Resources/libs/lss_token_generator.py
Library     ../../../Resources/libs/jwt_generation.py
Library     REST
Library     DebugLibrary    
Library    ../../libs/jwt_generation.py

*** Keywords ***
REST_Create_Token
    [Documentation]  Create a token needed for request authorization  
    [Arguments]    ${user}
    ${token}    Get 1 A Auth Token    ${user}
    Set Global Variable    ${token} 

REST_Create_JWT_Token
    [Documentation]  Create a token needed for request authorization  orga, officeId, userId, password
    [Arguments]    ${user}
    Log Dictionary    ${user}
    ${jwt}    jwt_generation.authenticate    ${user}[user]    ${user}[pwd]
    ${token}    jwt_generation.getattr    token    ${jwt}
    RETURN    ${token} 

REST_Request
    [Documentation]  Send a request to the specified endpoint (URI) 
    ...    Parameters :
    ...    - ${method} : POST, GET, PATCH or DELETE
    ...    - ${USER}
    ...    - ${URI} : Uniform Resource Identifier
    ...    - ${body} : data to send
     [Arguments]    ${method}    ${USER}    ${URI}    ${body}=None
    ${token}    REST_Create_JWT_Token    ${USER} 
    Log To Console    method = ${method}, URI =${URI}, data=${body}
    Log Many    method = ${method}    URI =${URI}    data=${body}
    #Headers preparation
    &{headers}    Create Dictionary    Authorization=Bearer ${token}   Content-Type=application/json
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

REST_Check_Status_From_Response
    [Documentation]    Retrieve the status code from the response and check its value
    ...    Parameters :
    ...    - ${expected_status_code} : status code of the response
    [Arguments]    ${expected_status_code}
    ${status_code}    Integer   response status    ${expected_status_code}

REST_Get_Value_From_Response_byJsonPath
    [Documentation]     Retrieve a value from the json response body
    ...    Parameters :
    ...    - ${JsonPath} : jsonPath to get value from example $.data.card.cardNumber
    ...    - ${response_body} : response body
    [Arguments]    ${JsonPath}=None    ${response_body}=None    
    IF    ${response_body} == None
        ${response_body}    Object    response body
    END
    ${value}    Get Value From Json    ${response_body}[0]     ${JsonPath}
    Log    ${value}[0]
    RETURN    ${value}[0]

REST_Create_Card
    [Arguments]    ${USER}    ${body_filename}   
    REST_Request    POST    ${USER}    ${REST_virtual_cards_URI}    ${EXECDIR}/${bodies_path}/${body_filename}
    REST_Check_Status_From_Response    201
    ${vcn_id}    REST_Get_Value_From_Response_byJsonPath      $.data.id
    RETURN    ${vcn_id}

REST_Get_Card_Info
    [Arguments]    ${USER}    ${VCN_ID}   
    REST_Request    GET    ${USER}    ${REST_virtual_cards_URI}/${VCN_ID}    
    REST_Check_Status_From_Response    200
    ${response}    REST_Get_Value_From_Response_byJsonPath      $.data
    RETURN    ${response}