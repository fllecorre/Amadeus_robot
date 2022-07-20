### PATHS ###
snapshot_template_path = "Resources/Components/XPP_data/snapshot_template.json"
configuration_template_path = "Resources/Components/XPP_data/configuration_template.json"

### FIELDS ###
snapshot_fields = ["Timestamp", "VCNID", "ExternalCardReference", "LinkCode", "TransactionType", "Amount", "Currency", "Status"]   

### SORTING ###
snapshot_sort = {"fieldId":"Timestamp", "order":"ascending"}

### TIME RANGE ###
startFrom_dict = {"time":"now", "roundTo":"d"}    
spanTo_dict = {"time":"now"} 

### FILTERS ###
snapshot_filters_dict1 = { "fieldId":"Type","operator":"in", "args":["Payment/B2BWallet/VirtualCard"] }   
snapshot_filters_dict2 = {"fieldId":"ExternalID", "operator":"in"}   

### DELIVERY OPTIONS ###
configuration_delivery = {"format":"CSV", "channel":"Download", "fileName":"PHASE.TestQAReport.yyyy-mm-dd-01.csv"} 

### API SETTINGS ###
baseURL = "https://paypages.dev.payment.amadeus.com:443" 
SAP = "1ASIUAPSGUI"
query_parameters = "?merchant=APS_OFF_NCE1A095X"

### TRANSACTION DATA ###
transaction_list = ["CARD CREATED", "AUTHORISATION_OK", "PURCHASE", "CARD DELETED"]




