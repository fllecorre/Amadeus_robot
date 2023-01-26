from VCN_report_lib.Manager_lib.Manager import Manager
from VCN_report_lib.Transaction_lib import Transaction_Citibank
from VCN_report_lib import utils

import xml.etree.ElementTree as ET
from datetime import datetime
import random

#https://rndwww.nce.amadeus.net/confluence/pages/viewpage.action?spaceKey=AVCC&title=Citibank+Reporting

class ManagerTransactionsCitibank(Manager):
    def expected_trans(self, itype, iinfo, iindice):
        list_type = itype.split('_')
        if list_type[0] == 'CITI':
            if   list_type[1] == "D" :
                return Transaction_Citibank.TransactionCitibankDEBIT(itype, iinfo, iindice)
            elif list_type[1] == "C" :
                return Transaction_Citibank.TransactionCitibankCREDIT(itype, iinfo, iindice)
    
    def generate(self, list_trans):
        #---------------------------------------------------------------------#
        adict = {
            "NumOfCredits" : 0,
            "TotalAmountOfCredits" : 0,
            "NumOfDebits" : 0,
            "TotalAmountOfDebits" : 0,
            "SequenceNum" : 0,

            "part_amount_req" : 0,
            "card_amount" : 0,
            "bal_amount" : 0,
            "part_amount" : 0,
        }
        l_report  = ''
        l_bom_expected = {"PaymentTransactions":[],"Transactions":[]}
        #---------------------------------------------------------------------#
        l_report += '<CDFTransmissionFile xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="CDFTransmissionFile.xsd">'
        l_report +=     self.generate_Header()
        l_report +=     '<IssuerEntity ICANumber="1412" IssuerNumber="00000001412">'
        l_report +=         self.generate_IssuerInformation_3000()
        l_report +=         '<CorporateEntity CorporationNumber="181312345">'
        l_report +=             self.generate_CorporateInformation_4000()
        
        adict["SequenceNum"] = 3
        #---------------------------------------------------------------------#
        l_report +=             '<AccountEntity AccountNumber="XXXXXXXXXX654321">'
        for trans in list_trans:
            report1, report2, adict = trans.generate_report(adict)
            l_report += report1
            l_bom_expected = self.update_bom_expected(l_bom_expected, report2)
            
        #---------------------------------------------------------------------#
        l_report +=             '</AccountEntity>'        
        l_report +=         '</CorporateEntity>'
        l_report +=     '</IssuerEntity>'
        l_report +=     self.generate_Trailer(adict) 
        l_report += '</CDFTransmissionFile>'
        
        return l_report, l_bom_expected
        #---------------------------------------------------------------------#
    
    def update_bom_expected(self, l_bom_expected, report2) :
        for tr in report2:
            l_bom_expected[tr].append(report2[tr])
        return l_bom_expected

    def generate_Header(self) :
        date = datetime.now()
        astring =   '<TransmissionHeader_1000>' + \
                        '<TransRecordHeader>' + \
                            '<SequenceNum>1</SequenceNum>' + \
                            '<MasterCardRecSeqNum>' + str(random.randint(1,99)) + '</MasterCardRecSeqNum>' + \
                        '</TransRecordHeader>' + \
                        '<ProcessingStartDate>' + date.strftime("%Y-%m-%d") + '</ProcessingStartDate>' + \
                        '<ProcessingStartTime>' + date.strftime("%H:%M:%S") + '</ProcessingStartTime>' + \
                        '<FileReferenceNum>' + date.strftime("%Y%m%d%H%M%S") + '8AW0000050' + '</FileReferenceNum>' + \
                        '<CDFVersionNum>3.00</CDFVersionNum>' + \
                        '<RunModeIndicator>V</RunModeIndicator>' + \
                        '<ProcessorNum>' + '7027' + '</ProcessorNum>' + \
                        '<ProcessorName>CITI Provider</ProcessorName>' + \
                        '<SchemaVersionNum>' + '14.01.00.00' + '</SchemaVersionNum>' + \
                    '</TransmissionHeader_1000>'
        return astring
    
    def generate_IssuerInformation_3000(self) :
        astring =   '<IssuerInformation_3000>' + \
                        '<HierarchyRecordHeader>' + \
                            '<SequenceNum>2</SequenceNum>' + \
                            '<StatusCode>A</StatusCode>' + \
                        '</HierarchyRecordHeader>' + \
                        '<NameLocaleCode>ENU</NameLocaleCode>' + \
                        '<NameLine1>Citibank Global - USA</NameLine1>' + \
                        '<AlternateNameLine1>CDF3.0.14.01.00.G.00011</AlternateNameLine1>' + \
                        '<PostedCurrencyCode>840</PostedCurrencyCode>' + \
                    '</IssuerInformation_3000>'
        return astring

    def generate_CorporateInformation_4000(self):
        astring =   '<CorporateInformation_4000>' + \
                        '<HierarchyRecordHeader>' + \
                            '<SequenceNum>3</SequenceNum>' + \
                            '<StatusCode>A</StatusCode>' + \
                        '</HierarchyRecordHeader>' + \
                        '<BillingType>O</BillingType>' + \
                        '<Cycle>M</Cycle>' + \
                        '<CycleDateIndicator>25</CycleDateIndicator>' + \
                        '<NameLocaleCode>ENU</NameLocaleCode>' + \
                        '<NameLine1>AMADEUS</NameLine1>' + \
                        '<BillingCurrencyCode>840</BillingCurrencyCode>' + \
                    '</CorporateInformation_4000>'
        return astring

    def generate_Trailer(self, dict) :
        astring =   '<TransmissionTrailer_9999>' + \
                        '<TransRecordHeader>' + \
                            '<SequenceNum>' + str(dict["SequenceNum"]+1) + '</SequenceNum>' + \
                        '</TransRecordHeader>' + \
                        '<RecordCount>' + str(dict["SequenceNum"]) + '</RecordCount>' + \
                        '<NumOfCredits>' + str(dict["NumOfCredits"]) + '</NumOfCredits>' + \
                        '<TotalAmountOfCredits>' + utils.add_digit(int(dict["TotalAmountOfCredits"]), 16) + '</TotalAmountOfCredits>' + \
                        '<NumOfDebits>' + str(dict["NumOfDebits"]) + '</NumOfDebits>' + \
                        '<TotalAmountOfDebits>' + utils.add_digit(int(dict["TotalAmountOfDebits"]), 16) + '</TotalAmountOfDebits>' + \
                    '</TransmissionTrailer_9999>'
        return astring
