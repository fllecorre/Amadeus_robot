*** Settings ***
Library    Collections
Library    JSONLibrary
Library     ../../../Resources/libs/Import_file_libs/VCN_report_generator.py


*** Keywords ***
Generate import file content
    [Arguments]    ${Provider}    ${Transaction_list}    ${Card_information}     
    Log        ${Provider}
    Log        ${Transaction_list}
    Log        ${Card_information} 
    @{Report_Output}    generate_import_file    ${Provider}    transaction_list=${Transaction_list}    card_information=${Card_information}
    FOR  ${Element}    IN     @{Report_Output} 
        Log      ${Element} 
    END
    RETURN    ${Report_Output}

Clean Import File Storage 
    Clean_import_file_dir    
