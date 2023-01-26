import requests
from lss_token_generator import get1AAuthToken
from test_users import APPUI1A01

REST_base_url = {
    "DEV":"http://172.17.237.47:21298/1ASIUPAYD",
    "PDT":"http://172.17.237.12:25012/1ASIUPAY",
    "UAT":"http://172.17.237.12:25012/1ASIUPAYU",
    "FVT":"http://172.17.237.12:25012/1ASIUPAYF",
}



def get_card_list(phase,user,params):
    url = f"{REST_base_url[phase]}/payment/v1/virtualCards?"
    for element in params.items():
        url += f"{element[0]}={element[1]}&"
    url = url[:-1]
    print(url)

    token = get1AAuthToken(user)
    headers = {
                "Authorization": f"1Aauth {token}",
                "Content-Type":"application/vnd.amadeus+json",
                "Accept":"application/vnd.amadeus+json,text/html"
               }
    response = requests.get(url,headers=headers)
    return str(response.status_code)





if __name__ == "__main__":
    params = {
        "state":"CA",
        "creationBeginDate":"2023-01-02",
        "creationEndDate":"2023-01-03"
    }
    print(get_card_list("UAT",APPUI1A01,params))