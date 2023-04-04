*** Settings ***
Library        cyberarklib
Library        ../resources/libs/qaproxy.py


*** Variables ***
${PHASE}    DEV
${cert_filepath}
${key_filepath}

*** Test Cases ***
Get Password From Cyberark With OS User Authentication
    [Tags]    windows
    ${password}    Get Password And Conceal   safe=APS-B2B-D    appID_OS=APS-B2B-OS-D    cyb_object=WIN_account
    Log      ${password}
    ${bom}    Get Vcn Bom    flecorre    ${password}    ${PHASE}    2222JNV3
    Log    ${bom}

Get Password From Cyberark With Certificate Authentication
    ${password}    Get Password And Conceal   safe=APS-B2B-D    appID_CERT=APS-B2B-APP-D    cyb_object=WIN_account    cert_file=${cert_filepath}   key_file=${key_filepath}
    Log      ${password}
    ${bom}    Get Vcn Bom    flecorre    ${password}    ${PHASE}    2222JNV3
    Log    ${bom}
