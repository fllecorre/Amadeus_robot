*** Settings ***
Resource        ../Resources/Components/Models/REST_API_Model.robot
Resource        ../Resources/Components/Models/QA_Proxy_Model.robot
Resource        ../Resources/Components/Models/XPP_Report_Model.robot
Resource        ../Resources/Components/Models/Import_file_Model.robot


*** Variables ***
${PHASE}    DEV
${USER}    ${APPUI1A01}
${QA_PROXY_USER}    ${MY_USER}      
${provider}    IXARIS 

*** Test Cases ***
#Card Creation
01_Card_Creation
    ${vcn_id}    REST_Create_Card   ${USER}    POST_new_VCN_full.json
    ${card_info_dict}    REST_Get_Card_Info   ${USER}     ${vcn_id}     
    Log    ${card_info_dict}

#Get & Check BOM (to rework)
02_GetCardBOM
    ${vcn_id}    REST_Create_Card   ${USER}    POST_new_VCN_full.json
    ${expected_bom_str}    Set Variable   {"Provider": "IXARIS", "MaxNumberOfAuthors": 1, "StaticCardInformation": {"PAN": "554756XXXXXX1566", "Type": "CREDIT", "Vendor": "CA"}}  
    Check BOM    ${QA_PROXY_USER}    ${PHASE}    ${vcn_id}    ${expected_bom_str}
    
        
#Create Report
03_Generate_Import_file_IXARIS   
    ${vcn_id}    REST_Create_Card   ${USER}    POST_new_VCN_full.json
    ${card_info_dict}    REST_Get_Card_Info   ${USER}     ${vcn_id}     
    @{card_info_list}    Create List    ${card_info_dict}[vcn_trid]    ${card_info_dict}[currency]    ${card_info_dict}[amount]    ${card_info_dict}[currency]    ${card_info_dict}[amount]
    ...    ${card_info_dict}[vcn_ext_id]    ${vcn_id}     ${card_info_dict}[card_number_start]    ${card_info_dict}[card_number_end]    ${card_info_dict}[vendor_code]    
    ...    ${card_info_dict}[limitation]    ${EMPTY}    ${EMPTY}    ${EMPTY}    ${EMPTY}    ${EMPTY}    ${EMPTY}
     
    ${report}    Generate import file content    ${provider}    ${transaction_list}    ${card_info_list}
    Log Many     FundingAccountReport_filename=${report}[0]    CardActivityReport_filename=${report}[1]    BOM_expected=${report}[2]      
    [Teardown]    Clean Import File Storage

#Move report to Inbox

#File Clean up

#AppEvent Generation (CAPLAQ)

 
05_XPP_Reporting_e2e
    # 1. Card Creation
    ${vcn_id}    REST_Create_Card   ${USER}    POST_new_VCN_full.json
    ${card_info_dict}    REST_Get_Card_Info   ${USER}     ${vcn_id}     
    @{card_info_list}    Create List    ${card_info_dict}[vcn_trid]    ${card_info_dict}[currency]    ${card_info_dict}[amount]    ${card_info_dict}[currency]    ${card_info_dict}[amount]
    ...    ${card_info_dict}[vcn_ext_id]    ${vcn_id}     ${card_info_dict}[card_number_start]    ${card_info_dict}[card_number_end]    ${card_info_dict}[vendor_code]    
    ...    ${card_info_dict}[limitation]    ${EMPTY}    ${EMPTY}    ${EMPTY}    ${EMPTY}    ${EMPTY}    ${EMPTY}
   
    # 2. Report Creation
    ${report}    Generate import file content    ${provider}    ${transaction_list}    ${card_info_list} 
    Log Many     FundingAccountReport_filename=${report}[0]    CardActivityReport_filename=${report}[1]    BOM_expected=${report}[2]
    ${BOM_expected}    Set Variable    ${report}[2]
    
    #TO DO : Processing Report (Move report to Inbox,...)

    # 4. Check BOM
    ${expected_bom_str}    Set Variable   {"Provider": "IXARIS", "MaxNumberOfAuthors": 1, "StaticCardInformation": {"PAN": "554756XXXXXX1566", "Type": "CREDIT", "Vendor": "CA"}}  
    Check BOM    ${QA_PROXY_USER}    ${PHASE}    ${vcn_id}    ${expected_bom_str}
   
    #TO DO: 5. AppEvent Generation (CAPLAQ)

    # 6. XPP Reporting
    @{filter_args_list}    Create List    ${card_info_dict}[vcn_trid]
    ${report}    ${configuration}    Generate XPP Report    ${USER}    ${PHASE}    ${filter_args_list}   
    ${transactions_list}    Get Transactions From Expected BOM    ${BOM_expected}
    ${expected_values_list}    Get Expected Values From Transactions    ${transactions_list}    ${snapshot_fields}    ${card_info_dict}    
    Check XPP Report    ${report}    ${snapshot_fields}    ${expected_values_list}
    
    # 7. Clean up (TO DO : Add File Clean up to teardown)
    [Teardown]    XPP_Report_Cleaning    ${USER}    ${PHASE}    ${configuration} 



    
