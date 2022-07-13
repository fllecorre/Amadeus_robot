*** Settings ***
Resource        ../Resources/Components/Models/Import_file_Model.robot
Test Teardown   Clean Import File Storage

*** Variables ***
@{Transaction_list}=   CARD CREATED    AUTHORISATION_OK     FREEZE    PURCHASE    CARD DELETED 
@{Card_information}=   0RABAc4dn_b34x6ncdRWbniIN	EUR	1.00	EUR	1.00	0RAArEjtTbX57KYibgAPhHu_9	22224WAF	522093	9372	CA	1	${EMPTY}	${EMPTY}	 ${EMPTY}	${EMPTY}	${EMPTY}	${EMPTY}
${Provider}    IXARIS

@{Transaction_list_2}=   CITI_C    CITI_C
@{Card_information_2}=   ${EMPTY}	    EUR	    1.00	EUR	    1.00	${EMPTY}	${EMPTY}	9999992222221111	${EMPTY}	${EMPTY}	 ${EMPTY}	${EMPTY}	${EMPTY}	${EMPTY}    ${EMPTY}	${EMPTY}
${Provider_2}    CITIBANK


*** Test Cases ***

01_Generate_Import_file_IXARIS    
    ${Report}    Generate import file content    ${Provider}    ${Transaction_list}    ${Card_information}    

02_Generate_Import_file_CITIBANK    
    ${Report}    Generate import file content    ${Provider_2}    ${Transaction_list_2}    ${Card_information_2}