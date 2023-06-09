"""
Test suite data
"""
from pnr.data_model.AgentSign import AgentSign

ATID = "09AC1497"

# Details to inject Edifact messages
log1 = AgentSign("NCE1A0955", "0055AA", "SU")
log2 = AgentSign("NCE1A00QA", "0103FR", "SU")
log3 = AgentSign("NCE1A09PD", "4863AM", "SU")

security_context_user_details_log1 = {
    "organisation": log1.corporation,
    "office_id": log1.office,
    "sign": log1.sign,
    "user_id": "SQA",
    "duty_code": log1.duty_code,
    "atid": ATID,
    "afrom": "1AUTOPY",
    "area_code": "A"
}
security_context_user_details_log2 = {
    "organisation": log2.corporation,
    "office_id": log2.office,
    "sign": log2.sign,
    "user_id": "RESQA",
    "duty_code": log2.duty_code,
    "atid": ATID,
    "afrom": "1AUTOPY",
    "area_code": "A",
}

security_context_user_details_log3 = {
    "organisation": log3.corporation,
    "office_id": log3.office,
    "sign": log3.sign,
    "user_id": "RESQA",
    "duty_code": log3.duty_code,
    "atid": ATID,
    "afrom": "1AUTOPY",
    "area_code": "A",
}



