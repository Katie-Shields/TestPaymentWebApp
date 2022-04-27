import app.main.config as config
import Adyen
import json
import uuid

'''
perform a call to /payments

Taking in the following object from our frontend_request. billingAddress and browserInfo only sent for cards
	{
		paymentMethodData: {
			type: "scheme",
			encryptedCardNumber: "adyenjs_0_1_25$DQ3JeLb...,
			encryptedExpiryMonth: "adyenjs_0_1_25$B1JSCp...,
			encryptedExpiryYear: "adyenjs_0_1_25$h86PBBe...,
			encryptedSecurityCode: "adyenjs_0_1_25$hrwG6...,
			holderName: "Joe Bob"
		},
		billingAddress: {
			street: "Brannan Street",
			city: "San Francisco",
			stateOrProvince: "California",
			postalCode: "94107",
			country: "US",
			houseNumberOrName: 274
		},
		browserInfo: {
			acceptHeader: "*/*",
			colorDepth: 24,
			language: "en-US",
			javaEnabled: false,
			screenHeight: 1440,
			screenWidth: 2560,
			userAgent: "Mozilla/5.0...,
			timeZoneOffset: 480
		}
	};

Will use this as the base of our payment request and add the necessary components from our backend. Feel free to modify
these values in the frontend adyen_implementations.js file or to override them here

Returns JSON representation of response
'''


def adyen_payments(frontend_request):
	adyen = Adyen.Adyen()
	adyen.client.platform = 'test'
	adyen.client.xapikey = config.checkout_apikey

	payment_info = frontend_request.get_json()
	txvariant = payment_info["paymentMethod"]["type"]
	print(payment_info);
	currency = payment_info["amount"]["currency"]
	order_ref = str(uuid.uuid4())
	payments_request = {}

	if currency == "INR":
		payments_request = {
			'channel': 'Web',
			'reference': order_ref,
			'shopperReference': "Katie-demo-1234",
			'returnUrl': "http://localhost:3300/api/handleShopperRedirect?orderRef=" + order_ref,
			'shopperLocale': "en_US",
			'storePaymentMethod': 'true',
			'recurringProcessingModel':'Subscription',
			'merchantAccount': config.merchant_account,
			'mandate': {
		      'amount': 500000,
		      'amountRule': 'max',
		      'frequency': 'adhoc',
		      'endsAt': '2022-12-31',
		      'remarks': 'comment Katie'
		    },
		    'browserInfo': {
		        'timeZoneOffset': -330,
		        'acceptHeader': '*/*',
		        'javaEnabled': 'false',
		        'language': 'EN',
		        'screenWidth': 1920,
		        'screenHeight': 1080,
		        'userAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
		        'colorDepth': 24
		    }
		}
		payments_request.update(payment_info)
	else:
		payments_request = {
			'amount': {
				'value': 1000,
				'currency': choose_currency(txvariant)
			},
			'channel': 'Web',
			'reference': order_ref,
			'shopperReference': "Katie demo Checkout",
			'returnUrl': "http://localhost:3300/api/handleShopperRedirect?orderRef=" + order_ref,
			'countryCode': 'NL',
			'shopperLocale': "en_US",
			'storePaymentMethod': 'true',
			'recurringProcessingModel':'Subscription',
			'merchantAccount': config.merchant_account,
	  		'metadata': {
	      		'Policynumber': 'Policy-123',
	      		'CorrelationId': 'testCorrelationId'
	  		}
		}
		payments_request.update(payment_info)

		if txvariant == 'alipay':
			payments_request['countryCode'] = 'CN'

		elif 'klarna' in txvariant:
			payments_request['countryCode'] = "US"
			payments_request['shopperEmail'] = "myEmail@adyen.com"
			payments_request['lineItems'] = [
				{
					'quantity': "1",
					'amountExcludingTax': "450",
					'taxPercentage': "1111",
					'description': "Sunglasses",
					'id': "Item #1",
					'taxAmount': "50",
					'amountIncludingTax': "500",
					'taxCategory': "High"
				},
				{
					'quantity': "1",
					'amountExcludingTax': "450",
					'taxPercentage': "1111",
					'description': "Headphones",
					'id': "Item #2",
					'taxAmount': "50",
					'amountIncludingTax': "500",
					'taxCategory': "High"
				}]
		elif txvariant == 'directEbanking' or txvariant == 'giropay':
			payments_request['countryCode'] = "DE"

		elif txvariant == 'dotpay':
			payments_request['countryCode'] = "PL"

		elif txvariant == 'scheme':
			payments_request['additionalData'] = {"allow3DS2": "true"}
			payments_request['origin'] = "http://localhost:3300"

		elif txvariant == 'ach' or txvariant == 'paypal':
			payments_request['countryCode'] = 'US'



	print("/payments request:\n" + str(payments_request))

	payments_response = adyen.checkout.payments(payments_request)
	formatted_response = json.dumps((json.loads(payments_response.raw_response)))

	print("/payments response:\n" + formatted_response)
	return formatted_response


def choose_currency(payment_method):
	if payment_method == "alipay":
		return "CNY"
	elif payment_method == "dotpay":
		return "PLN"
	elif payment_method == "boletobancario":
		return "BRL"
	elif payment_method == "ach" or payment_method == "paypal":
		return "USD"
	else:
		return "USD"
