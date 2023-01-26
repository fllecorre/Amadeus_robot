"""
        CHECK VCN CARD BOM LIBRARY
         The goal of this library is to check an expected json with a received json for b2b wallet Card bom
         The function VerifyCardBom_v2 is to be called to use the library with the parameters
                    - bom_expected : data dict
                    - bom_received : string containing json coming from QA Proxy
                    - ignore_keys : list of keys and paths with to be ignored while the check is performed
"""
import json
import logging



VCN_LOGGER = logging.getLogger(__name__)
class Bom:
    def __init__(self, expected_bom: dict, received_bom : dict, keys_to_ignore=None):
        self.expected_bom = expected_bom
        self.received_bom = received_bom
        self.keys_to_ignore = keys_to_ignore
        if keys_to_ignore is None:
            self.keys_to_ignore = []
    def  __repr__(self) -> str:
        return f"expected BOM: {self.expected_bom} \n received BOM: {self.received_bom}"

    def ignore_checks(self,input_key):
        """Checks if the key or path input is contained in the list of keys/paths to be ignored
        Args:
            input_key (list): list of paths/keys

        Returns:
            boolean: returns True if the input key is in the list or False
        """
        for element in self.keys_to_ignore:
            if element in input_key:
                VCN_LOGGER.info(f"{input_key} => Value check ignored")
                return True
        return False

    def check_bom(self):
        """Check Bom content to validate expected bom values with received bom
        Returns:
            _type_: Boolean
        """
        dict_expected = flatten_json(self.expected_bom)
        dict_received = flatten_json(self.received_bom)
        check_result = True
        for key in dict_expected.keys():
            try:
                if (dict_expected[key] != dict_received[key]):
                    if dict_expected[key] == "*" or self.ignore_checks(key):
                        VCN_LOGGER.warning("%s == True => %s => Value check ignored",key,dict_expected[key])
                    elif "TransactionDateTime" in key and check_timestamp(dict_expected[key],dict_received[key]):
                        VCN_LOGGER.info("%s == True => %s",key,dict_expected[key])
                    else:
                        check_result = False
                        VCN_LOGGER.error("%s == False : bom_expected : %s, bom_received : %s",key,dict_expected[key],dict_received[key])
                else:
                    VCN_LOGGER.info("%s == True => %s",key,dict_expected[key])
            except KeyError as error:
                if self.ignore_checks(key):
                    VCN_LOGGER.warning("%s: Key check ignored == True",key)
                else:
                    VCN_LOGGER.error("%s:%s missing in received Bom",error,key)
                    check_result = False
        VCN_LOGGER.warning("final check bom result : %s",check_result)
        return check_result

def validate_json_input(json_input):
    """This function converts:
    - QA proxy getVCNBlob to a valid dict
    - A json to python dict
    Args:
        json_input (str): QA proxy json string value, or json

    Returns:
        _type_: Valid dict object
    """
    if not isinstance(json_input,dict):
        try:
            formatted_json = json_input.replace('\{','{').replace('\}','}').replace('\%','%')
            formatted_json = json.loads(formatted_json)
            VCN_LOGGER.info("formatted to json %s",type(formatted_json))
            return formatted_json
        except Exception as json_exception:
            VCN_LOGGER.error("%s -> Invalid json",json_exception)
            raise("Invalid Json")
    else:
        VCN_LOGGER.info("is json dict by default %s",json_input)
        return json_input


def check_timestamp(expected_date, received_date):
    """Transform Timestamp into Date Hour Minute format and compare dates
    Args:
        expected_date (str): Expected date
        received_date (str): Received date

    Returns:
        Bool: Comparison result
    """
    result= False
    try:
        expected_date = str(expected_date[0:16])
        received_date = str(received_date[0:16])

    except Exception as timestamp_exception:
        VCN_LOGGER.error("%s :Invalid date format",timestamp_exception)
        return result

    if expected_date == received_date:
        result= True
        return result
    return result


def build_flatten_list_element(list_element,initial_path,current_key,current_dict):
    """Parse an element of the current dict from an initial path,
        Create a flatten version with unique paths
        if transactionID present key is generated based on it, if not an index is added
    Args:
        current_dict (dict): current data dict to parse
        list_element (list): list element of the current dict
        initial_path (str): path to list
        current_key (str): key of the list
    """
    index= 0
    for item in list_element:
        try:
            current_path = initial_path + [f"{current_key}_{item['ExternalTransactionId']}"]
        except KeyError as transactionid_exception:
            VCN_LOGGER.info("%s: No TransactionID value for %s",transactionid_exception,item)
            current_path = initial_path + [f"{current_key}_{str(index)}"]
            index += 1
        current_dict.update(flatten_json(item, current_path))

def flatten_json(bom, path=[], separator="."):
    """Converts json dict to a flat dict using sub-branches keys by create a unique key
    Args:
        bom (dict): Json bom content
        path (list, optional): JsonPath if specified, defaulted to []
        separator (str, optional): Keys separator string. Defaults to "."

    Returns:
        dict: Flat Json dict with unique keys
    """
    result = {}
    for key, value in list(bom.items()):
        current_path = path + [key]
        if isinstance(value, dict):
            result.update(flatten_json(value, current_path))
        elif isinstance(value, list):
            build_flatten_list_element(value,path,key,result)
        else:
            result[separator.join(current_path)] = value
    return result


def verifycardbom_v2(bom_received,bom_expected,ignore_keys=[]):
    """ Check bom function using new library
    Args:
        bom_received (str): received bom
        bom_Expected (str): expected bom
        exact_match (bool, optional): Exact match of key,value. Defaults to False.

    Returns:
        _type_: TTS result (1: False, 0: True)
    """
    bom = Bom(validate_json_input(bom_expected),validate_json_input(bom_received),ignore_keys)
    if not isinstance(ignore_keys,list):
        raise f"Invalid input ignore_keys {type(ignore_keys)}, Please enter a list"
    result = bom.check_bom()
    if result:
        return 0
    return 1