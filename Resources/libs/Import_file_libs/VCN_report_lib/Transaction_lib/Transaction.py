from VCN_report_lib import utils
import datetime
from abc import ABCMeta, abstractmethod

class Transaction:
    __metaclass__ = ABCMeta
    merchant_name = 'Air Europa'
    list_keys = ['TG','UX','UXES','UXIT']
    merchant_dict = {
        'TG' : {
            'merchantName' : 'THAI AIRWAYS INTRNTION',
            'merchantCountry' : 'NZ',
            'merchantCategoryCode' : '3077'
        },
        'UX': {
            'merchantName' : merchant_name,
            'merchantCountry' : 'FI',
            'merchantCategoryCode' : '4511'
        },
        'UXES': {
            'merchantName' : merchant_name,
            'merchantCountry' : 'ES',
            'merchantCategoryCode' : '4511'
        },
        'UXIT': {
            'merchantName' : merchant_name,
            'merchantCountry' : 'IT',
            'merchantCategoryCode' : '4511'
        }
    }

    @abstractmethod
    def __init__(self, itype, iinfo, iindex) :
        raise NotImplementedError

    @abstractmethod
    def generate_report(self, dict) :
        raise NotImplementedError

    def datestdtojd (self, idate):
        fmt = '%Y-%m-%d'
        adate = datetime.datetime.strptime(idate, fmt)
        adate = adate.timetuple()
        return str(adate.tm_year)[2:] + str(adate.tm_yday)

    def report_formating (self, ireport) :
        if len(ireport)>2:
            ireport += "\n"
        return ireport