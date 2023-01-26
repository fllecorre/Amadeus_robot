from random import choice
import string
import sys

class VirtualException(Exception):
    def __init__(self, _type, _func):
        Exception(self)
        
def other_types(type):
    matrix={    
                'Transactions': 
                {
                    'CREATION': 'CARD CREATED',
                    'CANCELLATION': 'CARD DELETED',
                    'UPDATE_FREEZE': 'FREEZE',
                    'UPDATE_THAW': 'THAW',
                    'UPDATE_FUNDS': 'TRANSFER'
                },
                'PaymentTransactions': 
                {
                    'REVERSAL': 'AUTHORISATION RELEASE',
                    'SETTLEMENT': 'PURCHASE',
                    'REFUND': 'MERCHANT REFUND',
                    'AUTHORISATION': 'AUTHORISATION'
                },
                'USB_PaymentTransactions': 
                {
                    'SETTLEMENT': 'P',
                    'REFUND': 'C'
                },
                'CITI_PaymentTransactions': 
                {
                    'SETTLEMENT': 'DEBIT',
                    'REFUND': 'CREDIT'
                },
            }
    for i in matrix:
        for k, v in matrix[i].items():
            if v == type:
                return [i,k]
            if k == type:
                return [i,v]
    print("Unexpected error:", sys.exc_info()[0])
        
def get_random_alphanumeric(size):
	return ''.join(choice(string.ascii_uppercase + string.digits) for _ in range(size))

def add_digit(ivalue, inum_of_digit, idigit = "0") :
        astring = str(ivalue) 
        return (inum_of_digit-len(astring))*idigit + astring