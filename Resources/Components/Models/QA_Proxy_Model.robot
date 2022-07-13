*** Settings ***
Library    Collections
Library    JSONLibrary
Library           ../../../Resources/libs/lss_token_generator.py 
Library         ../../../Resources/libs/Import_file_libs/VCN_checkimport.py  
Resource    REST_API_Model.robot
Variables       ../../../Resources/libs/test_users.py

*** Variables ***
${qaproxy_base_url}    https://qaproxy.forge.amadeus.net/api   
${l_file_provider_path}    /ama/obe/${PHASE}/aps/vcp/data/vcp/Providers/${provider}

*** Keywords ***
Get VCN BOM
    [Arguments]    ${USER}    ${PHASE}    ${VCN_ID}        
    ${json_response}    REST_Request    GET    ${USER}    JWT    ${qaproxy_base_url}/tool/db/getVCNBlob/${PHASE}/${VCN_ID}
    REST_Check_Status_From_Response    200
    RETURN    ${json_response}[body]

Get File Content
    [Arguments]    ${USER}    ${PHASE}    ${directory}    ${filename} 
    ${file_content}    REST_Request    GET    ${USER}    JWT     ${qaproxy_base_url}/tool/fs/catFile/${PHASE}/${l_file_provider_path}/${directory}/${filename} 
    RETURN    ${file_content} 

Check File Location
    [Arguments]    ${USER}    ${PHASE}    ${directory}    ${filename} 
    ${files_list}     REST_Request    GET    ${USER}    JWT    ${qaproxy_base_url}/tool/fs/listDirectory/${PHASE}/${l_file_provider_path}/${directory} 
    IF    ${filename} in ${files_list}
        ${file_content}    Get_File_Content    ${USER}    ${PHASE}    ${directory}     ${filename}
        ${length}    Get Length      ${file_content}    
        IF    ${length} == 0    Fail    File is empty!    ELSE    RETURN    File found !
    END
    

