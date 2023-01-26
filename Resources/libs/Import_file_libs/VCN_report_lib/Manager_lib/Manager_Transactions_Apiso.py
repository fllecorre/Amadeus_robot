from VCN_report_lib.Manager_lib.Manager import Manager
from VCN_report_lib.Transaction_lib import Transaction_Apiso

class ManagerTransactionsApiso(Manager):
    def expected_trans(self, itype, iinfo, iindice):
        if   itype == "CARD CREATED" :
            return #Transaction_Apiso.TransactionApisoCREATED(itype, iinfo, iindice)
        elif itype == "CARD DELETED" :
            return #Transaction_Apiso.TransactionApisoDELETED(itype, iinfo, iindice)
    
    def generate(self, list_trans, iinfo):
        adict = {
            "part_amount_req":0,
            "card_amount":0,
            "bal_amount":0,
            "part_amount":0
        }

        l_authreport = ''
        l_cardreport = ''
        l_settreport = ''
        l_statusreport = ''
        l_bom_expected = {"PaymentTransactions":[],"Transactions":[]}
        
        for trans in list_trans:
            report1, report2, report3, report4, report5, adict = trans.generate_report(adict)

            l_cardreport = self.add_report(report1, l_cardreport)
            l_authreport = self.add_report(report2, l_authreport)
            l_settreport = self.add_report(report3, l_settreport)
            if report4:
                l_statusreport = report4

            for tr in report5:
                l_bom_expected[tr].append(report5[tr])
                tr_index = l_bom_expected[tr].index(report5[tr])
                if (tr == "Transactions") and ("CREATION" in tr) and (iinfo[10] != ''):
                    l_bom_expected[tr][tr_index].update({"AdditionalInfo": {"Item":[]}})
                    for i in range(10,14):
                        if iinfo[i] != '':
                            l_bom_expected[tr][tr_index]["AdditionalInfo"]["Item"].append({"ShortName": iinfo[i].split("-")[0].strip(),"Type": "CardInfo","Value": iinfo[i].split("-")[1].strip()})

        output = [l_bom_expected]
        output = self.update_output(l_statusreport, output)
        output = self.update_output(l_settreport, output)
        output = self.update_output(l_authreport, output)
        output = self.update_output(l_cardreport, output)

        return tuple(output)

    def update_output(self, l_report, output) :
        if l_report != '' :
            output.insert(0,str(l_report))
        return output

    def add_report(self, out_report, l_report) :
        if out_report:
            l_report += out_report
        return l_report
