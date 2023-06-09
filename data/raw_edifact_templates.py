"""
Raw Edifact Templates
"""

IGNORE_CONTEXT_RAW = r"""UNH+1+PNRADD:14:1:1A'
ORG+00+:{var[office_id]}+++E+EN:EUR:EN+{var[sign]}'
OPT+20'
UNT+5+1'
"""

IGNORE_CONTEXT = {
    "query": IGNORE_CONTEXT_RAW,
    "response": "PNRACC",
}


FSPTBQ = """UNH+1+FSPTBQ:20:2:1A'
ORG+00+12345675:NCE1A21EC:MUC1A0701+NCE+DCD001000000+T+FR:EUR:EN+A0012NRSU+09AA0E7D'
EQN+20:RC*2:PX'
PTC+CH+1'
PTC+ADT+2'
PTK'
ATC++NPS:0*FFI:1'
ODR+1'
DPT+::NCE'
ARR+::LGW'
DAT+:210522'
TFI++M:U2'
UNT+14+1'
"""
TOKEN_REQUEST_RAW = r"""UNH+1+SPWREQ:09:1:1A+0001V8DYLSC1T8'&
DCX+939+<DCC VERS="1.0"><MW><UKEY VAL="M929QWRY51EU1FYKVTNY$4RCD1" TRXNB="1-1"/><SAP NAME="1ASIUAPSGUID" FARM="EXT" DCNAME="MUC" ENC="U8"/><DYNR><PEAKTK TYPE="AIRIT" VAL="1A"/><PEAKTK TYPE="ETK_PTT" VAL="E1A"/></DYNR></MW><SEC VERS="2.11" CONTENTS="UNDEFINED"><USERINFOS><OFFICEID VALUE="NCE1A09PD"/><SIGN VALUE="8936RT"/><SIGN_OFFICE VALUE="NCE1A09PD"/><OOFF VALUE="NCE1A09PD"/><AREACODE VALUE="A"/><DCD VALUE="DCD000000000"/><USERID VALUE="RTHIRION"/><ORGANIZATION VALUE="1A"/><COUNTRY VALUE="FR"/><ORIGINTYPECODE VALUE="A"/><VND VALUE="AMAD"/><TCC VALUE="NCE"/><CPI VALUE="00"/><ALS VALUE="RTHIRION"/><J VAL="01"/><IUS VAL="RTHIRION"/><IOF VAL="NCE1A09PD"/><ISI VAL="8936RT"/><IOG VAL="1A"/></USERINFOS><USERSETTINGS><DUTYCODE VALUE="SU"/></USERSETTINGS><PREFERENCES><LANGUAGE VALUE="EN"/><CURRENCY VALUE="EUR"/></PREFERENCES><SECURITYINDICATORS VALUE="YY7"/><SIGNER VAL="L"/><AUTHL FLG="S"/></SEC><TRX><SRC IP="10.64.36.53:13685"/></TRX></DCC>'&
SPW+AMADEUS+/multi/login_with_password/+HTTP:POST:application/json'&
ATR++api-key:0Rm5hK8JjOsBh1YJS2oBDQ=='&
BLB+61+B+{"email":"zakaria.najib@outpayce.com","password":{"value":"Pass1234"}}'
"""

TOKEN_REQUEST = {
    "query": TOKEN_REQUEST_RAW,
    "response": "SPWRES",
}