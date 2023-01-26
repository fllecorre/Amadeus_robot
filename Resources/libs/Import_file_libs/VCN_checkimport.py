"""
 CHECK BOM after a merge of transaction contents from IMPORT files sent by provider
"""


import json
import sys
import re
import logging
import copy

VCN_LOGGER = logging.getLogger(__name__)


def VerifyCardBom(bom,bom_Expected):
    """ VerifyCardBom: main function to check BOM content after an integration/merge of transactions request included in import file - IXARIS provider
        Mapping BOM vs import file: http://rndwww.nce.amadeus.net/wiki/wikidoc/index.php/VCN_Card_Activity_(IXARIS) """
    VCN_LOGGER.info('Received BOM')
    VCN_LOGGER.info(bom)
    VCN_LOGGER.info('Expected BOM')
    VCN_LOGGER.info(bom_Expected)
    bom=bom.replace('\{','{').replace('\}','}').replace('\%','%')
    bom_dict = json.loads(bom)
    Match = True

    for k in bom_Expected:
        VCN_LOGGER.info(k)
        #Validate amounts in the expected response if they are present
        if k in ['AvailableBalance','TotalRequestedAmount','TotalLoadedAmount']:
            if k in bom_dict:
                if bom_dict[k]["Amount"] != bom_Expected[k]["Amount"]:
                    VCN_LOGGER.info(k + "/Amount incorrect, Expected: " + bom_Expected[k]["Amount"] + ", Received: " + bom_dict[k]["Amount"])
                    Match = False
                if bom_dict[k]["Currency"] != bom_Expected[k]["Currency"]:
                    VCN_LOGGER.info(k + "/Currency incorrect, Expected: " + bom_Expected[k]["Currency"] + ", Received: " + bom_dict[k]["Currency"])
                    Match = False
            else:
                VCN_LOGGER.info(k + " not present in BOM")
                Match = False

        if k == "TransactionIndex":
            if "AdditionalInfo" in bom_Expected["TransactionIndex"]:
                if bom_dict["TransactionIndex"]["AdditionalInfo"] != bom_Expected["TransactionIndex"]["AdditionalInfo"]:
                    VCN_LOGGER.info("TransactionIndex AdditionalInfo incorrect, Expected: " + bom_Expected["TransactionIndex"]["AdditionalInfo"] + ", Received: " + bom_dict["TransactionIndex"]["AdditionalInfo"])
                    Match = False
            if "Current" in bom_Expected["TransactionIndex"]:
                if bom_dict["TransactionIndex"]["Current"] != bom_Expected["TransactionIndex"]["Current"]:
                    VCN_LOGGER.info("TransactionIndex Current incorrect, Expected: " + bom_Expected["TransactionIndex"]["Current"] + ", Received: " + bom_dict["TransactionIndex"]["Current"])
                    Match = False

        if k == "StaticCardInformation":
            for l in bom_Expected["StaticCardInformation"]:
                if l in bom_dict["StaticCardInformation"]:
                    if bom_Expected["StaticCardInformation"][l] != bom_dict["StaticCardInformation"][l]:
                        if l != "PAN":
                            VCN_LOGGER.info("StaticCardInformation/" + l + " incorrect, Expected: " + bom_Expected["StaticCardInformation"][l] + ", Received: " + bom_dict["StaticCardInformation"][l])
                            Match = False
                        else:
                            if bom_Expected["StaticCardInformation"][l][:6] != bom_dict["StaticCardInformation"][l][:6]:
                                VCN_LOGGER.info("StaticCardInformation/" + l + " incorrect, Expected: " + bom_Expected["StaticCardInformation"][l] + ", Received: " + bom_dict["StaticCardInformation"][l])
                                Match = False
                else:
                    VCN_LOGGER.info("StaticCardInformation/" + l + " not present in BOM")
                    Match = False

        if k in ['ExternalID','PRI','CardStatus']:
            if k in bom_dict:
                if bom_dict[k] != bom_Expected[k]:
                    VCN_LOGGER.info(k + " incorrect, Expected: " + bom_Expected[k] + ", Received: " + bom_dict[k])
                    Match = False
            else:
                VCN_LOGGER.info(k + " not present in BOM")
                Match = False

        if k in ['Transactions','PaymentTransactions']:
          if bom_Expected[k]:
            for tr_exp in bom_Expected[k]:
                check_type = 0
                check_tr = 0
                i = bom_Expected[k].index(tr_exp)

                for tr in bom_dict[k]:
                    if tr["Type"] == tr_exp["Type"]:
                        check_type += 1
                        if "ExternalTransactionId" in tr:
                            VCN_LOGGER.info("3")
                            if tr["ExternalTransactionId"] == tr_exp["ExternalTransactionId"]:
                                check_tr += 1
                                j = bom_dict[k].index(tr)
                                if VerifyTrBom(bom_dict[k][j],bom_Expected[k][i]) == False:
                                    Match = False
                        else:
                            if not tr["Type"] == "CREATION":
                                VCN_LOGGER.info("Transaction Type " + tr["Type"] + "is present in BOM without any TrnID")
                                Match = False
                            if tr["Type"] == "CREATION" and bom_dict['Provider']=='USBANK':
                                check_tr += 1
                                j = bom_dict[k].index(tr)
                                if VerifyTrBom(bom_dict[k][j],bom_Expected[k][i]) == False:
                                    Match = False
            if check_tr < 1:
                VCN_LOGGER.info("Transaction Type " + tr_exp["Type"] + ":" + tr_exp["ExternalTransactionId"] + " is not present in BOM")
                Match = False
                if check_type > check_tr:
                    VCN_LOGGER.info("Transaction Type " + tr_exp["Type"] + " is present in BOM with an unknown Trnid")
                    Match = False
            elif check_tr > 1:
                VCN_LOGGER.info("Transaction Type " + tr_exp["Type"] + ":" + tr_exp["ExternalTransactionId"] + " is present times " + str(check_tr) + " in BOM")
                Match = False
                if check_type > check_tr:
                    VCN_LOGGER.info("Transaction Type " + tr_exp["Type"] + " is present in BOM with an unknown Trnid")
                    Match = False

    VCN_LOGGER.info(Match)

    if Match is True:
        return 0
    else:
        return 1



def VerifyTrBom(bom_dict,bom_Expected):
    """ VerifyTrBom: sub function to check BOM content after an integration/merge of transactions request only included in import file - IXARIS provider """
    MatchTr = True
    #Retrieve
    try:
        for k in bom_Expected:
            #Compare Dates
            VCN_LOGGER.info(k)

            # Compare other Ids that should be present
            if k in ['ExternalTransactionId','ApprovalCode','CardFactory']:
                if k in bom_dict:
                    if bom_dict[k] != bom_Expected[k]:
                        VCN_LOGGER.info("3")
                        VCN_LOGGER.info(k + " incorrect, Expected: " + bom_Expected[k] + ", Received: " + bom_dict[k])
                        MatchTr = False
                else:
                    VCN_LOGGER.info("!! Missing Element !! : " + k + " is not present in BOM")
                    MatchTr = False

            if k == "AdditionalInfo":
                if k in bom_dict:
                    for addinfo_exp in bom_Expected["AdditionalInfo"]["Item"]:
                        check_add = False
                        for addinfo in bom_dict["AdditionalInfo"]["Item"]:
                            if addinfo["ShortName"] == addinfo_exp["ShortName"]:
                                check_add = True
                                if addinfo["Value"] != addinfo_exp["Value"]:
                                    VCN_LOGGER.info("Value incorrect for Additional Info"+ addinfo_exp["ShortName"] + ", Expected: " + addinfo_exp["Value"] + ", Received: " + addinfo["Value"])
                                    MatchTr = False
                        if check_add is False:
                            VCN_LOGGER.info("Not present as Additional Info:" + addinfo_exp["ShortName"])
                            MatchTr = False
                else:
                    VCN_LOGGER.info("Not present in the BOM: " + k)
                    MatchTr = False

            if k in ["TransactionDateTime", "Merchant","TransactionStatus", "AmountRequested", "BalanceAfter", "BalanceBefore", "ForexFeeAmount", "TransactionAmount"]:
                if k in bom_dict:
                    for k_item in bom_Expected[k]:
                        if k_item in bom_dict[k]:
                            if bom_dict[k][k_item][:10]!=bom_Expected[k][k_item][:10]:
                                VCN_LOGGER.info(k + " " + k_item + " incorrect, Expected: " + bom_Expected[k][k_item] + ", Received: " + bom_dict[k][k_item])
                                MatchTr = False
                        else:
                            VCN_LOGGER.info("!! Missing Element !! : " + k + "/" + k_item + " is not present in BOM")
                            MatchTr = False
                else:
                    VCN_LOGGER.info("!! Missing Element !! : " + k + " is not present in BOM")
                    MatchTr = False


    except:
        VCN_LOGGER.info("Unexpected error:", sys.exc_info()[0])
        MatchTr = False

    return MatchTr


