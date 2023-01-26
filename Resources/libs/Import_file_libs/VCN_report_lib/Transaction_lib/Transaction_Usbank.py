from VCN_report_lib.Transaction_lib.Transaction import Transaction
from VCN_report_lib import utils
import datetime

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

class TransactionUsbank (Transaction) :
    def __init__(self, iinfo, iindex):
        self._info                         = iinfo
        self._index                        = iindex

    def __str__(self):
        return "None"

    def init_report (self):

        self._FAreport                     = ""
        self._cardreport                   = ""
        self._bom_Expected                 = {}

        self._date_ref                     = datetime.datetime.utcnow() + datetime.timedelta(seconds=self._index)
        self._date                         = str(self._date_ref.strftime("%Y-%m-%d %H:%M:%S")) #
        self._date_provider                = str((self._date_ref + datetime.timedelta(hours=1)).strftime("%Y-%m-%d 00:00:00.000"))
        self._AdjId                        = 'ADJID_' + self._date_ref.strftime("%Y%m%d%H%M%S") + '_' + get_random_alphanumeric(5)

        self._card_trx_status = self._info[3]

        try :
            if self._info[16] != '':
                self._card_amount_req      = float(self._info[2])
                self._card_currency_req    = self._info[1]
                self._card_amount          = float(self._info[16])
                self._card_currency        = self._info[17]
                self._exch_rate            = self._card_amount_req / self._card_amount
                self._forex_fee            = "{0:.2f}".format(0.8 * self._card_amount)
        except:
            self._card_amount              = float(self._info[2]) 
            self._card_amount_req          = float(self._info[2])
            self._card_currency            = self._info[1]
            self._card_currency_req        = self._info[1]
            self._exch_rate                = 1
            if self._info[15] in self.list_keys :
                self._merchantName         = self.merchant_dict[self._info[15]]['merchantName']
                self._merchantCountry      = self.merchant_dict[self._info[15]]['merchantCountry']
                self._merchantCategoryCode = self.merchant_dict[self._info[15]]['merchantCategoryCode']
            else:
                self._merchantName         = 'JETSTAR AIR            AUSTRALIA     AUS                                                             '
                self._merchantCountry      = 'AU'
                self._merchantCategoryCode = '3079'

        if self._index == 0 and self._info[0] != '':
            self._TrnId                    = self._info[0]
        else:
            self._TrnId                    = 'TRNID_' + self._date_ref.strftime("%Y%m%d%H%M%S")+ '_' + get_random_alphanumeric(5)

        if self._info[9] == 'VI':
            self._vendor                   = 'VISA'
            self._factory                  = '1a_vi_12m'
            self._nonforexfee              = '0.800000000'
        else:
            self._vendor                   = 'MASTERCARD'
            self._factory                  = '1a_ca_12m'
            self._nonforexfee              = '0.000000000'
            
        if int(self._info[10])==1:
            self._factory                  = self._factory + '_ss'
        else:
            self._factory                  = self._factory + '_ms'
        #-------------------------------------------------------------------#


    def generate_card_report(self, adict) :
        #date_ref_BEFORE_AFTER-----------------------------------------------------date_ref_BEFORE_AFTER.strftime("%m/%d/%Y"))
        card_report =   str(self._date_ref.strftime("%m/%d/%Y")) + ',' + str(self._date_ref.strftime("%m/%d/%Y")) + ',' + self._TrnId + \
                        ',"amadeus","USA",' + self._info[5] + ',' + self._info[7] + 'XXXXXX' + self._info[8] +',440910110,' + type.split('_')[1] + \
                        ',3001,556904XXXXXX0272,' + str(adict["part_amount_req"]) + ',' + adict["card_currency"] + ',' + str(adict["part_amount"]) + \
                        ',' + adict["card_currency"] + ',DELTA     00670705262916,USA,3058,,,' + self._info[3] + ',61846,' + self._info[11] + ',' + \
                        self._info[12] + ',' + self._info[13] + ',' + self._info[14] + ',' + self._info[15] + ',,,,,,,,,,'
        return card_report


    def generate_bom_expected(self, adict, type) :
        bom_Expected={ "PaymentTransactions": {
                            "AmountRequested": { 
                                "Amount": str(adict["part_amount_req"]),
                                "Currency": adict["card_currency_req"]
                            },
                            "ApprovalCode": "61846",
                            "Merchant": {
                                "Name": "DELTA     00670705262916",
                                "Country": "USA",
                                "MCC": "3058"
                            },
                            "ExternalTransactionId": self.TrnId,
                            "TransactionAmount": {
                                "Amount": str(adict["part_amount"]),
                                "Currency": adict["card_currency"]
                            },
                            "TransactionDateTime": {
                                "Creation": str(self.date_ref.strftime("%Y-%m-%d 00:00:00.000")),
                                "Processed": str(self.date_ref.strftime("%Y-%m-%d 00:00:00.000")),
                                "ReadyToReport": str(self.date_ref.strftime("%Y-%m-%d 00:00:00.000"))
                            },
                            "TransactionStatus": {
                                "ActionStatus": "OK",
                                "PluginStatus": self._card_trx_status,
                                "Timestamp": str(self.date_ref.strftime("%Y-%m-%d 00:00:00.000"))
                            },
                            "Type": other_types(type)[1][1]
                        }}
        return bom_Expected

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

class TransactionUsbankSETTLEMENT(TransactionUsbank) :
    def generate_report(self, adict) :
        
        self.init_report()
        
        FAreport = self.report_formating(self._FAreport)
        cardreport = self.report_formating(self._cardreport)
            
        return FAreport,cardreport,self._bom_Expected , adict
    
    
class TransactionIxarisREFUND(TransactionUsbank) :
    def generate_report(self, adict) :
        
        self.init_report()
        
        FAreport = self.report_formating(FAreport)
        cardreport = self.report_formating(cardreport)
            
        return FAreport,cardreport,self._bom_Expected , adict