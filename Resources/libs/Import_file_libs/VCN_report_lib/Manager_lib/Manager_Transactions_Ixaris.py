from VCN_report_lib.Manager_lib.Manager import Manager
from VCN_report_lib.Transaction_lib import Transaction_Ixaris

class ManagerTransactionsIxaris(Manager):
    def expected_trans(self, itype, iinfo, iindice):
        if   itype == "CARD CREATED" :
            return #Transaction_Ixaris.TransactionIxarisCREATED(itype, iinfo, iindice)
        elif itype == "CARD DELETED" :
            return #Transaction_Ixaris.TransactionIxarisDELETED(itype, iinfo, iindice)
    
    def generate(self, list_trans, iinfo):
        adict = {
            "part_amount_req":0,
            "card_amount":0,
            "bal_amount":0,
            "part_amount":0
        }

        l_FAreport = ''
        l_cardreport = ''
        l_bom_expected = {"PaymentTransactions":[],"Transactions":[]}
        
        for trans in list_trans:
            report1, report2, report3, adict = trans.generate_report(adict)
            l_FAreport += report1
            l_cardreport += report2
            for tr in report3:
                l_bom_expected[tr].append(report3[tr])
                tr_index = l_bom_expected[tr].index(report3[tr])
                if (tr == "Transactions") and (iinfo[11] != ''):
                    l_bom_expected[tr][tr_index].update({"AdditionalInfo": {"Item":[]}})
                    for i in range(11,15):
                        if iinfo[i] != '':
                            l_bom_expected[tr][tr_index]["AdditionalInfo"]["Item"].append({"ShortName": iinfo[i].split(":")[0].strip(),"Type": "CardInfo","Value": iinfo[i].split(":")[1].strip()})
        if l_FAreport == "" :
            l_FAreport = "\n"
        if l_cardreport == "" :
            l_cardreport = "\n"
        f = open("Report/Ixaris/Report_Expected_Ixaris.csv", "w")
        f.write("1:"+ l_FAreport+"2:"+l_cardreport)
        f.close()
        return str(l_FAreport),str(l_cardreport),l_bom_expected