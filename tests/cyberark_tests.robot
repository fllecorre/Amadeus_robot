*** Settings ***
Library        cyberarklib
Library        ../resources/libs/qaproxy.py

*** Test Cases ***
Get Password From Cyberark With OS User Authentication
    ${password}    Get Password And Conceal   safe=APS-B2B-D    appID=APS-B2B-OS-D    cyb_object=WIN_account
    Log      ${password}
    ${bom}    Get Vcn Bom    flecorre    ${password}    DEV    2222JNV3
    Log    ${bom}


Get Password From Cyberark With Certificate Authentication
    ${password}    Get Password And Conceal   safe=APS-B2B-D    appID=APS-B2B-OS-D    cyb_object=WIN_account
    ${bom}    Get Vcn Bom    flecorre    ${password}    DEV    2222JNV3
    Log    ${bom}