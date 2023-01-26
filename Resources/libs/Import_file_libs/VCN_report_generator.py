from __future__ import print_function
from __future__ import absolute_import
# ========================================================================================================
#                                 generate import file to be used for test purpose
# Import file content: https://rndwww.nce.amadeus.net/confluence/display/AVCC/Reconciliation
# =======================================================================================================

import sys
import datetime
from random import choice
import string
import logging
import copy
from VCN_report_generator_Input_data import *
import csv
import copy
from pathlib import Path
import os


from VCN_report_lib.VirtualCard import *
# get "root" logger in order to retrieve the property script_path as well
VCN_LOGGER  = logging.getLogger(__name__)

Resources_dir = Path(__file__).resolve().parent.parent.parent
Report_storage_dir= Resources_dir / 'Components' /'Import_file_data'

# ============================================================================
# generate_report: main method to generate report
# ============================================================================
def	generate_tuple(list_1,card,prov):
	tuply = (list_1,card,prov)
	return	tuple(tuply)


def generate_report(list_1,card,prov='ixusb'):
	global part_amount_req, card_amount, bal_amount, part_amount
	part_amount_req=''
	card_amount=''
	bal_amount=''
	part_amount=''

	l_authreport = ''
	l_FAreport = ''
	l_cardreport = ''
	l_settreport = ''
	l_statusreport = ''
	l_bom_expected = {"PaymentTransactions":[],"Transactions":[]}

	if prov.lower() == 'citibank' :
		aCitiBankVirtualCreditCard = VirtualCard('citibank')
		aCitiBankVirtualCreditCard.add_list_transaction(list_1, card)

		report, bom = aCitiBankVirtualCreditCard.generate_transactions_report()
		return report, bom

	if prov.lower() == 'ixusb':
		for type in list_1:
			indice=list_1.index(type)
			report1, report2, report3 = ixusb_generate_transaction(indice, type, *card)
			l_FAreport += report1
			l_cardreport += report2
			for tr in report3:
				l_bom_expected[tr].append(report3[tr])
				tr_index = l_bom_expected[tr].index(report3[tr])
				if tr == "Transactions":
					if card[11] != '':
						l_bom_expected[tr][tr_index].update({"AdditionalInfo": {"Item":[]}})
						for i in range(11,15):
							if card[i] != '':
								l_bom_expected[tr][tr_index]["AdditionalInfo"]["Item"].append({"ShortName": card[i].split(":")[0].strip(),"Type": "CardInfo","Value": card[i].split(":")[1].strip()})

		return str(l_FAreport),str(l_cardreport),l_bom_expected

	if prov.lower() == 'apiso':
		for type in list_1:
			indice=list_1.index(type)
			report1, report2, report3, report4, report5 = apiso_generate_transaction(indice, type, *card)
			VCN_LOGGER.info("CardLoad:" + report1)
			VCN_LOGGER.info("report2:" + report2)
			VCN_LOGGER.info("report3:" + report3)
			VCN_LOGGER.info("report4:" + report4)
			VCN_LOGGER.info(report5)
			if report1:
				l_cardreport += report1
			if report2:
				l_authreport += report2
			if report3:
				l_settreport += report3
			if report4:
				l_statusreport = report4
			for tr in report5:
				l_bom_expected[tr].append(report5[tr])
				tr_index = l_bom_expected[tr].index(report5[tr])
				if tr == "Transactions":
					if "CREATION" in tr:
						if card[10] != '':
							l_bom_expected[tr][tr_index].update({"AdditionalInfo": {"Item":[]}})
							for i in range(10,14):
								if card[i] != '':
									l_bom_expected[tr][tr_index]["AdditionalInfo"]["Item"].append({"ShortName": card[i].split("-")[0].strip(),"Type": "CardInfo","Value": card[i].split("-")[1].strip()})

		output = [l_bom_expected]
		if l_statusreport!='':
			output.insert(0,str(l_statusreport))
			VCN_LOGGER.info("-----l_statusreport present-----")
			VCN_LOGGER.info(l_statusreport)
		if l_settreport!='':
			output.insert(0,str(l_settreport))
			VCN_LOGGER.info("-----l_settreport present-----")
			VCN_LOGGER.info(l_settreport)
		if l_authreport!='':
			output.insert(0,str(l_authreport))
			VCN_LOGGER.info("-----l_authreport present-----")
			VCN_LOGGER.info(l_authreport)
		if l_cardreport!='':
			output.insert(0,str(l_cardreport))
			VCN_LOGGER.info("-----l_cardreport present-----")
			VCN_LOGGER.info(l_cardreport)
		VCN_LOGGER.info("output :")
		VCN_LOGGER.info(tuple(output))
		return tuple(output)


# ===========================================================================================================
# ixusb_generate_transaction: sub function method to generate Ixaris and USbank reports (transaction part)
# ===========================================================================================================

def ixusb_generate_transaction(indice, type, *args):
	global part_amount_req, card_amount, bal_amount, part_amount
	print("Type generate_report:", type)

	date_ref=datetime.datetime.utcnow() + datetime.timedelta(seconds=indice)
	date=str(date_ref.strftime("%Y-%m-%d %H:%M:%S"))
	date_provider=str((date_ref + datetime.timedelta(hours=1)).strftime("%Y-%m-%d 00:00:00.000"))
	AdjId='ADJID_' + date_ref.strftime("%Y%m%d%H%M%S") + '_' + getRandomAlphanumeric(5)

	card_trx_status = args[3]


	if args[16]!='':
		card_amount_req = float(args[2])
		card_currency_req = args[1]
		card_amount = float(args[16])
		card_currency = args[17]
		exch_rate = card_amount_req/card_amount
		forex_fee = "{0:.2f}".format(0.8 * card_amount)

	else:
		card_amount = card_amount_req = float(args[2])
		card_currency = card_currency_req = args[1]
		exch_rate = 1

		# Catch MCC code and check if the it's present in VCN_report_generator_Input_data
		if args[15] in List_keys :
			merchantName = MerchantDict[args[15]]['merchantName']
			merchantCountry = MerchantDict[args[15]]['merchantCountry']
			merchantCategoryCode = MerchantDict[args[15]]['merchantCategoryCode']
		else:
		# if MCC isn't corresponding to any of MCC in VCN_report_generator_Input_data, push Hard coded values
			merchantName = 'JETSTAR AIR            AUSTRALIA     AUS                                                             '
			merchantCountry = 'AU'
			merchantCategoryCode = '3079'


	if indice == 0 and args[0] != '':
		TrnId = args[0]
	else:
		TrnId='TRNID_' + date_ref.strftime("%Y%m%d%H%M%S")+ '_' +getRandomAlphanumeric(5)

	FAreport = ''
	cardreport = ''
	if args[9] == 'VI':
		vendor = 'VISA'
		factory = '1a_vi_12m'
		nonforexfee = '0.800000000'
	else:
		vendor = 'MASTERCARD'
		factory = '1a_ca_12m'
		nonforexfee = '0.000000000'

	if int(args[10])==1:
		factory = factory + '_ss'
	else:
		factory = factory + '_ms'

	#USBANK Report generation
	if type.split('_')[0] == "USB":
		if bal_amount == '':
			bal_amount = card_amount
			if type.split("_")[1]>'0':
				USB_tr_type = type.split("_")[1]
				if USB_tr_type == 'P':
					if type.split("_")[2]>'0':
						part_amount = float(type.split("_")[2])
						part_amount_req = part_amount*exch_rate
						VCN_LOGGER.info( "USBank Partial Settlement: " + str(part_amount_req) + " " + card_currency)
						amount_before = bal_amount
						part_amount = part_amount_req/exch_rate
						amount_after = bal_amount - part_amount
						bal_amount = amount_after
					else:
						amount_before = part_amount = bal_amount
						part_amount_req = part_amount*exch_rate
						bal_amount = amount_after = 0.00
				elif USB_tr_type == 'C':
					if type.split("_")[2]>'0':
						part_amount = float(type.split("_")[2])
						part_amount_req = part_amount*exch_rate
						VCN_LOGGER.info( "USBank Partial Refund: " + str(part_amount_req) + " " + card_currency)
						amount_before = bal_amount
						part_amount = part_amount_req/exch_rate
						amount_after = bal_amount + part_amount
						bal_amount = amount_after
					else:
						amount_before = part_amount = bal_amount
						part_amount_req = part_amount*exch_rate
						amount_after = bal_amount + part_amount
					part_amount = -part_amount
					part_amount_req = -part_amount_req
			else:
				USB_tr_type = 'P'


		#date_ref_BEFORE_AFTER = datetime.datetime.utcnow() - datetime.timedelta(100) + datetime.timedelta(seconds=indice)  # before
		#date_ref_BEFORE_AFTER = datetime.datetime.utcnow() + datetime.timedelta(100) + datetime.timedelta(seconds=indice)  # after
		date_ref_BEFORE_AFTER = date_ref # normal
		print("lolololo: ", date_ref_BEFORE_AFTER)

		cardreport = str(date_ref.strftime("%m/%d/%Y")) + ',' + str(date_ref_BEFORE_AFTER.strftime("%m/%d/%Y")) + ',' + TrnId + ',"amadeus","USA",' + args[5] + ',' + args[7] + 'XXXXXX' + args[8] +',440910110,' + type.split('_')[1] + ',3001,556904XXXXXX0272,' \
			+ str(part_amount_req) + ',' + card_currency + ',' + str(part_amount) + ',' + card_currency + ',DELTA     00670705262916,USA,3058,,,' + args[3] + ',61846,' \
			+ args[11] + ',' + args[12] + ',' + args[13] + ',' + args[14] + ',' + args[15] + ',,,,,,,,,,'

		bom_Expected={ "PaymentTransactions": {
			"AmountRequested": {
				"Amount": str(part_amount_req),
				"Currency": card_currency_req
			},
			"ApprovalCode": "61846",
			"Merchant": {
				"Name": "DELTA     00670705262916",
				"Country": "USA",
				"MCC": "3058"
			},
			"ExternalTransactionId": TrnId,
			"TransactionAmount": {
				"Amount": str(part_amount),
				"Currency": card_currency
			},
			"TransactionDateTime": {
				"Creation": str(date_ref.strftime("%Y-%m-%d 00:00:00.000")),
				"Processed": str(date_ref.strftime("%Y-%m-%d 00:00:00.000")),
				"ReadyToReport": str(date_ref.strftime("%Y-%m-%d 00:00:00.000"))
			},
			"TransactionStatus": {
				"ActionStatus": "OK",
				"PluginStatus": card_trx_status,
				"Timestamp": str(date_ref.strftime("%Y-%m-%d 00:00:00.000"))
			},
			"Type": OtherTypes(USB_tr_type)[1]
		}}

	elif type.split("_")[0] == "CARD CREATED":
		bal_amount = card_amount
		cardreport = '"'+ date + '.910","' + date + '.911",' + '"Amadeus","amamadeus#amamadeus","' + \
			TrnId + '","' + AdjId + '","' + type + '","' + card_currency + '","' + str(card_amount) + '","Funding Account","' + args[3] + \
			'","Virtual Card","' + args[4] + '","Virtual Card","' + args[4] + '","DESTINATION","' + card_currency + '","' + str(card_amount) + '","' + card_currency + '","' + str(card_amount) + \
			'","1.000000000","0.000000000","0.000000000","0.00","' + str(card_amount) + '","' + str(card_amount) + '","COMPLETED","N","A","","","","","","","' + args[5] + '","' + args[6] + '","' + \
			args[7] + '******' + args[8] + '","' + vendor + '","' + factory + '","' + args[11] + '","' + args[12] + '","' + args[13] + '","' + args[14] + \
			'","' + args[15] + '",""'
		FAreport = '"'+ date + '.910","' + date + '.911",' + '"Amadeus","amamadeus#amamadeus","FRANCE","' + \
			TrnId + '","' + AdjId + '","' + type + '","' + card_currency + '","' + str(card_amount) + '","test.regression","Funding Account","' + args[3] + \
			'","Virtual Card","' + args[4] + '","Funding Account","' + args[3] + '","SOURCE","' + card_currency + '","-' + str(card_amount) + '","' + card_currency + '","-' + str(card_amount) + '","1.000000000","'+nonforexfee+'","0.000000000","100000","-' + \
			str(card_amount) + '","99999","COMPLETED","N","A","FANumber_Test",""'
		bom_Expected={ "Transactions": {
			"AmountRequested": {
				"Amount": str(card_amount),
				"Currency": card_currency
			},
		"AmountLoaded": {
			"Amount": str(card_amount),
			"Currency": card_currency
		},
			"BalanceAfter": {
				"Amount": str(card_amount),
				"Currency": card_currency
			},
			"CardGenerationFee": {
					"Amount": nonforexfee,
					"Currency": card_currency
			},
			"Source": "IMPORT",
			"Link": "VCCIX",
			"CardFactory": factory,
			"BalanceBefore": {
				"Amount": "0.00",
				"Currency": card_currency
			},
			"ExternalTransactionId": TrnId,
			"TransactionDateTime": {
				"Creation": date + '.910',
				"Processed": date + '.911' ,
				"ReadyToReport": date
			},
			"TransactionStatus": {
				"ActionCode": "CA",
				"ActionStatus": "OK",
				"Timestamp": date + '.911'
			},
			"Type": OtherTypes(type.split("_")[0])[1]
		}}

	#AUTHORISATION Partial Amount Has to be in FA Currency: EUR in this test
	elif type.split("_")[0] == "AUTHORISATION":
		if type.split("_")[1] == "OK":
			try:
				if type.split("_")[2]>'0':
					part_amount = float(type.split("_")[2])
					part_amount_req = part_amount*exch_rate
					print("Author Partial Amount: " + str(part_amount_req) + " " + card_currency)
					cardreport = '"'+ date + '.920","' + date + '.921",' + '"Amadeus","amamadeus#amamadeus","' + \
						TrnId + '","' + AdjId + '","' + type.split("_")[0] + '","' + card_currency + '","-' + str(part_amount) + '","Virtual Card","' + args[4] + \
						'","Provider","","Virtual Card","' + args[4] + '","SOURCE","' + card_currency_req + '","-' + str(part_amount_req) + '","' + card_currency + '","0.00","'+str(exch_rate)+'","0.000000000","0.000000000","' + \
						str(card_amount) + '","0.00","' + str(card_amount) + \
						'","COMPLETED","N","A","' + merchantName + '","' + merchantCountry + '","' + merchantCategoryCode + '","","111111","' + date_provider + '","' \
						+ args[5] + '","' + args[6] + '","' + \
						args[7] + '******' + args[8] + '","' + vendor + '","' + factory + '","' + args[11] + '","' + args[12] + '","' + args[13] + '","' + args[14] + \
						'","' + args[15] + '","NORMAL_TAKE"'
					bom_Expected={ "PaymentTransactions": {
						"AmountRequested": {
							"Amount": '-' + str(part_amount_req),
							"Currency": card_currency_req
						},
						"ApprovalCode": "111111",
						"BalanceAfter": {
							"Amount": str(card_amount),
							"Currency": card_currency
						},
						"BalanceBefore": {
							"Amount": str(card_amount),
							"Currency": card_currency
						},
						"ForexFeeAmount": {
							"Amount": "0.0",
							"Currency": "EUR"
						},
						"Merchant": {
							"Country": "AU",
							"MCC": "3079"
						},
						"ExternalTransactionId": TrnId,
						"TransactionAmount": {
							"Amount": '-' + str(part_amount),
							"Currency": card_currency
						},
						"TransactionDateTime": {
							"Creation": date,
							"Processed": date_provider,
							"ReadyToReport": date
						},
						"TransactionStatus": {
							"ActionStatus": "OK",
							"PluginStatus": "COMPLETED",
							"ResponseCode": "NORMAL_TAKE",
							"Timestamp": date
						},
						"Type": OtherTypes(type.split("_")[0])[1]
					}}
					VCN_LOGGER.info(bom_Expected)
			except:
				cardreport = '"'+ date + '.920","' + date + '.921",' + '"Amadeus","amamadeus#amamadeus","' + \
					TrnId + '","' + AdjId + '","' + type.split("_")[0] + '","' + card_currency + '","-' + str(card_amount) + '","Virtual Card","' + args[4] + \
					'","Provider","","Virtual Card","' + args[4] + '","SOURCE","' + card_currency_req + '","-' + str(card_amount_req) + '","' + card_currency + '","0.00","'+str(exch_rate)+'","0.000000000","0.000000000","' + \
					str(card_amount) + '","0.00","' + str(card_amount) + \
					'","COMPLETED","N","A","' + merchantName + '","' + merchantCountry + '","' + merchantCategoryCode + '","","111111","' + date_provider + '","' \
					+ args[5] + '","' + args[6] + '","' + \
					args[7] + '******' + args[8] + '","' + vendor + '","' + factory + '","' + args[11] + '","' + args[12] + '","' + args[13] + '","' + args[14] + \
					'","' + args[15] + '","NORMAL_TAKE"'
				print('cardreport',cardreport)

				bom_Expected={ "PaymentTransactions": {
					"AmountRequested": {
						"Amount": '-' + str(card_amount_req),
						"Currency": card_currency_req
					},
					"ApprovalCode": "111111",
					"BalanceAfter": {
						"Amount": str(card_amount),
						"Currency": card_currency
					},
					"BalanceBefore": {
						"Amount": str(card_amount),
						"Currency": card_currency
					},
					"ForexFeeAmount": {
						"Amount": "0.0",
						"Currency": "EUR"
					},
					"Merchant": {
						"Country": "AU",
						"MCC": "3079"
					},
					"ExternalTransactionId": TrnId,
					"TransactionAmount": {
						"Amount": '-' + str(card_amount),
						"Currency": card_currency
					},
					"TransactionDateTime": {
						"Creation": date,
						"Processed": date_provider,
						"ReadyToReport": date
					},
					"TransactionStatus": {
						"ActionStatus": "OK",
						"PluginStatus": "COMPLETED",
						"ResponseCode": "NORMAL_TAKE",
						"Timestamp": date
					},
					"Type": OtherTypes(type.split("_")[0])[1]
				}}
				VCN_LOGGER.info(bom_Expected)

		elif type.split("_")[1] == "KO":
			cardreport = '"'+ date + '.920","' + date + '.921",' + '"Amadeus","amamadeus#amamadeus","' + \
					TrnId + '","' + AdjId + '","' + type.split("_")[0] + '","' + card_currency + '","-' + str(card_amount) + '","Virtual Card","' + args[4] + \
					'","","","Virtual Card","' + args[4] + '","SOURCE","' + card_currency_req + '","-' + str(card_amount_req) + '","' + card_currency + \
					'","0.00","'+str(exch_rate)+'","0.000000000","0.000000000","0.00","0.00","0.00","COMPLETED","Y","A","' + merchantName + '","' + merchantCountry + '","' + merchantCategoryCode + '","","999999","' + date_provider + '","' \
					+ args[5] + '","' + args[6] + '","' + \
					args[7] + '******' + args[8] + '","' + vendor + '","' + factory + '","' + args[11] + '","' + args[12] + '","' + args[13] + '","' + args[14] + \
					'","' + args[15] + '","DECLINED_TAKE : Insufficient funds/over credit limit"'

			bom_Expected={ "PaymentTransactions": {
				"AmountRequested": {
					"Amount": '-' + str(card_amount),
					"Currency": card_currency
				},
				"ApprovalCode": "999999",
				"BalanceAfter": {
					"Amount": "0.00",
					"Currency": card_currency
				},
				"BalanceBefore": {
					"Amount": "0.00",
					"Currency": card_currency
				},
				"ForexFeeAmount": {
					"Amount": "0.0",
					"Currency": "EUR"
				},
				"Merchant": {
					"Country": "AU",
					"MCC": "3079"
				},
				"ExternalTransactionId": TrnId,
				"TransactionAmount": {
					"Amount": '-' + str(card_amount),
					"Currency": card_currency
				},
				"TransactionDateTime": {
					"Creation": date,
					"Processed": date_provider,
					"ReadyToReport": date
				},
				"TransactionStatus": {
					"ActionStatus": "OK",
					"PluginStatus": "COMPLETED",
					"ResponseCode": "DECLINED_TAKE : Insufficient funds/over credit limit",
					"Timestamp": date
				},
				"Type": OtherTypes(type.split("_")[0])[1]
			}}

	if type.split("_")[0] == "MERCHANT REFUND":
		if bal_amount == '':
			bal_amount = float('0.00')
		try:
			if type.split("_")[1]>'0':
				refund_amount = float(type.split("_")[1])
				amount_before = bal_amount
				amount_after = bal_amount + refund_amount
				bal_amount = amount_after
		except:
			if part_amount != '':
				refund_amount = part_amount
				amount_before = bal_amount
				amount_after = bal_amount + refund_amount
				bal_amount = amount_after
			else:
				amount_before = refund_amount = bal_amount
				bal_amount = amount_after = refund_amount + bal_amount

		cardreport = '"' + date + '.970","' + date + '.971",' \
			+ '"Amadeus","amamadeus#amamadeus","' + TrnId + '","' + AdjId + '","' + type.split("_")[0] + '","' + card_currency + '","' + str(refund_amount) + '","Provider","","Virtual Card","' + args[4] + '","Virtual Card","' + args[4] \
			+ '","DESTINATION","' + card_currency + '","' + str(refund_amount) + '","' + card_currency + '","' + str(refund_amount) + '","1.000000000","0.000000000","0.000000000","'  \
			+ str(amount_before) + '","' + str(refund_amount) + '","' + str(amount_after) + '","COMPLETED","Y","A","' + merchantName + '","' + merchantCountry + '","' + merchantCategoryCode + '","","999999","' + date_provider+ '","' \
			+ args[5] + '","' + args[6] + '","' + args[7] + '******' + args[8] + '","' + vendor + '","' + factory + '","' + args[11] + '","' + args[12] + '","' + args[13] + '","' + args[14] + '","' + args[15] + '","","-2.99","' + card_currency + '"'

		bom_Expected={ "PaymentTransactions": {
			"AmountRequested": {
				"Amount": str(refund_amount),
				"Currency": card_currency
			},
			"BalanceAfter": {
				"Amount": str(amount_after),
				"Currency": card_currency
			},
			"BalanceBefore": {
				"Amount": str(amount_before),
				"Currency": card_currency
			},
			"ForexFeeAmount": {
				"Amount": "0.0",
				"Currency": "EUR"
			},
			"Merchant": {
				"Country": "AU",
				"MCC": "3079"
			},
			"ExternalTransactionId": TrnId,
			"TransactionAmount": {
				"Amount": str(refund_amount),
				"Currency": card_currency
			},
			"TransactionDateTime": {
				"Creation": date,
				"Processed": date_provider,
				"ReadyToReport": date
			},
			"TransactionStatus": {
				"ActionStatus": "OK",
				"PluginStatus": "COMPLETED",
				"Timestamp": date
			},
			"Type": OtherTypes(type.split("_")[0])[1]
		}}


	if type.split("_")[0] == "AUTHORISATION RELEASE":
		if part_amount == '':
			part_amount = card_amount
		cardreport = '"' + date + '.940","' + date + '.941",' \
			+ '"Amadeus","amamadeus#amamadeus","' + TrnId + '","' + AdjId + '","' + type + '","' + card_currency + '","' + str(part_amount) + '","","","Virtual Card","' + args[4] + '","Virtual Card","' + args[4]\
			+ '","DESTINATION","' + card_currency + '","-' + str(part_amount) + '","' + card_currency + '","0.00","1.000000000","0.000000000","0.000000000","' \
			+ str(card_amount) + '","0.00","' + str(card_amount) + '","COMPLETED","N","A","' + merchantName + '","' + merchantCountry + '","' + merchantCategoryCode + '","","999999",' + date_provider + ',"' \
			+ args[5] + '","' + args[6] + '","' + args[7] + '******' + args[8] + '","' + vendor + '","' + factory + '","' + args[11] + '","' + args[12] + '","' + args[13] + '","' + args[14] + '","' + args[15] + '","REVERSE_TAKE"'

		bom_Expected={ "PaymentTransactions": {
			"AmountRequested": {
				"Amount": '-' + str(part_amount),
				"Currency": card_currency
			},
			"BalanceAfter": {
				"Amount": str(card_amount),
				"Currency": card_currency
			},
			"BalanceBefore": {
				"Amount": str(card_amount),
				"Currency": card_currency
			},
			"ForexFeeAmount": {
				"Amount": "0.0",
				"Currency": "EUR"
			},
			"Merchant": {
				"Country": "AU",
				"MCC": "3079"
			},
			"ExternalTransactionId": TrnId,
			"TransactionAmount": {
				"Amount": str(part_amount),
				"Currency": card_currency
			},
			"TransactionDateTime": {
				"Creation": date,
				"Processed": date_provider,
				"ReadyToReport": date
			},
			"TransactionStatus": {
				"ActionStatus": "OK",
				"ResponseCode": "REVERSE_TAKE",
				"PluginStatus": "COMPLETED",
				"Timestamp": date
			},
			"Type": OtherTypes(type.split("_")[0])[1]
		}}

	elif type.split("_")[0] == "FREEZE":
		cardreport = '"'+ date + '.930","' + date + '.931",' + '"Amadeus","amamadeus#amamadeus","' + \
			TrnId + '","' + AdjId + '","' + type + '","' + card_currency + '","0.00","Virtual Card","' + args[4] + \
			'","Provider","","Virtual Card","' + args[4] + '","SOURCE","' + card_currency + '","0.00","' + card_currency + '","0.00","1.000000000","0.000000000","0.000000000","' + \
			str(card_amount) + '","0.00","' + str(card_amount) + \
			'","COMPLETED","N","A","' + merchantName + '","' + merchantCountry + '","' + merchantCategoryCode + '","","111111",'+ date_provider+ ',"' \
			+ args[5] + '","' + args[6] + '","' + \
			args[7] + '******' + args[8] + '","' + vendor + '","' + factory + '","' + args[11] + '","' + args[12] + '","' + args[13] + '","' + args[14] + \
			'","' + args[15] + '","NORMAL_TAKE"'
		bom_Expected={ "Transactions": {
			"AmountLoaded": {
				"Amount": "0.00",
				"Currency": card_currency
			},
			"AmountRequested": {
				"Amount": "0.00",
				"Currency": card_currency
			},
			"BalanceAfter": {
				"Amount": str(card_amount),
				"Currency": card_currency
			},
			"CardFactory": factory,
			"BalanceBefore": {
				"Amount": str(card_amount),
				"Currency": card_currency
			},
			"ExternalTransactionId": TrnId,
			"Source": "IMPORT",
			"TransactionDateTime": {
				"Creation": date + '.930',
				"Processed": date + '.931' ,
				"ReadyToReport": date
			},
			"TransactionStatus": {
				"ActionCode": "FZ",
				"ActionStatus": "OK",
				"ResponseCode": "NORMAL_TAKE",
				"Timestamp": date + '.931'
			},
			"Type": OtherTypes(type.split("_")[0])[1]
		}}

	elif type.split("_")[0] == "THAW":
		cardreport = '"'+ date + '.950","' + date + '.951",' + '"Amadeus","amamadeus#amamadeus","' + \
			TrnId + '","' + AdjId + '","' + type + '","' + card_currency + '","0.00","","","Virtual Card","' + args[4] + '","Virtual Card","' + args[4] + '","DESTINATION","' \
			+ card_currency + '","0.00","' + card_currency + '","0.00","1.000000000","0.000000000","0.000000000","' + str(card_amount) + '","0.00","' + str(card_amount) \
			+ '","COMPLETED","N","A","' + merchantName + '","' + merchantCountry + '","' + merchantCategoryCode + '","","111111",'+ date_provider+ ',"' \
			+ args[5] + '","' + args[6] + '","' + \
			args[7] + '******' + args[8] + '","' + vendor + '","' + factory + '","' + args[11] + '","' + args[12] + '","' + args[13] + '","' + args[14] + \
			'","' + args[15] + '","REVERSE_TAKE"'

		bom_Expected={ "Transactions": {
			"AmountLoaded": {
				"Amount": "0.00",
				"Currency": card_currency
			},
			"AmountRequested": {
				"Amount": "0.00",
				"Currency": card_currency
			},
			"BalanceAfter": {
				"Amount": str(card_amount),
				"Currency": card_currency
			},
			"CardFactory": factory,
			"BalanceBefore": {
				"Amount": str(card_amount),
				"Currency": card_currency
			},
			"ExternalTransactionId": TrnId,
      "Source": "IMPORT",
			"TransactionDateTime": {
				"Creation": date + '.950',
				"Processed": date + '.951' ,
				"ReadyToReport": date
			},
			"TransactionStatus": {
				"ActionCode": "TH",
				"ActionStatus": "OK",
				"ResponseCode": "REVERSE_TAKE",
				"Timestamp": date + '.951'
			},
			"Type": OtherTypes(type.split("_")[0])[1]
		}}
	elif type.split('_')[0] == "PURCHASE":
		if bal_amount == '':
			bal_amount = card_amount
		if part_amount_req != '':
			amount_before = bal_amount
			part_amount = part_amount_req/exch_rate-2
			amount_after = bal_amount - part_amount
			bal_amount = amount_after
		else:
			amount_before = part_amount = bal_amount
			part_amount_req = part_amount*exch_rate
			bal_amount = amount_after = 0.00

		cardreport = '"' + date + '.960","' + date + '.961",' \
			+ '"Amadeus","amamadeus#amamadeus","' + TrnId + '","' + AdjId + '","' + type.split('_')[0] + '","' + card_currency + '","-' + str(part_amount) + '","Virtual Card","' + args[4] \
			+ '","Provider","","Virtual Card","' + args[4] + '","SOURCE","' + card_currency_req + '","-' + str(part_amount_req) + '","' + card_currency + '","-' + str(part_amount) + '","'+str(1/exch_rate)+'","0.000000000","2.00","' \
			+ str(amount_before) + '","-' + str(part_amount) + '","' + str(amount_after) + '","COMPLETED","N","A","' + merchantName + '","' + merchantCountry + '","' + merchantCategoryCode + '","75353107175906001643167","111111",' + date_provider + ',"' \
			+ args[5] + '","' + args[6] + '","' + args[7] + '******' + args[8] + '","' + vendor + '","' + factory + '","' + args[11] + '","' + args[12] + '","' + args[13] + '","' + args[14] + '","' + args[15] + '","","1.99","' + card_currency + '"'

		bom_Expected={ "PaymentTransactions": {
			"AmountRequested": {
				"Amount": '-' + str(part_amount_req),
				"Currency": card_currency_req
			},
			"BalanceAfter": {
				"Amount": str(amount_after),
				"Currency": card_currency
			},
			"BalanceBefore": {
				"Amount": str(amount_before),
				"Currency": card_currency
			},
			"ForexFeeAmount": {
				"Amount": "2.0",
				"Currency": "EUR"
			},
			"Merchant": {
				"Country": "AU",
				"MCC": "3079"
			},
			"ExternalTransactionId": TrnId,
			"TransactionAmount": {
				"Amount": '-' + str(part_amount),
				"Currency": card_currency
			},
			"InterchangeAmount": {
				"Amount": "1.99",
				"Currency": card_currency
			},
			"TransactionDateTime": {
				"Creation": date,
				"Processed": date_provider,
				"ReadyToReport": date
			},
			"TransactionStatus": {
				"ActionStatus": "OK",
				"PluginStatus": "COMPLETED",
				"Timestamp": date
			},
			"Type": OtherTypes(type.split("_")[0])[1]
		}}

	# Partial Amounts for DELETE / TRANSFER have to be in EUR
	elif type.split("_")[0] == "CARD DELETED" or (type.split("_")[0] == "TRANSFER" and len(type.split("_")) == 1):
		if bal_amount == '':
			bal_amount = card_amount
		try:
			if type.split("_")[1]>'0':
				delete_amount = float(type.split("_")[1])
				amount_before = bal_amount
				amount_after = bal_amount - delete_amount
				bal_amount = amount_after
		except:
			amount_before = delete_amount = bal_amount
			amount_after = bal_amount - delete_amount
			bal_amount = amount_after

		cardreport = '"'+ date + '.980","' + date + '.981",' + '"Amadeus","amamadeus#amamadeus","' \
			+ TrnId + '","' + AdjId + '","' + type.split("_")[0] + '","' + card_currency + '","' + str(delete_amount) + '","Virtual Card","' + args[4] + '","Funding Account","' + args[3] \
			+ '","Virtual Card","' + args[4] + '","SOURCE","' + card_currency + '","-' + str(delete_amount) + '","' + card_currency + '","-' + str(delete_amount) + '","1.000000000","0.000000000","0.000000000","' \
			+ str(amount_before) + '","-' + str(delete_amount) + '","' + str(amount_after) + '","COMPLETED","N","A","","","","","","","' + args[5] + '","' + args[6] + '","' \
			+ args[7] + '******' + args[8] + '","' + vendor + '","' + factory + '","' + args[11] + '","' + args[12] + '","' + args[13] + '","' + args[14] + '","' + args[15] + '",""'

		if delete_amount>0:
			FAreport = '"'+ date + '.980","' + date + '.981",' + '"Amadeus","amamadeus#amamadeus","FRANCE","' + \
				TrnId + '","' + AdjId + '","TRANSFER","' + card_currency + '","' + str(delete_amount) + '","test.regression","Virtual Card","' + args[4] + '","Funding Account","' + args[3] + '","Funding Account","' + args[3] \
				+ '","DESTINATION","' + card_currency + '","' + str(delete_amount) + '","' + card_currency + '","' + str(delete_amount) + '","1.000000000","0.000000000","0.000000000","99999","' \
				+ str(delete_amount) + '","100000","COMPLETED","N","A","FANumber_Test",""'

		bom_Expected={ "Transactions": {
			"AmountLoaded": {
				"Amount": str(delete_amount),
				"Currency": card_currency
			},
			"AmountRequested": {
				"Amount": '-' + str(delete_amount),
				"Currency": card_currency
			},
			"BalanceAfter": {
				"Amount": str(amount_after),
				"Currency": card_currency
			},
			"BalanceBefore": {
				"Amount": str(amount_before),
				"Currency": card_currency
			},
			"ExternalTransactionId": TrnId,
			"Source": "IMPORT",
			"TransactionDateTime": {
				"Creation": date + '.980',
				"Processed": date + '.981' ,
				"ReadyToReport": date
			},
			"TransactionStatus": {
				"ActionCode": "RV",
				"ActionStatus": "OK",
				"Timestamp": date + '.981'
			},
			"Type": OtherTypes(type.split("_")[0])[1]
		}}

	elif type.split("_")[0] == "TRANSFER" and len(type.split("_"))>1:
		if bal_amount == '':
			bal_amount = card_amount
		transfer_amount = float(type.split("_")[1])
		amount_before = bal_amount
		amount_after = bal_amount + transfer_amount
		bal_amount = amount_after

		cardreport = '"'+ date + '.990","' + date + '.991",' + '"Amadeus","amamadeus#amamadeus","' \
			+ TrnId + '","' + AdjId + '","' + type.split("_")[0] + '","' + card_currency + '","' + str(transfer_amount) + '","Funding Account","' + args[3] + '","Virtual Card","' + args[4] \
			+ '","Virtual Card","' + args[4] + '","DESTINATION","' + card_currency + '","' + str(transfer_amount) + '","' + card_currency + '","' + str(transfer_amount) + '","1.000000000","0.000000000","0.000000000","' \
			+ str(amount_before) + '","' + str(transfer_amount) + '","' + str(amount_after) + '","COMPLETED","N","A","","","","","","","' + args[5] + '","' + args[6] + '","' \
			+ args[7] + '******' + args[8] + '","' + vendor + '","' + factory + '","' + args[11] + '","' + args[12] + '","' + args[13] + '","' + args[14] + '","' + args[15] + '",""'

		FAreport = '"'+ date + '.990","' + date + '.991",' + '"Amadeus","amamadeus#amamadeus",""FRANCE","' + \
			TrnId + '","' + AdjId + '","TRANSFER","' + card_currency + '","' + str(transfer_amount) + '","test.regression","Funding Account","' + args[3] + '","Virtual Card","' + args[4] + '","Funding Account","' + args[3] \
			+ '","SOURCE","' + card_currency + '","-' + str(transfer_amount) + '","' + card_currency + '","-' + str(transfer_amount) + '","1.000000000","0.000000000","0.000000000","99999","-' \
			+ str(transfer_amount) + '","100000","COMPLETED","N","A","FANumber_Test",""'

		bom_Expected={ "Transactions": {
			"AmountLoaded": {
				"Amount": str(transfer_amount),
				"Currency": card_currency
			},
			"AmountRequested": {
				"Amount": str(transfer_amount),
				"Currency": card_currency
			},
			"BalanceAfter": {
				"Amount": str(amount_after),
				"Currency": card_currency
			},
			"BalanceBefore": {
				"Amount": str(amount_before),
				"Currency": card_currency
			},
			"ExternalTransactionId": TrnId,
			"Source": "IMPORT",
			"TransactionDateTime": {
				"Creation": date + '.990',
				"Processed": date + '.991' ,
				"ReadyToReport": date
			},
			"TransactionStatus": {
				"ActionCode": "RV",
				"ActionStatus": "OK",
				"Timestamp": date + '.991'
			},
			"Type": OtherTypes(type.split("_")[0])[1]
		}}
	elif type.split("_")[0] == "BANK DEPOSIT":
		FAreport = '"'+ date + '.910","' + date + '.911",' + '"Amadeus","amamadeus#amamadeus","FRANCE","' + \
			TrnId + '","' + AdjId + '","BANK DEPOSIT","' + card_currency + '","' + str(card_amount) + '","System","Bank Account","Bank Transfer In","Funding Account","FundingAccountEUR","Funding Account","FundingAccountEUR","DESTINATION","' + card_currency + '","-' + str(card_amount) + '","' + card_currency + '","-' + str(card_amount) + '","1.000000000","0.0000000","0.000000000","100000","-' + \
			str(card_amount) + '","99999","COMPLETED","N","A","FANumber_Test",""'
		bom_Expected={}

	elif type.split("_")[0] == "BANK DEPOSIT REVERSAL":
		FAreport = '"'+ date + '.910","' + date + '.911",' + '"Amadeus","amamadeus#amamadeus","FRANCE","' + \
			TrnId + '","' + AdjId + '","BANK DEPOSIT REVERSAL","' + card_currency + '","' + str(card_amount) + '","System","Funding Account","FundingAccountEUR","Bank Account","Bank Transfer In","Funding Account","FundingAccountEUR","SOURCE","' + card_currency + '","-' + str(card_amount) + '","' + card_currency + '","-' + str(card_amount) + '","1.000000000","0.0000000","0.000000000","100000","-' + \
			str(card_amount) + '","99999","COMPLETED","N","A","FANumber_Test",""'
		bom_Expected={}

	elif type.split("_")[0] == "FEE REVERSAL" :
		FAreport = '"'+ date + '.910","' + date + '.911",' + '"Amadeus","amamadeus#amamadeus","FRANCE","' + \
			TrnId + '","' + AdjId + '","FEE REVERSAL","' + card_currency + '","0","Operator","Charge","","Funding Account","FundingAccountEUR","Funding Account","FundingAccountEUR","DESTINATION","' + card_currency + '","0","' + card_currency + '","0","1.000000000","-0.9","0","0.4","0.9","1.3","COMPLETED","N","A","FANumber_Test",""'
		bom_Expected={}

	elif type.split("_")[0] == "FUNDING ACCOUNT CREATED" :
		FAreport = '"'+ date + '.910","' + date + '.911",' + '"Amadeus","amamadeus#amamadeus","FRANCE","' + \
			TrnId + '","' + AdjId + '","FUNDING ACCOUNT CREATED","' + card_currency + '","0","System","","","Funding Account","FundingAccountEUR","Funding Account","FundingAccountEUR","DESTINATION","' + card_currency + '","0","' + card_currency + '","0","1","0","0.000000000","0.000000000","0.000000000","0.00","COMPLETED","N","A","FANumber_Test",""'
		bom_Expected={}

	elif type.split("_")[0] == "FUNDING ACCOUNT DELETED" :
		FAreport = '"'+ date + '.910","' + date + '.911",' + '"Amadeus","amamadeus#amamadeus","FRANCE","' + \
			TrnId + '","' + AdjId + '","FUNDING ACCOUNT DELETED","' + card_currency + '","0","System","","","Funding Account","FundingAccountEUR","Funding Account","FundingAccountEUR","DESTINATION","' + card_currency + '","0","' + card_currency + '","0","1","0","0.000000000","0.000000000","0.000000000","0.00","COMPLETED","N","A","FANumber_Test",""'
		bom_Expected={}

	elif type.split("_")[0] == "LOSS RECOVERY" :
		FAreport = '"'+ date + '.910","' + date + '.911",' + '"Amadeus","amamadeus#amamadeus","FRANCE","' + \
			TrnId + '","' + AdjId + '","LOSS RECOVERY","' + card_currency + '","' + str(card_amount) + '","System","Funding Account","Funding Account_fr","Virtual Card","Amadeus IT Group SA","Funding Account","FundingAccountEUR","SOURCE","' + card_currency + '","-' + str(card_amount) + '","' + card_currency + '","-' + str(card_amount) + '","1.000000000","'+nonforexfee+'","0.000000000","100000","-' + \
			str(card_amount) + '","99999","COMPLETED","N","A","FANumber_Test",""'
		bom_Expected={}

	elif type.split("_")[0] == "MANUAL DEBIT" :
		FAreport = '"'+ date + '.910","' + date + '.911",' + '"Amadeus","amamadeus#amamadeus","FRANCE","' + \
			TrnId + '","' + AdjId + '","MANUAL DEBIT","' + card_currency + '","' + str(card_amount) + '","Operator","Manual Account","Revolving_debit","Funding Account","test_manual_debit","Funding Account","test_manual_debit","SOURCE","' + card_currency + '","-' + str(card_amount) + '","' + card_currency + '","-' + str(card_amount) + '","1.000000000","'+nonforexfee+'","0.000000000","100000","-' + \
			str(card_amount) + '","9.12","COMPLETED","N","A","FANumber_Test","Revolving_Debit"'
		bom_Expected={}

	elif type.split("_")[0] == "MANUAL CREDIT" :
		FAreport = '"'+ date + '.910","' + date + '.911",' + '"Amadeus","amamadeus#amamadeus","FRANCE","' + \
			TrnId + '","' + AdjId + '","MANUAL CREDIT","' + card_currency + '","' + str(card_amount) + '","Operator","Manual Account","Revolving_Credit","Funding Account","test_manual_credit","Funding Account","test_manual_credit","DESTINATION","' + card_currency + '","' + str(card_amount) + '","' + card_currency + '","' + str(card_amount) + '","1.000000000","'+nonforexfee+'","0.000000000","100000","' + \
			str(card_amount) + '","199999","COMPLETED","N","A","FANumber_Test","Revolving_Credit"'
		bom_Expected={}

	elif type.split("_")[0] == "FA TRANSFER" :
		if type.split("_")[1] != 'EUR':
			req_currency = type.split("_")[1]
			forex_rate = 1.17
			req_amount = card_amount / forex_rate
			nonforexfee = 1.44
			forex_fee = (card_amount*3)/100
			participant_amount = card_amount - forex_fee - nonforexfee
			req_amount = card_amount / forex_rate

			FAreport = '"'+ date + '.910","' + date + '.911",' + '"Amadeus","amamadeus#amamadeus","FRANCE","' + \
				TrnId + '","' + AdjId + '","TRANSFER","' + req_currency + '","' + str(req_amount) + '","test.regression","Funding Account","FundingAccount_EUR","Funding Account","FundingAccount_' + req_currency + '","Funding Account","FundingAccount_EUR","SOURCE","' + req_currency + '","-' + str(req_amount) + '","' + card_currency + '","-'+str(participant_amount)+ '","'+str(forex_rate)+'","'+str(nonforexfee)+'","'+str(forex_fee)+'","100000","-' + \
				str(card_amount) + '","99.22","COMPLETED","Y","A","FANumber_Test",""'
			bom_Expected={}

		else:
			FAreport = '"'+ date + '.910","' + date + '.911",' + '"Amadeus","amamadeus#amamadeus","FRANCE","' + \
				TrnId + '","' + AdjId + '","TRANSFER","' + card_currency + '","' + str(card_amount) + '","test.regression","Funding Account","FundingAccount_1","Funding Account","FundingAccount_2","Funding Account","FundingAccount_1","SOURCE","' + card_currency + '","-' + str(card_amount) + '","' + card_currency + '","-' + str(card_amount) + '","1.000000000","0.000000000","0.000000000","100000","-' + \
				str(card_amount) + '","99.22","COMPLETED","N","A","FANumber_Test",""'
			bom_Expected={}


	elif type.split("_")[0] == "BANK RETURN" :
		FAreport = '"'+ date + '.910","' + date + '.911",' + '"Amadeus","amamadeus#amamadeus","FRANCE","' + \
			TrnId + '","' + AdjId + '","BANK RETURN","' + card_currency + '","' + str(card_amount) + '","test.regression","Funding Account","FundingAccount_EUR","Bank Account","Bank Account","Funding Account","FundingAccount_EUR","SOURCE","' + card_currency + '","-' + str(card_amount) + '","' + card_currency + '","-' + str(card_amount) + '","1.000000000","17.00000","0.000000000","100000","-' + \
			str(card_amount) + '","99.22","INITIALISED","N","A","FANumber_Test",""'
		bom_Expected={}

	if len(cardreport) >2:
		cardreport += "\n"

	if len(FAreport) >2:
		FAreport += "\n"
	return FAreport,cardreport,bom_Expected


# ============================================================================================
# apiso_generate_transaction: sub function method to generate apiso reports (transaction part)
# ============================================================================================
def apiso_generate_transaction(indice, type, *args):
	global part_amount_req, card_amount, bal_amount, part_amount
	VCN_LOGGER.info( "Type generate_report: " + str(type) + " " + str(indice))
	date_ref=datetime.datetime.utcnow() + datetime.timedelta(seconds=indice)
	date=str(date_ref.strftime("%Y-%m-%d %H:%M:%S"))
	date_provider=str(date_ref.strftime("%Y-%m-%d %H:00:00"))


	authreport=''
	cardreport=''
	settreport=''
	statusreport=''
	balreport=''
	output=''
	int_fee=''
	transfer_type=''

	card_amount_req = float(args[2])
	card_currency_req=args[1]
	card_amount = float(args[4])
	card_currency=args[3]
	exch_rate= card_amount_req/card_amount
	if card_currency_req != card_currency:
		forex_fee = "{0:.2f}".format(0.2 * card_amount)
		ffee_bomexp_amt = {'Amount': str(forex_fee),'Currency':card_currency}
		ffee_bomexp = {"ForexFeeAmount" : ffee_bomexp_amt}
	else:
		forex_fee = 0
		ffee_bomexp = {}
	provider_ref = args[5]
	ama_ref = args[6]

	if (indice == 0 and args[0] != ''):
		TrnId = args[0]
	else:
		TrnId='TRNID_'+date_ref.strftime("%Y%m%d%H%M%S")+'_'+ str(indice)
	if args[9]=='VI':
		vendor='V'
	else:
		vendor='M'

	if type.split("_")[0] == "CARD CREATED":
		bal_amount = card_amount
		cardreport = provider_ref + ',ACC' + provider_ref + ',' + ama_ref + ',123456,3,' + TrnId + ',' + date_provider + ',C,' + vendor + \
			',' + card_currency + ',575131232,' + "{0:.2f}".format(card_amount_req) + ',' + card_currency_req + ',' + "{0:.2f}".format(card_amount) + ',' + str(forex_fee)
		statusreport = provider_ref + ',ACC' + provider_ref + ',' + ama_ref + ',123456,USD,575131232,' + date_provider + ',A,' + "{0:.2f}".format(card_amount)\
			+ ',0,' + "{0:.2f}".format(card_amount)
		bom_Expected={ "Transactions": {
			"AmountRequested": {
				"Amount": "{0:.2f}".format(card_amount_req),
				"Currency": card_currency_req
			},
		"AmountLoaded": {
			"Amount": "{0:.2f}".format(card_amount),
			"Currency": card_currency
		},
			"Link": "VCCAPISO",
			"ExternalTransactionId": TrnId,
			"TransactionDateTime": {
				"Creation": date + '.910',
				"Processed": date_provider,
				"ReadyToReport": date
			},
			"TransactionStatus": {
				"ActionStatus": "OK",
				"Timestamp": date + '.910'
			},
			"Type": OtherTypes(type.split("_")[0])[1]
		}}
#	AUTHORISATION Partial Amount Has to be in FA Currency: EUR in this test
	elif type.split("_")[0] == "AUTHORISATION":
		if type.split("_")[1] == "OK":
			try:
				if type.split("_")[2]>0:
					part_amount_req = float(type.split("_")[2])
					part_amount = part_amount_req/exch_rate
					if card_currency_req != card_currency:
						forex_fee = "{0:.2f}".format(-0.2 * part_amount)
						ffee_bomexp_amt = {'Amount': str(forex_fee),'Currency':card_currency}
						ffee_bomexp = {"ForexFeeAmount" : ffee_bomexp_amt}
					else:
						forex_fee = 0
						ffee_bomexp = {}
					VCN_LOGGER.info( "Author Partial Amount: " + "{0:.2f}".format(part_amount_req) + " " + card_currency_req)
					authreport = provider_ref + ',ACC' + provider_ref + ',' + ama_ref + ',123456,3,' + TrnId + ',' + date_provider + ',Auth,' + vendor + \
						',00,Auth Approved,' + card_currency + ',575131232,-' + "{0:.2f}".format(part_amount_req) + ',' + card_currency_req + ',-' + "{0:.2f}".format(part_amount) + ',' + str(forex_fee) + \
						',1111,APISO TEST MERCHANT OK,Test Airline Agent,4511,FRANCE,NICE'
					statusreport = provider_ref + ',ACC' + provider_ref + ',' + ama_ref + ',123456,USD,575131232,' + date_provider + ',A,' + "{0:.2f}".format(card_amount)\
						+ ','+ "{0:.2f}".format(part_amount) +',' + "{0:.2f}".format(card_amount)
					bom_Expected={ "PaymentTransactions": {
						"AmountRequested": {
							"Amount": '-' + "{0:.2f}".format(part_amount_req),
							"Currency": card_currency_req
						},
						"ApprovalCode": "1111",
						"AuthResponseCode":"00",
						"AuthResponseMessage":'Auth Approved',
						"Merchant": {
							"Name": "APISO TEST MERCHANT OK",
							"MCC": "4511",
							"Country": "FRANCE",
							"City": "NICE"
						},
						"ExternalTransactionId": TrnId,
						"TransactionAmount": {
							"Amount": '-' + "{0:.2f}".format(part_amount),
							"Currency": card_currency
						},
						"TransactionDateTime": {
							"Creation": date,
							"Processed": date_provider,
							"ReadyToReport": date
						},
						"TransactionStatus": {
							"ActionStatus": "OK",
							"Timestamp": date
						},
						"Type": OtherTypes(type.split("_")[0])[1]
					}}
					bom_Expected['PaymentTransactions'].update(ffee_bomexp)
			except:
				authreport = provider_ref + ',ACC' + provider_ref + ',' + ama_ref + ',123456,3,' + TrnId + ',' + date_provider + ',Auth,' + vendor + \
					',00,Auth Approved,' + card_currency + ',575131232,-' + "{0:.2f}".format(card_amount_req) + ',' + card_currency_req + ',-' + "{0:.2f}".format(card_amount) + ',' + str(forex_fee) + \
					',1111,APISO TEST MERCHANT OK,Test Airline Agent,4511,FRANCE,NICE'
				statusreport = provider_ref + ',ACC' + provider_ref + ',' + ama_ref + ',123456,USD,575131232,' + date_provider + ',A,' + "{0:.2f}".format(card_amount)\
					+ ','+ "{0:.2f}".format(card_amount) +',' + "{0:.2f}".format(card_amount)
				bom_Expected={ "PaymentTransactions": {
					"AmountRequested": {
						"Amount": "-" + "{0:.2f}".format(card_amount_req),
						"Currency": card_currency_req
					},
					"ApprovalCode": "1111",
					"AuthResponseCode":"00",
					"AuthResponseMessage":"Auth Approved",
					"Merchant": {
						"Name": "APISO TEST MERCHANT OK",
						"MCC": "4511",
						"Country": "FRANCE",
						"City": "NICE"
					},
					"ExternalTransactionId": TrnId,
					"TransactionAmount": {
						"Amount": "-" + "{0:.2f}".format(card_amount),
						"Currency": card_currency
					},
					"TransactionDateTime": {
						"Creation": date,
						"Processed": date_provider,
						"ReadyToReport": date
					},
					"TransactionStatus": {
						"ActionStatus": "OK",
						"Timestamp": date
					},
					"Type": OtherTypes(type.split("_")[0])[1]
				}}
				bom_Expected['PaymentTransactions'].update(ffee_bomexp)
		elif type.split("_")[1] == "KO":
			authreport = provider_ref + ',ACC' + provider_ref + ',' + ama_ref + ',123456,3,' + TrnId + ',' + date_provider + ',Auth,' + vendor + \
				',51,Insufficient Funds,' + card_currency + ',575131232,-' + "{0:.2f}".format(card_amount_req) + ',' + card_currency_req + ',0,0' + \
				',,APISO_MERCHANT_KO,Test Airline Agent,4511,FRANCE,NICE'
			statusreport = provider_ref + ',ACC' + provider_ref + ',' + ama_ref + ',123456,USD,575131232,' + date_provider + ',A,' + "{0:.2f}".format(card_amount)\
				+ ',0,' + "{0:.2f}".format(card_amount)
			bom_Expected={ "PaymentTransactions": {
				"AmountRequested": {
					"Amount": '-' + "{0:.2f}".format(card_amount_req),
					"Currency": card_currency_req
				},
				"AuthResponseCode":"51",
				"AuthResponseMessage":"Insufficient Funds",
				"Merchant": {
					"Name": "APISO_MERCHANT_KO",
					"MCC": "4511",
					"Country": "FRANCE",
					"City": "NICE"
				},
				"ExternalTransactionId": TrnId,
				"TransactionAmount": {
					"Amount": '0.00',
					"Currency": card_currency
				},
				"TransactionDateTime": {
					"Creation": date,
					"Processed": date_provider,
					"ReadyToReport": date
				},
				"TransactionStatus": {
					"ActionStatus": "KO",
					"Timestamp": date
				},
				"Type": OtherTypes(type.split("_")[0])[1]
			}}

	if type.split("_")[0] == "AUTHORISATION RELEASE":
		if part_amount_req == '':
			part_amount_req = card_amount_req
			part_amount = card_amount
			if card_currency_req != card_currency:
				forex_fee = "{0:.2f}".format(0.2 * part_amount)
				ffee_bomexp_amt = {'Amount': str(forex_fee),'Currency':card_currency}
				ffee_bomexp = {"ForexFeeAmount" : ffee_bomexp_amt}
			else:
				forex_fee = 0
				ffee_bomexp = {}
		authreport = provider_ref + ',ACC' + provider_ref + ',' + ama_ref + ',123456,3,' + TrnId + ',' + date_provider + ',Rev,' + vendor + \
			',00,Auth Reversal,' + card_currency + ',575131232,' + "{0:.2f}".format(part_amount_req) + ',' + card_currency_req + ',' + "{0:.2f}".format(part_amount) + ',' + str(forex_fee) + \
			',1111,APISO TEST MERCHANT OK,Test Airline Agent,4511,FRANCE,NICE'
		statusreport = provider_ref + ',ACC' + provider_ref + ',' + ama_ref + ',123456,USD,575131232,' + date_provider + ',A,' + "{0:.2f}".format(card_amount)\
			+ ',0,' + "{0:.2f}".format(card_amount)
		bom_Expected={ "PaymentTransactions": {
			"AmountRequested": {
				"Amount": "{0:.2f}".format(part_amount_req),
				"Currency": card_currency_req
			},
			"ApprovalCode": "1111",
			"AuthResponseCode":"00",
			"AuthResponseMessage":"Auth Reversal",
			"Merchant": {
				"Name": "APISO TEST MERCHANT OK",
				"MCC": "4511",
				"Country": "FRANCE",
				"City": "NICE"
			},
			"ExternalTransactionId": TrnId,
			"TransactionAmount": {
				"Amount": "{0:.2f}".format(part_amount),
				"Currency": card_currency
			},
			"TransactionDateTime": {
				"Creation": date,
				"Processed": date_provider,
				"ReadyToReport": date
			},
			"TransactionStatus": {
				"ActionStatus": "OK",
				"Timestamp": date
			},
			"Type": OtherTypes(type.split("_")[0])[1]
		}}
		bom_Expected['PaymentTransactions'].update(ffee_bomexp)

	elif type.split('_')[0] == "PURCHASE":
		if bal_amount == '':
			bal_amount = card_amount
		if part_amount_req != '':
			amount_before = bal_amount
			part_amount = part_amount_req/exch_rate
			amount_after = bal_amount - part_amount
			bal_amount = amount_after
		else:
			amount_before = part_amount = bal_amount
			part_amount_req = part_amount*exch_rate
			bal_amount = amount_after = 0.00

		if card_currency_req != card_currency:
			forex_fee = "{0:.2f}".format(-0.2 * part_amount)
			ffee_bomexp_amt = {'Amount': str(forex_fee),'Currency':card_currency}
			ffee_bomexp = {"ForexFeeAmount" : ffee_bomexp_amt}
		else:
			forex_fee = 0
			ffee_bomexp = {}


		int_fee = "{0:.2f}".format(0.1 * part_amount_req)
		rev_1a = "{0:.2f}".format(0.05 * part_amount_req)

		VCN_LOGGER.info( "Settlement Partial Amount: " + "{0:.2f}".format(part_amount_req) + " " + card_currency_req)
		settreport = provider_ref + ',ACC' + provider_ref + ',' + ama_ref + ',123456,3,' + TrnId + ',' + date_provider + ',Settled,' + vendor + \
			',' + card_currency + ',575131232,-' + "{0:.2f}".format(part_amount_req) + ',' + card_currency_req + ',-' + "{0:.2f}".format(part_amount) + ',' + str(forex_fee) + \
			',-' + str(int_fee) + ',' + card_currency_req + ',' + str(rev_1a) + ',APISO TEST MERCHANT OK,Test Airline Agent,4511,FRANCE,NICE'
		statusreport = provider_ref + ',ACC' + provider_ref + ',' + ama_ref + ',123456,USD,575131232,' + date_provider + ',A,' + "{0:.2f}".format(amount_after)\
			+ ',0,' + "{0:.2f}".format(amount_after)
		bom_Expected={ "PaymentTransactions": {
			"AmountRequested": {
				"Amount": '-' + "{0:.2f}".format(part_amount_req),
				"Currency": card_currency_req
			},
			"Merchant": {
				"Name": "APISO TEST MERCHANT OK",
				"MCC": "4511",
				"Country": "FRANCE",
				"City": "NICE"
			},
			"ExternalTransactionId": TrnId,
			"TransactionAmount": {
				"Amount": '-' + "{0:.2f}".format(part_amount),
				"Currency": card_currency
			},
			"InterchangeAmount": {
				"Amount": '-' + str(int_fee),
				"Currency": card_currency_req
			},
			"TransactionDateTime": {
				"Creation": date,
				"Processed": date_provider,
				"ReadyToReport": date
			},
			"TransactionStatus": {
				"ActionStatus": "OK",
				"Timestamp": date
			},
			"Type": OtherTypes(type.split("_")[0])[1]
		}}
		bom_Expected['PaymentTransactions'].update(ffee_bomexp)

	if type.split("_")[0] == "MERCHANT REFUND":
		if bal_amount == '':
			bal_amount = float('0.00')
		try:
			if type.split("_")[1]>0:
				part_amount_req = float(type.split("_")[1])
				part_amount = part_amount_req/exch_rate
				amount_before = bal_amount
				amount_after = bal_amount + part_amount
				bal_amount = amount_after
		except:
			if part_amount != '':
				part_amount_req = part_amount*exch_rate
				amount_before = bal_amount
				amount_after = bal_amount + part_amount
				bal_amount = amount_after
			else:
				amount_before = bal_amount
				part_amount = card_amount
				part_amount_req = part_amount*exch_rate
				bal_amount = amount_after = part_amount + bal_amount

		if card_currency_req != card_currency:
			forex_fee = "{0:.2f}".format(0.2 * part_amount)
			ffee_bomexp_amt = {'Amount': str(forex_fee),'Currency':card_currency}
			ffee_bomexp = {"ForexFeeAmount" : ffee_bomexp_amt}
		else:
			forex_fee = 0
			ffee_bomexp = {}

		int_fee = "{0:.2f}".format(0.1 * part_amount_req)
		rev_1a = "{0:.2f}".format(0.05 * part_amount_req)

		VCN_LOGGER.info( "Refund Amount Amount: " + "{0:.2f}".format(part_amount) + " " + card_currency)
		settreport = provider_ref + ',ACC' + provider_ref + ',' + ama_ref + ',123456,3,' + TrnId + ',' + date_provider + ',Refund,' + vendor + \
			',' + card_currency + ',575131232,' + "{0:.2f}".format(part_amount_req) + ',' + card_currency_req + ',' + "{0:.2f}".format(part_amount) + ',' + str(forex_fee) + \
			',' + str(int_fee) + ',' + card_currency_req + ',' + str(rev_1a)+ ',APISO TEST MERCHANT OK,Test Airline Agent,4511,FRANCE,NICE'
		statusreport = provider_ref + ',ACC' + provider_ref + ',' + ama_ref + ',123456,USD,575131232,' + date_provider + ',A,' + "{0:.2f}".format(amount_after)\
			+ ',0,' + "{0:.2f}".format(amount_after)
		bom_Expected={ "PaymentTransactions": {
			"AmountRequested": {
				"Amount": "{0:.2f}".format(part_amount_req),
				"Currency": card_currency_req
			},
			"Merchant": {
				"Name": "APISO TEST MERCHANT OK",
				"MCC": "4511",
				"Country": "FRANCE",
				"City": "NICE"
			},
			"ExternalTransactionId": TrnId,
			"TransactionAmount": {
				"Amount": "{0:.2f}".format(part_amount),
				"Currency": card_currency
			},
			"InterchangeAmount": {
				"Amount": str(int_fee),
				"Currency": card_currency_req
			},
			"TransactionDateTime": {
				"Creation": date,
				"Processed": date_provider,
				"ReadyToReport": date
			},
			"TransactionStatus": {
				"ActionStatus": "OK",
				"Timestamp": date
			},
			"Type": OtherTypes(type.split("_")[0])[1]
		}}
		bom_Expected['PaymentTransactions'].update(ffee_bomexp)

	# Partial Amounts for DELETE / TRANSFER have to be in EUR
	elif type.split("_")[0] == "CARD DELETED":
		if bal_amount == '':
			bal_amount = card_amount
		try:
			if type.split("_")[1]>0:
				part_amount_req = float(type.split("_")[1])
				part_amount = part_amount_req/exch_rate
				amount_before = bal_amount
				amount_after = bal_amount - delete_amount
				bal_amount = amount_after
		except:
			amount_before = part_amount = bal_amount
			amount_after = bal_amount - part_amount
			bal_amount = amount_after
			part_amount_req = part_amount

		if card_currency_req != card_currency:
			forex_fee = "{0:.2f}".format(-0.2 * part_amount)
		else:
			forex_fee = 0

		cardreport = provider_ref + ',ACC' + provider_ref + ',' + ama_ref + ',123456,3,' + TrnId + ',' + date_provider + ',F,' + vendor + \
			',' + card_currency + ',575131232,-' + "{0:.2f}".format(part_amount_req) + ',' + card_currency_req + ',-' + "{0:.2f}".format(part_amount) + ',' + str(forex_fee)
		statusreport = provider_ref + ',ACC' + provider_ref + ',' + ama_ref + ',123456,USD,575131232,' + date_provider + ',B,' + str(amount_after) +\
			',0,' + str(amount_after)
		bom_Expected={ "Transactions": {
			"AmountLoaded": {
				"Amount": "{0:.2f}".format(part_amount),
				"Currency": card_currency
			},
			"AmountRequested": {
				"Amount": '-' + "{0:.2f}".format(part_amount_req),
				"Currency": card_currency_req
			},
			"ExternalTransactionId": TrnId,
			"Source": "IMPORT",
			"TransactionDateTime": {
				"Creation": date + '.900',
				"Processed": date_provider,
				"ReadyToReport": date
			},
			"TransactionStatus": {
				"ActionStatus": "OK",
				"Timestamp": date + '.900'
			},
			"Type": OtherTypes(type.split("_")[0])[1]
		}}
	#STATUS Has to come with the expected STATUS in 1st position and optional Partial Amount in 2nd position in the Requested Currency
	elif type.split("_")[0] == "STATUS":
		try:
			if type.split("_")[2]>0:
				part_amount_req = float(type.split("_")[2])
				part_amount = part_amount_req/exch_rate
				if card_currency_req != card_currency:
					forex_fee = "{0:.2f}".format(-0.2 * part_amount)
				else:
					forex_fee = 0
				VCN_LOGGER.info( "Status Partial Amount: " + "{0:.2f}".format(part_amount_req) + " " + card_currency_req)
				statusreport = provider_ref + ',ACC' + provider_ref + ',' + ama_ref + ',123456,USD,575131232,' + date_provider + ','+ type.split("_")[1] +',' + "{0:.2f}".format(part_amount)\
					+ ',0,' + "{0:.2f}".format(part_amount)
				bom_Expected=''
		except:
			statusreport = provider_ref + ',ACC' + provider_ref + ',' + ama_ref + ',123456,USD,575131232,' + date_provider + ','+type.split("_")[1]+',' + "{0:.2f}".format(card_amount)\
				+ ',0,' + "{0:.2f}".format(card_amount)
			bom_Expected=''

	elif type.split("_")[0] == "BANK TRANSFER" :
		try:
			if float(type.split("_")[1])<0:
				bank_amount_req = float(type.split("_")[1])
				bank_amount = bank_amount_req/exch_rate
				if card_currency_req != card_currency:
					forex_fee = "{0:.2f}".format(-0.2 * bank_amount)
				else:
					forex_fee = 0
				VCN_LOGGER.info( "Bank Return Amount: " + "{0:.2f}".format(bank_amount_req) + " " + card_currency_req)
				cardreport = '123456,' + TrnId + ',' + date_provider + ',3,575131232,Unload,' + "{0:.2f}".format(bank_amount_req) + ',' + card_currency_req + ',' +\
					"{0:.2f}".format(bank_amount) + ',' + card_currency + ',' + str(exch_rate) + ',' + str(forex_fee) + ',' + card_currency
				bom_Expected={}
			else:
				bank_amount_req = float(type.split("_")[1])
				bank_amount = bank_amount_req/exch_rate
				if card_currency_req != card_currency:
					forex_fee = "{0:.2f}".format(-0.2 * bank_amount)
				else:
					forex_fee = 0
				VCN_LOGGER.info( "Bank Deposit Amount: " + "{0:.2f}".format(bank_amount_req) + " " + card_currency_req)
				cardreport = '123456,' + TrnId + ',' + date_provider + ',3,575131232,Load,' + "{0:.2f}".format(bank_amount_req) + ',' + card_currency_req + ',' +\
					"{0:.2f}".format(bank_amount) + ',' + card_currency + ',' + str(exch_rate) + ',' + str(forex_fee) + ',' + card_currency
				bom_Expected={}
		except:
			bank_amount_req = float(-1000)
			bank_amount = bank_amount_req/exch_rate
			if card_currency_req != card_currency:
				forex_fee = "{0:.2f}".format(-0.2 * bank_amount)
			else:
				forex_fee = 0
			VCN_LOGGER.info( "Bank Return Amount: " + "{0:.2f}".format(bank_amount_req) + " " + card_currency_req)
			cardreport = '123456,' + TrnId + ',' + date_provider + ',3,575131232,Unload,' + "{0:.2f}".format(bank_amount_req) + ',' + card_currency_req + ',' +\
				"{0:.2f}".format(bank_amount) + ',' + card_currency + ',' + str(exch_rate) + ',' + str(forex_fee) + ',' + card_currency
			bom_Expected={}

	elif type.split("_")[0] == "TRANSFER":
		if len(type.split("_"))>1:
			if bal_amount == '':
				bal_amount = card_amount
			transfer_amount_req = float(type.split("_")[1])
			if transfer_amount_req<0:
				transfer_type='D'
			else:
				transfer_type='C'
			transfer_amount = transfer_amount_req/exch_rate
			if card_currency_req != card_currency:
				forex_fee = "{0:.2f}".format(-0.2 * transfer_amount)
			else:
				forex_fee = 0
			VCN_LOGGER.info( 'transfer_type: ' + transfer_type + ' transfer_amount:' + "{0:.2f}".format(transfer_amount_req) + ' ' + card_currency_req)
			bal_amount = bal_amount + transfer_amount
		else:
			transfer_amount_req = card_amount_req
			transfer_amount = card_amount
			transfer_type='F'
			bal_amount = 0
			VCN_LOGGER.info( 'transfer_type: ' + transfer_type + ' transfer_amount:' + "{0:.2f}".format(transfer_amount_req) + ' ' + card_currency_req)
		cardreport = provider_ref + ',ACC' + provider_ref + ',' + ama_ref + ',123456,3,' + TrnId + ',' + date_provider + ','+ transfer_type +',' + vendor + \
			',' + card_currency + ',575131232,' + "{0:.2f}".format(transfer_amount_req) + ',' + card_currency_req + ',' + "{0:.2f}".format(transfer_amount) + ',' + str(forex_fee)
		statusreport = provider_ref + ',ACC' + provider_ref + ',' + ama_ref + ',123456,USD,575131232,' + date_provider + ',A,' + "{0:.2f}".format(bal_amount)\
			+ ',0,' + "{0:.2f}".format(bal_amount)
		bom_Expected={ "Transactions": {
			"AmountRequested": {
				"Amount": "{0:.2f}".format(transfer_amount_req),
				"Currency": card_currency_req
			},
		"AmountLoaded": {
			"Amount": "{0:.2f}".format(transfer_amount),
			"Currency": card_currency
		},
			"Link": "VCCAPISO",
			"ExternalTransactionId": TrnId,
			"TransactionDateTime": {
				"Creation": date + '.910',
				"Processed": date_provider,
				"ReadyToReport": date
			},
			"TransactionStatus": {
				"ActionStatus": "OK",
				"Timestamp": date + '.910'
			},
			"Type": OtherTypes(type.split("_")[0])[1]
		}}

	if len(cardreport) >2:
		cardreport += "\n"
	if len(settreport) >2:
		settreport += "\n"
	if len(authreport) >2:
		authreport += "\n"
	if args[10] != '1':
		statusreport = ''
	if len(statusreport) >2:
		statusreport += "\n"


	return cardreport,authreport,settreport,statusreport,bom_Expected


# ============================================================================
# getRandomAlphanumeric: generate random value (Alpha)
# ============================================================================

def getRandomAlphanumeric(size):
	return ''.join(choice(string.ascii_uppercase + string.digits) for _ in range(size))


# ============================================================================
# OtherTypes: check type by matrix method
# ============================================================================

def OtherTypes(type):
	matrix={'Transactions': {'CREATION': 'CARD CREATED','CANCELLATION': 'CARD DELETED','UPDATE_FREEZE': 'FREEZE','UPDATE_THAW': 'THAW','UPDATE_FUNDS': 'TRANSFER'},'PaymentTransactions': {'REVERSAL': 'AUTHORISATION RELEASE','SETTLEMENT': 'PURCHASE','REFUND': 'MERCHANT REFUND','AUTHORISATION': 'AUTHORISATION'},'USB_PaymentTransactions': {'SETTLEMENT': 'P','REFUND': 'C'}}
	try:
		for i in matrix:
			for k, v in matrix[i].items():
				if v == type:
					return [i,k]
				if k == type:
					return [i,v]
	except:
		Match=False
		print("Unexpected error:", sys.exc_info()[0])



def Store_Import_File(file_name,file_content,extension):
		file_name = file_name +'_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + '_QA.'+ extension
		file_path = Report_storage_dir / file_name
		print('curdir',file_path)
		try:
			with open(file_path, 'w') as file:
				file.write(file_content)
				return file_name
		except Exception as e:
			print("Unable to create bin file {}".format(e))

def Clean_import_file_dir():
	for file in os.listdir(Report_storage_dir):
		print(f"Clean file {file}")
		os.remove(os.path.join(Report_storage_dir, file))

def generate_import_file(provider, transaction_list, card_information):

	if provider.lower() == "ixaris":

		bom_expected = {
			"Provider": "IXARIS"
			}
		funding_account_report = '"startDate","transactionDate","community","client","country","transactionID","adjustmentID","transactionType","transactionCurrency","transactionAmount","transactionAuthor","sourceType","sourceDetails","destinationType","destinationDetails","participantType","participantDetails","participantSink","originalCurrency","originalAmount","participantCurrency","participantAmount","exchangeRate","nonForexFee","forexFee","balanceBefore","balanceAdjustment","balanceAfter","status","forexFlag","direction","externalRef","transactionInfo"' + '\n'
		card_activity_report = '"startDate","transactionDate","community","client","transactionID","adjustmentID","transactionType","transactionCurrency","transactionAmount","sourceType","sourceDetails","destinationType","destinationDetails","participantType","participantDetails","participantSink","originalCurrency","originalAmount","participantCurrency","participantAmount","exchangeRate","nonForexFee","forexFee","balanceBefore","balanceAdjustment","balanceAfter","status","forexFlag","direction","merchantName","merchantCountry","merchantCategoryCode","acquirerReferenceNumber","authCode","providerDate","externalRef","externalID","cardNum","cardScheme","cardFactoryName","customField1","customField2","customField3","customField4","customField5","transactionInfo","interchangeAmount","interchangeCurrency"'+ '\n'

		fa_report,card_report,bom = generate_report(transaction_list,card_information)
		funding_account_report += fa_report
		card_activity_report += card_report
		bom_expected.update(bom)

		funding_account_report= Store_Import_File('Funding_Account_Activity_ixaris',funding_account_report,'csv')
		card_activity_report = Store_Import_File('Card_Activity_ixaris',card_activity_report,'csv')

		output=(funding_account_report,card_activity_report,bom_expected)
		return	tuple(output)

	elif provider.lower() == "usbank":

		bom_expected = {
			"Provider": "USBANK"
			}
		card_activity_report = 'Posted Txn Date/Timestamp","Transaction Date/Timestamp","Transaction ID","Travel Agency Name ","Travel Agency Country","Card ID","Card Number ","Agency Identifier","Transaction Type ","Type Description ","Funding Account Ref/ID","Requested Transaction Amount","Requested Transaction Currency ","Transaction Amount","Transaction Currency","Merchant Name","Merchant Country","Merchant MCC","Interchange Currency","Interchange Amount","Transaction Status","Authorisation Approval Code","User Defined 1","User Defined 2","User Defined 3","User Defined 4","User Defined 5","User Defined 6","User Defined 7","User Defined 8","User Defined 9","User Defined 10","User Defined 11","User Defined 12","User Defined 13","User Defined 14","User Defined 15'+ '\n'
		card_report,bom = generate_report(transaction_list,card_information)

		card_activity_report+=card_report
		bom_expected.update(bom)

		card_activity_report = Store_Import_File('Card_Activity_usbank',card_activity_report,'csv')
		output=(card_activity_report,bom_expected)

		return	tuple(output)

	elif provider.lower() == "citibank":

		bom_expected = {
			"Provider": "CITIBANK"
			}
		card_activity_report,bom = generate_report(transaction_list,card_information,prov='citibank')
		bom_expected.update(bom)

		card_activity_report = Store_Import_File('Card_Activity_citibank',card_activity_report,'xml')
		output=(card_activity_report,bom_expected)

		return	tuple(output)
	else:
		return None


if __name__ == "__main__":

	card=('0RABAc4dn_b34x6ncdRWbniIN', 'EUR', '1.00', 'EUR', '1.00', '0RAArEjtTbX57KYibgAPhHu_9', '22224WAF', '522093', '9372', 'CA', '1', '', '', '', '', '','')
	list_1 = ['CARD CREATED','CARD DELETED','TRANSFER_-2']
	Ixaris_report =  generate_import_file('IXARIS',list_1,card)

#  card=('0RABAc4dn_b34x6ncdRWbniIN', 'EUR', '1.00', 'EUR', '1.00', '0RAArEjtTbX57KYibgAPhHu_9', '22224WAF', '522093', '9372', 'CA', '1', '', '', '', '', '','')
# 	# print(Ixaris_report[0],Ixaris_report[1],Ixaris_report[2])


	# card = ('','USD','10.00','USD','10.00','','','9999992222221111','','','','','','','','')
	# list_1 = ["CITI_C","CITI_C"]
	# CA_citibank_report=  generate_import_file('CITIBANK',list_1,card)



# 	# print(CA_citibank_report[0],CA_citibank_report[1])

