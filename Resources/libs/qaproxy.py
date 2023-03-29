
from jwt_generation import authenticate,getattr
from lss_token_generator import getBearerToken,get1AAuthToken
from VCN_checkBom import validate_json_input,verifycardbom_v2
from test_users import *
import requests
import json
import logging,time, random,string
import os.path

PROXY_LOGGER =logging.getLogger(__name__)

qaproxy_base_url= "https://qaproxy.forge.amadeus.net/api/tool"

def getRandomAlphanumeric(size):
	return ''.join(choice(string.ascii_uppercase + string.digits) for _ in range(size))

def generate_token(user,pwd,phase,token_type):
    if token_type == "LSS_Bearer":
        token = getBearerToken(phase,user)
        return f"Bearer {token}"
    elif  token_type == "JWT":
        token =  authenticate(user,pwd)
        return    getattr("token",token)
    elif token_type == "LSS_1Aauth":
        token = get1AAuthToken(user)
        return f"1Aauth {token}"


def get_file_name_from_path(filepath):
    return list(filter(None,filepath.split("/")))[-1]

def get_file_destination_from_origin_path(phase,provider,filepath):
    filename = get_file_name_from_path(filepath)
    return f"//ama/obe/{phase}/aps/vcp/data/vcp/Providers/{provider.capitalize()}/Inbox/{filename}"


def get_vcn_bom(user,pwd,phase,card_id,id_type="VcnId"):
    token = generate_token(user,pwd,phase,"JWT")
    print(token)
    token = f"Bearer {token}"
    headers=  {
                'Authorization': token
            }
    if id_type == "VcnId":
        url_path = f"{qaproxy_base_url}/db/getVCNBlob/{phase}/{card_id}"
    elif id_type == "ExternalID":
        url_path = f"{qaproxy_base_url}/db/getVCNByExtID/{phase}/{card_id}"
    else:
        PROXY_LOGGER.error(f"Invalid card type input {id_type}")
        return "Invalid card type input"
    response = requests.get(url_path,headers=headers)

    if response.status_code == 200:
        return validate_json_input(response.text)
    else:
        PROXY_LOGGER.error(f"response from Proxy {response.status_code}")
        return response.status_code

def Get_files_list(user,phase,provider,folder):
    token = generate_token(user,phase,"JWT")
    token = f"Bearer {token}"
    headers=  {
                'Authorization': token
            }
    url_path = f"{qaproxy_base_url}/fs/listDirectory/{phase}//ama/obe/{phase}/aps/vcp/data/vcp/Providers/{provider}/{folder}/"
    response = requests.get(url_path,headers=headers)
    if response.status_code == 200:
        return validate_json_input(response.text)['fileList']
    else:
        PROXY_LOGGER.error(f" Error while retrieving file list from {url_path}!")
        return response.status_code

def Check_file_in_directory(user,phase,provider,folder,filename):
    files_list = Get_files_list(user,phase,provider,folder)
    if filename in files_list:
        PROXY_LOGGER.info(f" {filename}: File exists in {folder}!")
        return True
    else:
        PROXY_LOGGER.info(f" {filename}: File doesn't exist in {folder}!")
        return False

def Check_file_status(user,phase,provider,status,filename):
    counter = 10
    check = 0
    result = Check_file_in_directory(user,phase,provider,status,filename)
    while check <= counter and not result:
        time.sleep(1)
        PROXY_LOGGER.warning(f" Retry check Processed {filename} for {check} time!")
        result = Check_file_in_directory(user,phase,provider,status,filename)
        check += 1
    if not result:
        PROXY_LOGGER.error(f" {filename}: File doesn't exist in {status}!")
    return result

def get_file_content_by_path(user,phase,file_path):
    url_path =f"{qaproxy_base_url}/fs/catFile/{phase}//ama/obe/{phase}{file_path}"
    token = generate_token(user,phase,"JWT")
    token = f"Bearer {token}"
    headers=  {
                'Authorization': token
            }
    response = requests.get(url_path,headers=headers)
    if response.status_code == 200:
        try:
            response_message = json.loads(response.text)
            output_csv = []
            for line in response_message['fileContent']:
                line = line.split(",")
                output_line = [element.replace("\"","") for element in line]
                output_csv.append(output_line)
            return output_csv
        except KeyError as not_readable_content:
            PROXY_LOGGER.warning(f"Not readable file content for : {file_path} -- {not_readable_content}")
            return response.text
    else:
        PROXY_LOGGER.error(f"response from Proxy {response.status_code}")
        return response.status_code


def add_import_file_to_folder(user,phase,provider,file_name,file_content,temp_folder=True):
    if temp_folder:
        tmp_folder_name =f"tmp/tmp.0751ZhHHNS"
        file_path = f"/{tmp_folder_name}/Inbox/{file_name}"
    else:
        file_path = f"/ama/obe/{phase}/aps/vcp/data/vcp/Providers/{provider}/Inbox/{file_name}"
    url_path =f"{qaproxy_base_url}/fs/createFile/{phase}/{file_path}"
    token = generate_token(user,phase,"JWT")
    token = f"Bearer {token}"
    headers=  {
                'Authorization': token
            }
    response = requests.get(url_path,headers=headers)
    if response.status_code == 200:
        PROXY_LOGGER.info(f"File {file_name} correctly created in directory {file_path}!")
        print(f"file_path : {file_path}")
        if add_content_to_file(user,phase,file_path,file_content) == 200:
            return file_path
    else:
        PROXY_LOGGER.error(f" Error while adding {file_name} to directory {file_path}!")
        return response.status_code


def add_content_to_file(user,phase,filepath,file_content):
    url_path = f"{qaproxy_base_url}/fs/addContentToFile/{phase}/{filepath}/"
    print(url_path)
    token = generate_token(user,phase,"JWT")
    token = f"Bearer {token}"
    headers=  {
                "Content-Type": "application/json",
                "Authorization": token
            }
    body={ "content":file_content}
    response = requests.post(url_path, data=json.dumps(body), headers=headers, timeout=15 )
    if response.status_code == 200:
        PROXY_LOGGER.info(f"File content correctly added to file {filepath}!")
        return response.status_code
    else:
        PROXY_LOGGER.error(f" Error while adding content to file {filepath}!")
        return response.status_code

def check_card_bom(user,phase,vcnid,expected_bom,ignored_key_list=[]):
    received_bom =get_vcn_bom(user,phase,vcnid,id_type="VcnId")
    print(received_bom[-1])
    if received_bom[-1] != "}":
        received_bom = received_bom + "}"
    return verifycardbom_v2(received_bom,expected_bom,ignored_key_list)

# if __name__ == "__main__":
#     print(get_vcn_bom(MYUSER,"DEV","CA_6M_100.22_EUR_16729369916",id_type="ExternalID"))
#     print(Get_files_list(MYUSER,"DEV","Ixaris","Rejected"))
#     print(Check_file_in_directory(MYUSER,"DEV","Ixaris","Rejected","Funding_Account_Activity_20230105.160433_QA.csv"))
#     print(Check_file_status(MYUSER,"DEV","Ixaris","Processed","Card_Activity_20221208.113659_QA.csv"))
#     print(Check_file_status(MYUSER,"DEV","Ixaris","Processed","Card_Activity_ixaris_20230113_205242_QA.csv"))
#     print(get_file_content_by_path(MYUSER,"DEV","/aps/vcp/data/vcp/Providers/Ixaris/Processed/Card_Activity_20221205.034542_QA.csv/"))
#     print(add_import_file_to_folder(MYUSER,"DEV","Ixaris","Card_Activity_ixaris_20230106_194146_QA.csv"))
#     file_content = """"startDate","transactionDate","community","client","country","transactionID","adjustmentID","transactionType","transactionCurrency","transactionAmount","transactionAuthor","sourceType","sourceDetails","destinationType","destinationDetails","participantType","participantDetails","participantSink","originalCurrency","originalAmount","participantCurrency","participantAmount","exchangeRate","nonForexFee","forexFee","balanceBefore","balanceAdjustment","balanceAfter","status","forexFlag","direction","externalRef","transactionInfo"
#         "2023-01-13 13:49:59.910","2023-01-13 13:49:59.911","Amadeus","amamadeus#amamadeus","FRANCE","0RABAc4dn_b34x6ncdRWbniIN","ADJID_20230113134959_IVXN7","CARD CREATED","EUR","1.0","test.regression","Funding Account","EUR","Virtual Card","1.00","Funding Account","EUR","SOURCE","EUR","-1.0","EUR","-1.0","1.000000000","0.000000000","0.000000000","100000","-1.0","99999","COMPLETED","N","A","FANumber_Test",""
#         "2023-01-13 13:50:00.980","2023-01-13 13:50:00.981","Amadeus","amamadeus#amamadeus","FRANCE","TRNID_20230113135000_W20GL","ADJID_20230113135000_SC8EW","TRANSFER","EUR","1.0","test.regression","Virtual Card","1.00","Funding Account","EUR","Funding Account","EUR","DESTINATION","EUR","1.0","EUR","1.0","1.000000000","0.000000000","0.000000000","99999","1.0","100000","COMPLETED","N","A","FANumber_Test",""
#         "2023-01-13 13:50:01.990","2023-01-13 13:50:01.991","Amadeus","amamadeus#amamadeus",""FRANCE","TRNID_20230113135001_HKXHM","ADJID_20230113135001_2AHMT","TRANSFER","EUR","-2.0","test.regression","Funding Account","EUR","Virtual Card","1.00","Funding Account","EUR","SOURCE","EUR","--2.0","EUR","--2.0","1.000000000","0.000000000","0.000000000","99999","--2.0","100000","COMPLETED","N","A","FANumber_Test","""""
#     user,phase,provider,file_name,file_content,temp_folder=True
#     print(add_import_file_to_folder(MYUSER,"DEV","Ixaris","Funding_Account_Activity_ixaris_20230106_180747_QA_Test_11.csv",file_content,temp_folder=True))
#     print(add_content_to_file(MYUSER,"DEV","/tmp/tmp.0751ZhHHNS/Inbox/Funding_Account_Activity_ixaris_20230106_180747_QA_Test2.csv/",file_content))
