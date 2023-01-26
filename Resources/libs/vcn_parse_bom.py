"""
        PARSE VCN CARD BOM LIBRARY
        The goal of this library is to parse the bom and get relevant data based on defined criteria
"""

import logging
from .VCN_checkBom import validate_json_input
from jsonpath_ng import parse
VCN_LOGGER = logging.getLogger(__name__)

def check_transaction_criteria_dict(transaction,transaction_criteria={}):
    """ Checks if transaction satisfied include and exclude criteria

    Args:
        transaction (dict): transaction
        transaction_criteria (dict, optional): data dict with specific keys and format. Defaults to dict().
            example :{
                        "include_criteria":{"Type":"SETTLEMENT","TransactionDateTime.ReadyToReport":"*"},
                        "exclude_criteria":{"Type":"GETFULL"}
                      }
    Returns:
        bool: Result True if transaction satisfy defined conditions
    """
    try:
        VCN_LOGGER.info("Include criteria: %s",transaction_criteria['include_criteria'])
        check_include_result = check_key_values_in_transaction(transaction,transaction_criteria['include_criteria'])
    except KeyError:
        VCN_LOGGER.info("Include_criteria not defined in criteria dict %s", transaction_criteria)
        check_include_result = None

    try:
        VCN_LOGGER.info("Exclude criteria: %s", transaction_criteria['exclude_criteria'])
        check_exclude_result = check_key_values_in_transaction(transaction,transaction_criteria['exclude_criteria'])
    except KeyError:
        VCN_LOGGER.info("Exclude_criteria not defined: %s",transaction_criteria)
        check_exclude_result = None

    conditions_pass = [
                    check_include_result and not check_exclude_result,
                    check_include_result is None and not check_exclude_result,
                    check_include_result and check_exclude_result is None
                    ]

    result = True
    if check_include_result is None and check_exclude_result is None:
        VCN_LOGGER.info("No filters defined for transaction: %s", transaction['Type'])
    elif any(conditions_pass):
        VCN_LOGGER.info("Transaction %s selected",transaction['Type'])
    else:
        VCN_LOGGER.info("Transaction %s doesn't satisfy %s",transaction['Type'],transaction_criteria)
        result=False
    return result

def check_key_values_in_transaction(transaction,key_values={}):
    """Check if a data dict of key values are present in a transaction

    Args:
        transaction (dict): transaction data dictionary
        key_values (dict): data dictionary of key:values to check in transaction

    Returns:
        bool: return True if key:val in transaction
    """
    for match_key in key_values:
        parser = parse(match_key)
        list_val = [match.value for match in parser.find(transaction)]
        if len(list_val) != 0:
            list_val.append('*')
        values = key_values[match_key]

        if any(value in values for value in list_val):
            VCN_LOGGER.info("%s:%s found in transaction",match_key,key_values[match_key])
        else:
            VCN_LOGGER.info("('%s':'%s') not found in transaction",match_key,key_values[match_key])
            return False
    return True


def get_transactions_from_bom(input_bom,transaction_key: str,transactions_criteria={}):
    """Get ready to report transactions from car bom

    Args:
        input_bom (dict): VCN card bom
        include_criteria (dict): data dictionary of transactions to be selected
        exclude_criteria (dict): data dictionary of transactions to be filtered

    Returns:
        list: list of transactions
    """
    formatted_json = validate_json_input(input_bom)
    selected_transaction_list = []
    not_selected_transaction_list =[]
    try:
        VCN_LOGGER.info("%s:%s",transaction_key,formatted_json[transaction_key])
        for transaction in formatted_json[transaction_key]:
            if check_transaction_criteria_dict(transaction,transactions_criteria):
                selected_transaction_list.append(transaction)
            else:
                not_selected_transaction_list.append(transaction)
                VCN_LOGGER.info("%s doesn't match criteria in %s",transaction['Type'],transaction_key)
    except KeyError as parse_exception:
        VCN_LOGGER.info("%s: Json doesn't contain key %s",parse_exception,transaction_key)
    VCN_LOGGER.warning(f"{transaction_key} : List elements according to criteria {transactions_criteria} : Selected: {[transaction['Type'] for transaction in  selected_transaction_list]}, Not selected: {[transaction['Type'] for transaction in  not_selected_transaction_list]}")
    if not selected_transaction_list:
        VCN_LOGGER.info("No transactions found according to input criteria %s",transactions_criteria)
    return selected_transaction_list

def get_useful_bom_data(bom,transactions_criteria={}):
    """retrieve bom with only transaction criteria according to input transactions
    Args:
        bom (_type_): input json
        transactions_criteria (_type_, optional): data dict containing transaction criteria. Defaults to dict().

    Returns:
        _type_: output bom with only selected transactions
    """
    formatted_bom = validate_json_input(bom)
    selected_transactions = get_transactions_from_bom(bom,'Transactions',transactions_criteria)
    selected_payment_transactions = get_transactions_from_bom(bom,'PaymentTransactions',transactions_criteria)
    try:
        del formatted_bom['Transactions'],formatted_bom['PaymentTransactions']
    except KeyError as key_no_found:
        VCN_LOGGER.warning("%s in input json",key_no_found)
    formatted_bom['Transactions'],formatted_bom['PaymentTransactions'] = selected_transactions,selected_payment_transactions
    return formatted_bom