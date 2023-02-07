OFFICE_KEY_NAME = 'name'
OFFICE_KEY_SIGN = 'sign'
OFFICE_KEY_DUTY_CODE = 'duty_code'
OFFICE_KEY_SIGN_CRYPTIC =  'sign_cryptic'
OFFICE_KEY_ORGA = 'orga'
OFFICE_KEY_USER = 'user'
OFFICE_KEY_PWD = 'pwd'
OFFICE_KEY_SIGN_WBS =  'sign_wbs'

# Esky user : Role restricted view only list of cards 
USER_ESKY= {
        OFFICE_KEY_NAME: 'FRAEY38EF',
        OFFICE_KEY_SIGN: '0003BB',
        OFFICE_KEY_SIGN_CRYPTIC: '0003BB',
        OFFICE_KEY_DUTY_CODE: 'SU',
        OFFICE_KEY_SIGN_WBS: 'B2BWESKY',
        OFFICE_KEY_USER: 'B2BWESKY',
        OFFICE_KEY_PWD: "eSky0302",
        OFFICE_KEY_ORGA: 'NMC-GERMAN'
}

# Admin user : Role all b2b permissions, view cards for the whole metagroup
APPUI1A01 = {
        OFFICE_KEY_NAME: 'NCE1A0955',
        OFFICE_KEY_SIGN: '0003BB',
        OFFICE_KEY_SIGN_CRYPTIC: '0003BB',
        OFFICE_KEY_DUTY_CODE: 'SU',
        OFFICE_KEY_SIGN_WBS: 'APPUI1A01',
        OFFICE_KEY_USER: 'APPUI1A01',
        OFFICE_KEY_PWD: "appui1a01",
        OFFICE_KEY_ORGA: '1A'

}

# Admin user : Role all b2b permissions, view cards for the whole metagroup
Resources/libs/test_users.py

USER_B2BW_USER2_DEV = {
        OFFICE_KEY_NAME: 'NCE1A0955',
        OFFICE_KEY_SIGN: '0333BB',
        OFFICE_KEY_SIGN_CRYPTIC: '0333BB',
        OFFICE_KEY_DUTY_CODE: 'SU',
        OFFICE_KEY_ORGA: '1A',
        OFFICE_KEY_USER: 'B2BW_USER2',
        OFFICE_KEY_PWD: 'B2BW_USER2_37'
}

USER_B2BW_USER2_FVT = {
                OFFICE_KEY_NAME: 'NCE1A0955',
                OFFICE_KEY_SIGN: '0333BB',
                OFFICE_KEY_SIGN_CRYPTIC: '0333BB',
                OFFICE_KEY_DUTY_CODE: 'SU',
                OFFICE_KEY_ORGA: '1A',
                OFFICE_KEY_USER: 'B2BW_USER2',
                OFFICE_KEY_PWD: 'B2BW_USER2_234'
}

# Admin user : Role all b2b permissions, view cards only for his own office
USER_B2BW_USER1 = {
        OFFICE_KEY_NAME: 'NCE1A0950',
        OFFICE_KEY_SIGN: '0109BB',
        OFFICE_KEY_SIGN_CRYPTIC: '0109BB',
        OFFICE_KEY_DUTY_CODE: 'SU',
        OFFICE_KEY_ORGA: '1A',
        OFFICE_KEY_USER: 'B2BW_USER1',
        OFFICE_KEY_PWD: 'B2BW_USER1_23'
}

# Admin user : Role all b2b permissions, view cards for the whole metagroup
USER_PCIDSS3 = {
        OFFICE_KEY_NAME: 'NCE1A0950',
        OFFICE_KEY_SIGN: '8162FL',
        OFFICE_KEY_SIGN_CRYPTIC: '8162FL',
        OFFICE_KEY_DUTY_CODE: 'SU',
        OFFICE_KEY_ORGA: '1A',
        OFFICE_KEY_USER: 'PCIDSS3',
        OFFICE_KEY_PWD: 'amadeus22'
}