from VCN_report_lib.Transaction_lib.Transaction import Transaction
from VCN_report_lib import utils
import datetime

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

class TransactionCitibank(Transaction) :
    def __init__(self, itype, iinfo, iindex):
        self._type                  = itype
        self._info                  = iinfo
        self._index                 = iindex

    def __str__(self):
        return "None"

    def init_report (self):
    
        self._date_ref              = datetime.datetime.utcnow() + datetime.timedelta(seconds=self._index)
        self._date                  = str(self._date_ref.strftime("%Y-%m-%d"))
        self._date_provider         = str((self._date_ref + datetime.timedelta(hours=1)).strftime("%Y-%m-%d"))
        self._date_juliantype       = self.datestdtojd(self._date)
        self._AdjId                 ='ADJID_' + self._date_ref.strftime("%Y%m%d%H%M%S") + '_' + utils.get_random_alphanumeric(5)
        
        self._card_trx_status       = self._info[3]

        self._card_amount_req       = float(self._info[2])
        self._card_currency_req     = self.currency_code_number_iso4217(self._info[1])[0]
        self._card_exponent_req     = self.currency_code_number_iso4217(self._info[1])[1]
        
        if (self._info[3] != '') :
            self._card_amount       = float(self._info[4])
            self._card_currency     = self.currency_code_number_iso4217(self._info[3])[0]
            self._card_exponent     = self.currency_code_number_iso4217(self._info[3])[1]
        else :
            self._card_amount       = self._card_amount_req
            self._card_currency     = self._card_currency_req
            self._card_exponent     = self._card_exponent_req

        self._exch_rate             = self._card_amount_req/self._card_amount

        if self._index == 0 and self._info[0] != '':
            self._TrnId             = self._info[0]
        else:
            self._TrnId             = 'TRNID_' + self._date_ref.strftime("%Y%m%d%H%M%S") + '_' + utils.get_random_alphanumeric(5)		


    def generate_FinancialRecordHeader(self, dict) :
        astring =           '<FinancialRecordHeader>' + \
                                '<SequenceNum>' + str(dict["SequenceNum"]) + '</SequenceNum>' + \
                                '<MaintenanceCode>U</MaintenanceCode>' + \
                            '</FinancialRecordHeader>'
        return astring
    
    def generate_CardAcceptor_5001(self, dict) :
        cardreport =    '<CardAcceptor_5001>' + \
                            self.generate_FinancialRecordHeader(dict) + \
                            '<AcquiringICA>6897</AcquiringICA>' + \
                            '<CardAcceptorId>266999786889</CardAcceptorId>' + \
                            '<CardAcceptorName>cooley</CardAcceptorName>' + \
                            '<CardAcceptorStreetAddress>12 MAIN STREET</CardAcceptorStreetAddress>' + \
                            '<CardAcceptorCity>MANKATO</CardAcceptorCity>' + \
                            '<CardAcceptorStateProvince>MN</CardAcceptorStateProvince>' + \
                            '<CardAcceptorLocationPostalCode>00001</CardAcceptorLocationPostalCode>' + \
                            '<CardAcceptorCountryCode>USA</CardAcceptorCountryCode>' + \
                            '<CardAcceptorTelephoneNum>5073888555</CardAcceptorTelephoneNum>' + \
                            '<LegalCorporationName>cooley</LegalCorporationName>' + \
                            '<CardAcceptorBusinessCode>3829</CardAcceptorBusinessCode>' + \
                            '<CardAcceptorTaxId>411883834</CardAcceptorTaxId>' + \
                        '</CardAcceptor_5001>'
        return cardreport

    def generate_FinancialTransaction_5000(self, itype, dict) :
        str_part_amount = utils.add_digit(int(dict["part_amount"]*(10**self._card_exponent)), 16)
        str_part_amount_req = utils.add_digit(int(dict["part_amount_req"]*(10**self._card_exponent_req)), 16)

        cardreport  =       '<FinancialTransaction_5000>' + \
                                self.generate_FinancialRecordHeader(dict) + \
                                '<ProcessorTransactionId>' + self._TrnId + '</ProcessorTransactionId>' + \
                                '<AlternateAccount>' + \
                                    '<AlternateAccountNumber>XXXXXXXXXX123456</AlternateAccountNumber>' + \
                                    '<AlternateAccountType>C</AlternateAccountType>' + \
                                '</AlternateAccount>' + \
                                '<AcquirerReferenceData>55500807108286688900078</AcquirerReferenceData>' + \
                                '<CardHolderTransactionType>' + itype[0] + '</CardHolderTransactionType>' + \
                                '<PostingDate>' + self._date_provider + '</PostingDate>' + \
                                '<TransactionDate>' + self._date + '</TransactionDate>' + \
                                '<ProcessingDate>' + self._date + '</ProcessingDate>' + \
                                '<BillingDate>' + self._date + '</BillingDate>' + \
                                '<ApprovalCode>' + '111111' + '</ApprovalCode>' + \
                                '<BanknetReferenceNum>' + '111111' + '</BanknetReferenceNum>' + \
                                '<DebitOrCreditIndicator>' + itype[1] + '</DebitOrCreditIndicator>' + \
                                '<AmountInOriginalCurrency CurrencyCode="' + self._card_currency + '" CurrencyExponent="' + str(self._card_exponent) + '" CurrencySign="C">' + \
                                str_part_amount + '</AmountInOriginalCurrency>' + \
                                '<OriginalCurrencyCode>' + self._card_currency + '</OriginalCurrencyCode>' + \
                                '<AmountInPostedCurrency CurrencyCode="' + self._card_currency_req + '" CurrencyExponent="' + str(self._card_exponent_req) + '" CurrencySign="C">' + \
                                str_part_amount_req + '</AmountInPostedCurrency>' + \
                                '<PostedCurrencyCode>' + self._card_currency_req + '</PostedCurrencyCode>' + \
                                '<PostedCurrencyConversionDate>' + self._date_juliantype + '</PostedCurrencyConversionDate>' + \
                                '<PostedConversionRate>' + str(self._exch_rate) + '</PostedConversionRate>' + \
                                '<BillingCurrencyCode>' + self._card_currency_req + '</BillingCurrencyCode>' + \
                                '<BillingConversionRate>1.0</BillingConversionRate>' + \
                                '<CustomerCode>19963684</CustomerCode>' + \
                                '<CardAcceptorReferenceNum>266999786889</CardAcceptorReferenceNum>' + \
                                '<IssuerTransactionCode>3001</IssuerTransactionCode>' + \
                                '<CustomIdentifier>' + self._info[7] + '</CustomIdentifier>' + \
                                '<CustomIdentifierType>OTHER1</CustomIdentifierType>' + \
                                '<CustomerRefValue3>8058*</CustomerRefValue3>' + \
                                '<CustomerRefValue10>VCA ACCOUNT</CustomerRefValue10>' + \
                            '</FinancialTransaction_5000>'
        return cardreport

    def currency_code_number_iso4217 (self, icurrency_code) :
        if   icurrency_code == "USD" :
            return "840", 2
        elif icurrency_code == "EUR" :
            return "978", 2
        elif icurrency_code == "AUD" :
            return "036", 2
        elif icurrency_code == "GBP" :
            return "826", 2
        elif icurrency_code == "CNY" :
            return "156", 2

    def generate_bom_expected (self, adict, type) :
        return {
                    "PaymentTransactions": 
                    {
                        "AmountRequested": { 
                            "Amount": str(adict["part_amount_req"]),
                            "Currency": self._info[1]
                        },
                        "ApprovalCode": "61846",
                        "Merchant": {
                            "Name": "DELTA     00670705262916",
                            "Country": "USA",
                            "MCC": "3058"
                        },
                        "ExternalTransactionId": self._TrnId,
                        "TransactionAmount": {
                            "Amount": str(adict["part_amount"]),
                            "Currency": self._info[3]
                        },
                        "TransactionDateTime": {
                            "Creation": str(self._date_ref.strftime("%Y-%m-%d 00:00:00.000")),
                            "Processed": str(self._date_ref.strftime("%Y-%m-%d 00:00:00.000")),
                            "ReadyToReport": str(self._date_ref.strftime("%Y-%m-%d 00:00:00.000"))
                        },
                        "TransactionStatus": {
                            "ActionStatus": "OK",
                            "PluginStatus": self._card_trx_status,
                            "Timestamp": str(self._date_ref.strftime("%Y-%m-%d 00:00:00.000"))
                        },
                        "Type": utils.other_types(type)[1]
                    }
                }      
        
 #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

class TransactionCitibankDEBIT(TransactionCitibank) :
    def __str__(self):
        return "CITI_D"

    def generate_report(self, adict) :

        self.init_report()

        adict["bal_amount"]         = adict["card_amount"]
        adict["part_amount"]        = self._card_amount
        adict["part_amount_req"]    = self._card_amount_req
        self._amount_before         = adict["bal_amount"]
        adict["part_amount"]        = adict["part_amount_req"]/self._exch_rate
        self._amount_after          = adict["bal_amount"] - adict["part_amount"]
        adict["bal_amount"]         = self._amount_after

        cardreport   =  '<FinancialTransactionEntity ProcessorTransactionId="' + self._TrnId + '">'
        adict["SequenceNum"] += 1
        cardreport  +=      self.generate_FinancialTransaction_5000(['00', 'D'], adict)
        adict["SequenceNum"] += 1                    
        cardreport  +=      self.generate_CardAcceptor_5001(adict)
        cardreport  +=  '</FinancialTransactionEntity>'

        adict["TotalAmountOfDebits"] += adict["part_amount_req"]*(10**self._card_exponent_req)
        adict["NumOfDebits"] += 1
        
        bom_expected =  self.generate_bom_expected(adict, 'DEBIT')
                
        return cardreport,bom_expected, adict


class TransactionCitibankCREDIT(TransactionCitibank) :
    def __str__(self):
        return "CITI_C"

    def generate_report(self, adict) :
        
        self.init_report()

        adict["bal_amount"]         = adict["card_amount"]
        adict["part_amount"]        = self._card_amount
        adict["part_amount_req"]    = self._card_amount_req
        self._amount_before         = adict["bal_amount"]
        adict["part_amount"]        = adict["part_amount_req"]/self._exch_rate
        self._amount_after          = adict["bal_amount"] + adict["part_amount"]
        adict["bal_amount"]         = self._amount_after
    
        cardreport   =  '<FinancialTransactionEntity ProcessorTransactionId="' + self._TrnId + '">'
        adict["SequenceNum"] += 1
        cardreport  +=      self.generate_FinancialTransaction_5000(['20', 'C'], adict)
        adict["SequenceNum"] += 1                    
        cardreport  +=      self.generate_CardAcceptor_5001(adict)
        cardreport  +=  '</FinancialTransactionEntity>'

        adict["TotalAmountOfCredits"] += adict["part_amount_req"]*(10**self._card_exponent_req)
        adict["NumOfCredits"] += 1

        bom_expected    = self.generate_bom_expected( adict, 'CREDIT')
                
        return cardreport,bom_expected, adict
        
