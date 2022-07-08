snapshot_template_path = "Resources/Components/Models/snapshot_template.json"

snapshot_fields = ["Timestamp", "LinkCode", "TransactionType", "TransactionAuthor", "SourceType", "SourceName", "DestinationType", "DestinationName", "ForexFlag", "CurrencyConversionRate", 
"ExternalID", "AdjustmentID", "AccountReference", "OriginalAmount", "OriginalCurrency", "Amount", "Currency", "AccountTransactionAmount", "AccountCurrency", "BalanceBeforeAmount", "BalanceBeforeCurrency", "BalanceAfterAmount", 
"BalanceAfterCurrency", "BalanceAdjustmentAmount", "BalanceAdjustmentCurrency", "ForexFeeAmount", "ForexFeeCurrency", "LinkResponse", "Status", "ExternalCardReference"]   

snapshot_sort = {"fieldId":"Timestamp", "order":"ascending"}

startFrom_dict = {"time":"now", "roundTo":"d"}    
spanTo_dict = {"time":"now"} 

snapshot_filters_dict1 = { "fieldId":"Type","operator":"in", "args":["Payment/B2BWallet/VirtualCard"] }   
snapshot_filters_dict2 = {"fieldId":"ExternalID", "operator":"in"}    

 