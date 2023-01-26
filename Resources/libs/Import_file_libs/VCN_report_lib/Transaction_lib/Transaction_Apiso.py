from VCN_report_lib.Transaction_lib.Transaction import Transaction
from VCN_report_lib import utils
import datetime

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

class TransactionApiso(Transaction) :
    def __init__(self, itype, iinfo, iindex):
        #-------------------------------------------------------------------#
        self._type                         = itype
        self._iinfo                        = iinfo
        self._index                        = iindex
        #-------------------------------------------------------------------#
        self._cardreport                   = ""
        self._authreport                   = ""
        self._settreport                   = ""
        self._statusreport                 = ""
        self._bom_Expected                 = {}
        
        self._balreport                    = ''
        self._output                       = ''
        self._int_fee                      = ''
        self._transfer_type                = ''
        #-------------------------------------------------------------------#
        self._date_ref                     = datetime.datetime.utcnow() + datetime.timedelta(seconds=self._index)
        self._date                         = str(self._date_ref.strftime("%Y-%m-%d %H:%M:%S"))
        self._date_provider                = str(self._date_ref.strftime("%Y-%m-%d %H:00:00"))
        self._card_amount_req              = float(self._iinfo[2])
        self._card_currency_req            = self._iinfo[1]
        self._card_amount                  = float(self._iinfo[4])
        self._card_currency                = self._iinfo[3]
        self._exch_rate                    = self._card_amount_req / self._card_amount
        
        if self._card_currency_req != self._card_currency:
            self._forex_fee                = "{0:.2f}".format(0.2 * self._card_amount)
            self._ffee_bomexp_amt          = {'Amount': str(self._forex_fee),'Currency':self._card_currency}
            self._ffee_bomexp              = {"ForexFeeAmount" : self._ffee_bomexp_amt}
        else:
            self._forex_fee                = 0
            self._ffee_bomexp              = {}
            
        self._provider_ref                 = self._iinfo[5]
        self._ama_ref                      = self._iinfo[6]

        if (self._index == 0 and self._iinfo[0] != ''):
            self._TrnId                    = self._iinfo[0]
        else:
            self._TrnId                    = 'TRNID_' + self._date_ref.strftime("%Y%m%d%H%M%S") + '_' + str(self._index)
        if self._iinfo[9] == 'VI':
            self._vendor                   = 'V'
        else:
            self._vendor                   = 'M'
        
    def __str__(self):
        return self._type

 #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
    
class TransactionApisoCREATED(TransactionApiso) :
    def generate_report(self, dict) :
        dict["bal_amount"] = self._card_amount

        cardreport      = self._provider_ref + ',ACC' + self._provider_ref + ',' + self._ama_ref + ',123456,3,' \
                        + self._TrnId + ',' + self._date_provider + ',C,' + self._vendor + ',' + self._card_currency \
                        + ',575131232,' + "{0:.2f}".format(self._card_amount_req) + ',' + self._card_currency_req + ',' \
                        + "{0:.2f}".format(self._card_amount) + ',' + str(self._forex_fee)
        
        authreport      = ''
        
        settreport      = ''
        
        statusreport    = self._provider_ref + ',ACC' + self._provider_ref + ',' + self._ama_ref + ',123456,USD,575131232,' \
                        + self._date_provider + ',A,' + "{0:.2f}".format(self._card_amount) + ',0,' \
                        + "{0:.2f}".format(self._card_amount)
        
        bom_Expected    = { "Transactions": {
                                "AmountRequested": {
                                    "Amount": "{0:.2f}".format(self._card_amount_req),
                                    "Currency": self._card_currency_req
                                },
                                "AmountLoaded": {
                                    "Amount": "{0:.2f}".format(self._card_amount),
                                    "Currency": self._card_currency
                                },
                                "Link": "VCCAPISO",
                                "ExternalTransactionId": self._TrnId,
                                "TransactionDateTime": {
                                    "Creation": self._date + '.910',
                                    "Processed": self._date_provider,
                                    "ReadyToReport": self._date
                                },
                                "TransactionStatus": {
                                    "ActionStatus": "OK",
                                    "Timestamp": self._date + '.910'
                                },
                                "Type": utils.other_types(self._type.split("_")[0])[1]
                            }}
        
        cardreport = self.report_formating(cardreport)
        authreport = self.report_formating(authreport) 
        settreport = self.report_formating(settreport)
        statusreport = self.report_formating(statusreport)

        return cardreport,authreport,settreport,statusreport,bom_Expected, dict
    
    
class TransactionApisoDELETED(TransactionApiso) :
    def generate_report(self, dict) :
        dict["card_amount"]             = self._card_amount
        if dict["bal_amount"] == '':
            dict["bal_amount"]          = self._card_amount
        try:
            if type.split("_")[1]>0:
                dict["part_amount_req"] = float(self._type.split("_")[1])
                dict["part_amount"]     = dict["part_amount_req"] / self._exch_rate 
                amount_before           = dict["bal_amount"]
                amount_after            = dict["bal_amount"] - delete_amount
                dict["bal_amount"]      = amount_after
        except:
            amount_before               = dict["bal_amount"]
            dict["part_amount"]         = dict["bal_amount"]
            amount_after                = dict["bal_amount"] - dict["part_amount"]
            dict["bal_amount"]          = amount_after
            dict["part_amount_req"]     = dict["part_amount"]

        if self._card_currency_req != self._card_currency:
            self._forex_fee = "{0:.2f}".format(-0.2 * dict["part_amount"])
        else:
            self._forex_fee = 0

        cardreport      = self._provider_ref + ',ACC' + self._provider_ref + ',' + self._ama_ref + ',123456,3,' \
                        + self._TrnId + ',' + self._date_provider + ',F,' + self._vendor + ',' + self._card_currency \
                        + ',575131232,-' + "{0:.2f}".format(dict["part_amount_req"]) + ',' + self._card_currency_req \
                        + ',-' + "{0:.2f}".format(dict["part_amount"]) + ',' + str(self._forex_fee)
                
        authreport      = ''
        
        settreport      = ''
        
        statusreport    = self._provider_ref + ',ACC' + self._provider_ref + ',' + self._ama_ref + ',123456,USD,575131232,' \
                        + self._date_provider + ',B,' + str(amount_after) + ',0,' + str(amount_after)
        
        bom_Expected    = { "Transactions": {
                                "AmountLoaded": {
                                    "Amount": "{0:.2f}".format(dict["part_amount"]),
                                    "Currency": self._card_currency
                                },
                                "AmountRequested": {
                                    "Amount": '-' + "{0:.2f}".format(dict["part_amount_req"]),
                                    "Currency": self._card_currency_req
                                },
                                "ExternalTransactionId": self._TrnId,
                                "Source": "IMPORT",
                                "TransactionDateTime": {
                                    "Creation": self._date + '.900',
                                    "Processed": self._date_provider,
                                    "ReadyToReport": self._date
                                },
                                "TransactionStatus": {
                                    "ActionStatus": "OK",
                                    "Timestamp": self._date + '.900'
                                },
                                "Type": utils.other_types(self._type.split("_")[0])[1]
                            }}
        
        cardreport = self.report_formating(cardreport)
        authreport = self.report_formating(authreport) 
        settreport = self.report_formating(settreport)
        statusreport = self.report_formating(statusreport)
            
        return cardreport,authreport,settreport,statusreport,bom_Expected, dict

