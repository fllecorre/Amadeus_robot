

# importing module
import sys
  
# appending a path
# sys.path.append('./third_party')

import VCN_report_generator
from VCN_report_lib import VirtualCard
from xml.dom import minidom

print("----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")

#Debug IXARIS
list_1 = ['CARD CREATED', 'AUTHORISATION_OK','FREEZE','PURCHASE','CARD DELETED']
card=('0RABAc4dn_b34x6ncdRWbniIN', 'EUR', '1.00', 'EUR', '1.00', '0RAArEjtTbX57KYibgAPhHu_9', '22224WAF', '522093', '9372', 'CA', '1', '', '', '', '', '')
print("IXARIS : by older")
#print(VCN_report_generator.generate_report(list_1,card,'ixusb'))

print("----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")

#Debug APISO
list_1 = ['TRANSFER_-1']
card=('TRNID_FUND_IMPORT_0001','USD','10.00','EUR','20.00','l_vcn_ext_ref','22224V66','555544','1111','CA','1','','','','','')
print("APISO : by older")
#print(VCN_report_generator.generate_report(list_1,card,'apiso'))

print("----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")

#DEBUG USBANK
list_1 = ['USB_P_123']
card=('', 'USD', '111.12', 'Open', '', '111.12_USD_15962058944', '222286BA', '556904', '0580', 'CA', '999', '', '', '', '', '')
print("USBANK : by older")
#print(VCN_report_generator.generate_report(list_1,card,'ixusb'))

print("----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")

#DEBUG CITIBANK
list_1 = ["CITI_C","CITI_C"]
card = ('','USD','10.00','USD','10.00','','','9999992222221111','','','','','','','','')
print("CITIBANK 1 : by older")
l_report, l_bom_expected = VCN_report_generator.generate_report(list_1,card,'citibank')
#print(l_report)
#print(minidom.parseString(l_report).toprettyxml(indent="  "))
#print(l_bom_expected)

print("----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
card = VirtualCard.VirtualCard("citibank")

info1 = ('','USD','20.00','USD','20.00','','','9999992222221111','','','','','','','','')
card.add_transaction("CITI_C", info1)
info2 = ('','USD','10.00','USD','10.00','','','9999992222221111','','','','','','','','')
card.add_transaction("CITI_D", info2)

print("CITIBANK 2 : by new with multiple_transaction")
l_report, l_bom_expected = card.generate_transactions_report()

l_report  = minidom.parseString(l_report).toprettyxml(indent="  ")

#print(minidom.parseString(l_report).toprettyxml(indent="  "))
#print(l_bom_expected)

print("----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
card = VirtualCard.VirtualCard("citibank")

info = ('','USD','10.00','USD','10.00','','','9999992222221111','','','','','','','','')
card.add_list_transaction(["CITI_C", "CITI_D"], info)

print("CITIBANK 2 : by new with list_transaction")
l_report, l_bom_expected = card.generate_transactions_report()

l_report  = minidom.parseString(l_report).toprettyxml(indent="  ")
f = open("Report_Expected_Citibank.xml", "w")
f.write(l_report)
f.close()

print(minidom.parseString(l_report).toprettyxml(indent="  "))
print(l_bom_expected)

print("----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
card = VirtualCard.VirtualCard("usbank")
info = ('', 'USD', '111.12', 'Open', '', '111.12_USD_15962058944', '222286BA', '556904', '0580', 'CA', '999', '', '', '', '', '')

print("USBANK : by new")
