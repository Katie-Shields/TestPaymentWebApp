import os
'''
Read in variables from config.ini file. Store them as global variables

Make sure to fill out your config.ini file!!!
'''

merchant_account = ""
checkout_apikey = ""
client_key = ""
POS_API_key = ""
supported_integrations = ['dropin', 'card', 'ideal', 'klarna', 'klarna_account','directEbanking', 'alipay', 'boletobancario',
                          'sepadirectdebit', 'dotpay', 'giropay', 'ach', 'paypal', 'applepay', 'paywithgoogle']


def read_config():
    global merchant_account, checkout_apikey, client_key, POS_API_key



    merchant_account = os.environ['MERCHANT_ACCOUNT']
    checkout_apikey = os.environ['X_API_KEY']
    client_key = os.environ['CLIENT_KEY']
    POS_API_key = os.environ['POS_API_KEY']

    # Check to make sure variables are set
    if not merchant_account or not checkout_apikey or not client_key or not POS_API_key:
        raise Exception("Please fill out information in config.ini file")
