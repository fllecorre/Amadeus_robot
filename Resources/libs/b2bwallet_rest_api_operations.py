import requests
from jsonpath_ng import ext
from lss_token_generator import get1AAuthToken
from datetime import *
from test_users import APPUI1A01
import logging

my_logger = logging.getLogger(__name__)

def get_time_frames():
    """
    Divides the range [one_month_ago, one_week_ago] in several time frames of 1 hour size 
    and returns all of them as a list 
    """
    today = datetime.today()
    one_week_ago = today - timedelta(days=7)
    one_month_ago = today - timedelta(days=30)
    delta = timedelta(hours=1)
    time_frames_number = int((one_week_ago - one_month_ago)/delta)
    time_frames = []
    time_frame = one_month_ago
    for x in range(time_frames_number):
        time_frames.append(time_frame.strftime("%Y-%m-%dT%H-%M-%S"))
        time_frame = time_frame + delta
    return time_frames

def get_ids_from_card_list(providers, card_list):
    """
    Based on the received providers, extracts all the ids of the cards present in the card_list
    and returns all of them as a list
    """
    ids = []
    for provider in providers:
        jsonpath_expression = ext.parse(f'$.data[?(@[:].provider=={provider})].id')
        for match in jsonpath_expression.find(card_list):
            my_logger.info(f'card_id: {match.value}')
            ids.append(match.value)
    return ids

def get_card_list(url, user, time_frame,status=None):
    """
    Performs the GET /virtualCards?creationBeginDate={Date&Time}&creationEndDate={Date&Time} for the given time_frame
    and returns the status_code and the cards list as a json
    """
    token = get1AAuthToken(user)
    headers = {
        "Authorization": f"1Aauth {token}",
        "Content-Type":"application/vnd.amadeus+json",
        "Accept":"application/vnd.amadeus+json,text/html"
    }
    tmp_time_frame = datetime.strptime(time_frame, "%Y-%m-%dT%H-%M-%S")
    next_time_frame = (tmp_time_frame + timedelta(hours=1)).strftime("%Y-%m-%dT%H-%M-%S")
    url += '?creationBeginDate=' + time_frame + '&creationEndDate=' + next_time_frame
    if status:
        url += f"&state={status}"

    response = requests.get(url,headers=headers)
    print(response.text)
    return response.status_code, response.json()

def delete_cards(url, user, ids):
    """
    Performs the DELETE /virtualCards/{vcnId} for all the ids received
    and returns a list of tuple.
    Each tuple is composed by:
        - status_code of the call
        - text of the response (empty if the status_code is 200, with an error message differently)
        - id of the processed card
    """
    responses = []
    for id in ids:
        token = get1AAuthToken(user)
        headers = {
            "Authorization": f"1Aauth {token}",
            "Content-Type":"application/vnd.amadeus+json",
            "Accept":"application/vnd.amadeus+json,text/html"
        }
        response = requests.delete(url + '/' + id, headers=headers)
        responses.append((response.status_code, response.text, id))
    return responses

def check_deleted_cards_status(cards_list):
    """
    Checks the status code of the deleted cards list received.
    The status code should be:
        - 200 in case the processed card was well deleted
        - 500 in case the processed card was already deleted (this does not cause a fail)
    """
    deleted_cards = []
    for card in cards_list:
        if (card[0] != 200) and (card[0] != 500):
            my_logger.warning(f'the card: {card[2]} had some problem. Please check its status code')
        else:
            deleted_cards.append(card)
    return deleted_cards


def append(deleted_list, deleted_cards):
    for x in deleted_cards:
        deleted_list.append(x)
    return(deleted_list)

def interpret_report(report):
    processed_cards= len(report)
    not_deleted_card = []
    deleted_cards = 0
    for card in report: 
        if card[0]==200:
            deleted_cards +=1
        else:
            not_deleted_card.append(card)
    deletion_rate = round((deleted_cards/(processed_cards+0.0001))*100,2)
    return f"{deletion_rate}% deleted cards, Deletion errors: {not_deleted_card}"
    
if __name__ == "__main__":
    report = [(200, '', '2222IJ38'), (200, '', '2222IJ2Q'), (200, '', '2222IJ2P'), (200, '', '2222IJ2B'), (200, '', '2222IJ2A'), (200, '', '2222IJ29'), (200, '', '2222IJ28'), (200, '', '2222IJ27'), (200, '', '2222IJ26'), (200, '', '2222IJ25'), 
(200, '', '2222IJ24'), (200, '', '2222IJ23'), (200, '', '2222IJ22'), (200, '', '2222IIZZ'), (200, '', '2222IIZY'), (200, '', '2222IIZX'), (200, '', '2222IIZW'), (200, '', '2222IIZV'), (200, '', '2222IIZU'), (200, '', '2222IIZT'), (200, '', 
'2222IIZS'), (200, '', '2222IIZR'), (200, '', '2222IIZQ'), (200, '', '2222IIZP'), (200, '', '2222IIZO'), (200, '', '2222IIZN'), (200, '', '2222IIZM'), (200, '', '2222IIZL'), (200, '', '2222IIZK'), (200, '', '2222IIZJ'), (200, '', '2222IIZI'), (200, '', '2222IJ9P'), (200, '', '2222IJDD'), (200, '', '2222IJDC'), (200, '', '2222IJDB'), (200, '', '2222IJCV'), (200, '', '2222IJCT'), (200, '', '2222IJCP'), (200, '', '2222IJCM'), (200, '', '2222IJCL'), (200, '', '2222IJCE'), (200, '', '2222IJCC'), (200, '', '2222IJCB'), (200, '', '2222IJC7'), (200, '', '2222IJBS'), (200, '', '2222IJAD'), (200, '', '2222IJG8'), (200, '', '2222IJG7'), (200, 
'', '2222IJG6'), (200, '', '2222IJG5'), (200, '', '2222IJG2'), (500, '', '2222IJFS'),(400, 'because I want to', '2222IJFS'), (200, '', '2222IJFR'), (200, '', '2222IJFP'), (200, '', '2222IJFO'), (200, '', '2222IJFM'), (200, '', '2222IJGG'), (200, '', '2222IJGF'), (200, '', '2222IJGE'), (200, '', '2222IJPN'), (200, '', '2222IJPM')]
    print(interpret_report(report))