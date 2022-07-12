### PATHS ###
snapshot_template_path = "Resources/Components/XPP_data/snapshot_template.json"
configuration_template_path = "Resources/Components/XPP_data/configuration_template.json"

### FIELDS ###
snapshot_fields = ["Timestamp", "LinkCode", "TransactionType", "TransactionAuthor", "SourceType", "SourceName", "DestinationType", "DestinationName", "ForexFlag", "CurrencyConversionRate", 
"ExternalID", "AdjustmentID", "AccountReference", "OriginalAmount", "OriginalCurrency", "Amount", "Currency", "AccountTransactionAmount", "AccountCurrency", "BalanceBeforeAmount", "BalanceBeforeCurrency", "BalanceAfterAmount", 
"BalanceAfterCurrency", "BalanceAdjustmentAmount", "BalanceAdjustmentCurrency", "ForexFeeAmount", "ForexFeeCurrency", "LinkResponse", "Status", "ExternalCardReference"]   

### SORTING ###
snapshot_sort = {"fieldId":"Timestamp", "order":"ascending"}

### TIME RANGE ###
startFrom_dict = {"time":"now", "roundTo":"d"}    
spanTo_dict = {"time":"now"} 

### FILTERS ###
snapshot_filters_dict1 = { "fieldId":"Type","operator":"in", "args":["Payment/B2BWallet/VirtualCard"] }   
snapshot_filters_dict2 = {"fieldId":"ExternalID", "operator":"in"}   

### DELIVERY OPTIONS ###
configuration_delivery = {"format":"CSV", "channel":"Download", "fileName":"PHASE.TestQAReport.yyyy-mm-dd-01.extension"} 

### API SETTINGS ###
baseURL = "https://paypages.dev.payment.amadeus.com:443" 
SAP = "1ASIUAPSGUI"
query_parameters = "?merchant=APS_OFF_NCE1A095X"

