import sys
from VCN_report_lib import utils
from VCN_report_lib.Manager_lib.Manager_Transactions_Ixaris import ManagerTransactionsIxaris
from VCN_report_lib.Manager_lib.Manager_Transactions_Apiso import ManagerTransactionsApiso
from VCN_report_lib.Manager_lib.Manager_Transactions_Usbank import ManagerTransactionsUsbank
from VCN_report_lib.Manager_lib.Manager_Transactions_Citibank import ManagerTransactionsCitibank


class VirtualCard :

    def __init__(self, iprovider):
        self.index = 0
        self._provider = iprovider
        self._list_transaction = []
        if self._provider == "ixaris" :
            self._manager = ManagerTransactionsIxaris()
        elif self._provider == "apiso" :
            self._manager = ManagerTransactionsApiso()
        elif self._provider == "usbank" :
            self._manager = ManagerTransactionsUsbank()
        elif self._provider == "citibank" :
            self._manager = ManagerTransactionsCitibank()
        else :
            raise utils.VirtualException()
            
    def __str__(self):
        result  = "VirtualCard: \n"
        result += "   Provider: " + self._provider + "\n"
        result += "   Info: " + str(self._info) + "\n"
        result += "   Transaction : ["
        for trans in self._list_transaction :
            result += str(trans)+", "
        result = result[:-2]+"]"
        return result
    #-------------------------getter-------------------------#
    def get_provider(self):        
        return self._provider 
    def get_info(self):        
        return self._info
    def get_transaction(self):
        return self._list_transaction
    #-------------------------other-------------------------#        
    def add_transaction(self, itype, iinfo) :
        self._list_transaction.append(self._manager.expected_trans(itype, iinfo, self.index))
        self.index += 1

    def add_list_transaction(self, ilist_type, iinfo) :
        for type in ilist_type :
            self._list_transaction.append(self._manager.expected_trans(type, iinfo, self.index))
            self.index += 1

    def generate_transactions_report(self) :
        return self._manager.generate(self._list_transaction)