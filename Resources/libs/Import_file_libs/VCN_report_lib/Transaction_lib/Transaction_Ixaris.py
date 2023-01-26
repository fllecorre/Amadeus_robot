from VCN_report_lib.Transaction_lib.Transaction import Transaction
from VCN_report_lib import utils
import datetime

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

class TransactionIxaris(Transaction) :
    def __init__(self, itype, iinfo, iindex):
        #-------------------------------------------------------------------#
        self._type                         = itype
        self._iinfo                        = iinfo
        self._index                        = iindex
        #-------------------------------------------------------------------#
        self._FAreport                     = ""
        self._cardreport                   = ""
        self._bom_Expected                 = {}
        #-------------------------------------------------------------------#
        self._date_ref                     = datetime.datetime.utcnow() + datetime.timedelta(seconds=self._index)
        self._date                         = str(self._date_ref.strftime("%Y-%m-%d %H:%M:%S")) #
        self._date_provider                = str((self._date_ref + datetime.timedelta(hours=1)).strftime("%Y-%m-%d 00:00:00.000"))
        self._AdjId                        = 'ADJID_' + self._date_ref.strftime("%Y%m%d%H%M%S") + '_' + utils.get_random_alphanumeric(5)
        try :
            if iinfo[16] != '':
                self._card_amount_req      = float(iinfo[2])
                self._card_currency_req    = iinfo[1]
                self._card_amount          = float(iinfo[16])
                self._card_currency        = iinfo[17]
                self._exch_rate            = self._card_amount_req / self._card_amount
                self._forex_fee            = "{0:.2f}".format(0.8 * self._card_amount)
        except:
            self._card_amount              = float(iinfo[2]) 
            self._card_amount_req          = float(iinfo[2])
            self._card_currency            = iinfo[1]
            self._card_currency_req        = iinfo[1]
            self._exch_rate                = 1
            if iinfo[15] in self.list_keys :
                self._merchantName         = self.merchant_dict[iinfo[15]]['merchantName']
                self._merchantCountry      = self.merchant_dict[iinfo[15]]['merchantCountry']
                self._merchantCategoryCode = self.merchant_dict[iinfo[15]]['merchantCategoryCode']
            else:
                self._merchantName         = 'JETSTAR AIR            AUSTRALIA     AUS                                                             '
                self._merchantCountry      = 'AU'
                self._merchantCategoryCode = '3079'

        if self._index == 0 and iinfo[0] != '':
            self._TrnId                    = iinfo[0]
        else:
            self._TrnId                    = 'TRNID_' + self._date_ref.strftime("%Y%m%d%H%M%S")+ '_' + utils.get_random_alphanumeric(5)

        if iinfo[9] == 'VI':
            self._vendor                   = 'VISA'
            self._factory                  = '1a_vi_12m'
            self._nonforexfee              = '0.800000000'
        else:
            self._vendor                   = 'MASTERCARD'
            self._factory                  = '1a_ca_12m'
            self._nonforexfee              = '0.000000000'
            
        if int(iinfo[10])==1:
            self._factory                  = self._factory + '_ss'
        else:
            self._factory                  = self._factory + '_ms'
        #-------------------------------------------------------------------#

    def __str__(self):
        return self._type

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

class TransactionIxarisCREATED(TransactionIxaris) :
    def generate_report(self, dict) :
        dict["bal_amount"] = self._card_amount
        
        cardreport   =  '"'+ self._date + '.910","' + self._date + '.911",' + '"Amadeus","amamadeus#amamadeus","' + \
                        self._TrnId + '","' + self._AdjId + '","' + self._type + '","' + self._card_currency + '","' + str(self._card_amount) + \
                        '","Funding Account","' + self._iinfo[3] + '","Virtual Card","' + self._iinfo[4] + '","Virtual Card","' + \
                        self._iinfo[4] + '","DESTINATION","' + self._card_currency + '","' + str(self._card_amount) + '","' + self._card_currency + \
                        '","' + str(self._card_amount) + '","1.000000000","0.000000000","0.000000000","0.00","' + \
                        str(self._card_amount) + '","' + str(self._card_amount) + '","COMPLETED","N","A","","","","","","","' + \
                        self._iinfo[5] + '","' + self._iinfo[6] + '","' + self._iinfo[7] + '******' + self._iinfo[8] + '","' + self._vendor + '","' + \
                        self._factory + '","' + self._iinfo[11] + '","' + self._iinfo[12] + '","' + self._iinfo[13] + '","' + self._iinfo[14] + '","' + \
                        self._iinfo[15] + '",""'
        
        FAreport     =  '"'+ self._date + '.910","' + self._date + '.911",' + '"Amadeus","amamadeus#amamadeus","FRANCE","' + \
                        self._TrnId + '","' + self._AdjId + '","' + self._type + '","' + self._card_currency + '","' + str(self._card_amount) + \
                        '","test.regression","Funding Account","' + self._iinfo[3] + '","Virtual Card","' + self._iinfo[4] + \
                        '","Funding Account","' + self._iinfo[3] + '","SOURCE","' + self._card_currency + '","-' + str(self._card_amount) + \
                        '","' + self._card_currency + '","-' + str(self._card_amount) + '","1.000000000","'+ self._nonforexfee + \
                        '","0.000000000","100000","-' + str(self._card_amount) + '","99999","COMPLETED","N","A","FANumber_Test",""'
        
        bom_Expected = {"Transactions": {
                            "AmountRequested": {
                            "Amount": str(self._card_amount),
                            "Currency": self._card_currency
                            },
                        "AmountLoaded": {
                            "Amount": str(self._card_amount),
                            "Currency": self._card_currency
                        },
                        "BalanceAfter": {
                            "Amount": str(self._card_amount),
                            "Currency": self._card_currency
                        },
                        "CardGenerationFee": {
                            "Amount": self._nonforexfee,
                            "Currency": self._card_currency
                        },
                        "Source": "IMPORT",
                        "Link": "VCCIX",
                        "CardFactory": self._factory,
                        "BalanceBefore": {
                            "Amount": "0.00",
                            "Currency": self._card_currency
                        },
                        "ExternalTransactionId": self._TrnId,
                        "TransactionDateTime": {
                            "Creation": self._date + '.910',
                            "Processed": self._date + '.911' ,
                            "ReadyToReport": self._date
                        },
                        "TransactionStatus": {
                            "ActionCode": "CA",
                            "ActionStatus": "OK",
                            "Timestamp": self._date + '.911'
                        },
                        "Type": utils.other_types(self._type.split("_")[0])[1]
                    }}
        
        FAreport = self.report_formating(FAreport)
        cardreport = self.report_formating(cardreport)
            
        return FAreport,cardreport,bom_Expected, dict
    
    
class TransactionIxarisDELETED(TransactionIxaris) :
    def generate_report(self, dict) :
        if dict["bal_amount"] == '': 
            dict["bal_amount"]          = self._card_amount
        try:
            if self._type.split("_")[1]>0:
                dict["bal_amount"]      = float(type.split("_")[1])
                dict["amount_before"]   = dict["bal_amount"]
                dict["amount_after"]    = dict["bal_amount"] - dict["delete_amount"] 
                dict["bal_amount"]      = dict["amount_after"]
        except:
            dict["amount_before"]       = dict["bal_amount"]
            dict["delete_amount"]       = dict["bal_amount"]
            dict["amount_after"]        = dict["bal_amount"] - dict["delete_amount"]
            dict["bal_amount"]          = dict["amount_after"]

        cardreport      = '"'+ self._date + '.980","' + self._date + '.981",' + '"Amadeus","amamadeus#amamadeus","' \
                        + self._TrnId + '","' + self._AdjId + '","' + self._type.split("_")[0] + '","' \
                        + self._card_currency + '","' + str(dict["delete_amount"]) + '","Virtual Card","' + self._iinfo[4] \
                        + '","Funding Account","' + self._iinfo[3] + '","Virtual Card","' + self._iinfo[4] \
                        + '","SOURCE","' + self._card_currency + '","-' + str(dict["delete_amount"]) + '","' \
                        + self._card_currency + '","-' + str(dict["delete_amount"]) + '","1.000000000","0.000000000","0.000000000","' \
                        + str(dict["amount_before"]) + '","-' + str(dict["delete_amount"]) + '","' + str(dict["amount_after"]) \
                        + '","COMPLETED","N","A","","","","","","","' + self._iinfo[5] + '","' + self._iinfo[6] + '","' \
                        + self._iinfo[7] + '******' + self._iinfo[8] + '","' + self._vendor + '","' + self._factory + '","' \
                        + self._iinfo[11] + '","' + self._iinfo[12] + '","' + self._iinfo[13] + '","' + self._iinfo[14] \
                        + '","' + self._iinfo[15] + '",""'
        
        FAreport = ""
        if dict["delete_amount"]>0:
            FAreport    = '"'+ self._date + '.980","' + self._date + '.981",' + '"Amadeus","amamadeus#amamadeus","FRANCE","' \
                        + self._TrnId + '","' + self._AdjId + '","TRANSFER","' + self._card_currency + '","' \
                        + str(dict["delete_amount"]) + '","test.regression","Virtual Card","' + self._iinfo[4] \
                        + '","Funding Account","' + self._iinfo[3] + '","Funding Account","' + self._iinfo[3] \
                        + '","DESTINATION","' + self._card_currency + '","' + str(dict["delete_amount"]) + '","' \
                        + self._card_currency + '","' + str(dict["delete_amount"]) + '","1.000000000","0.000000000","0.000000000","99999","' \
                        + str(dict["delete_amount"]) + '","100000","COMPLETED","N","A","FANumber_Test",""'
  
        bom_Expected    = { "Transactions": {
                                "AmountLoaded": {
                                    "Amount": str(dict["delete_amount"]),
                                    "Currency": self._card_currency
                                },
                                "AmountRequested": {
                                    "Amount": '-' + str(dict["delete_amount"]),
                                    "Currency": self._card_currency
                                },
                                "BalanceAfter": {
                                    "Amount": str(dict["amount_after"]),
                                    "Currency": self._card_currency
                                },
                                "BalanceBefore": {
                                    "Amount": str(dict["amount_before"]),
                                    "Currency": self._card_currency
                                },
                                "ExternalTransactionId": self._TrnId,
                                "Source": "IMPORT",
                                "TransactionDateTime": {
                                    "Creation": self._date + '.980',
                                    "Processed": self._date + '.981' ,
                                    "ReadyToReport": self._date
                                },
                                "TransactionStatus": {
                                    "ActionCode": "RV",
                                    "ActionStatus": "OK",
                                    "Timestamp": self._date + '.981'
                                },
                                "Type": utils.other_types(self._type.split("_")[0])[1]
                            }}
        
        FAreport = self.report_formating(FAreport)
        cardreport = self.report_formating(cardreport)
            
        return FAreport,cardreport,bom_Expected, dict