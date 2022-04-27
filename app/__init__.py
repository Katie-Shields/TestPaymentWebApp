import os

from flask import Flask, render_template, send_from_directory, request, redirect, url_for, abort

from .main.config import read_config
from .main.payments import adyen_payments
from .main.payment_methods import adyen_payment_methods
from .main.redirect import handle_shopper_redirect
from .main.additional_details import get_payment_details
import app.main.config as config

# Fusion Application Factory
def create_app():
    app = Flask('app')

    # Register 404 handler
    app.register_error_handler(404, page_not_found)

    # read in values from config.ini file and load them into project
    read_config()

    # Routes:
    @app.route('/')
    def home():
        return render_template('home.html')

    @app.route('/cart/<integration>', defaults={'use_case':None})
    @app.route('/cart/<integration>/<use_case>')
    def cart(integration,use_case):
        return render_template('cart.html', method=integration, use_case=use_case)

    @app.route('/checkout/<integration>', defaults={'use_case':None})
    @app.route('/checkout/<integration>/<use_case>')
    def checkout(integration,use_case):
        client_key = config.client_key

        if integration in config.supported_integrations:
            return render_template('component.html', method=integration, client_key=client_key, use_case=use_case)
        else:
            abort(404)

    @app.route('/api/getPaymentMethods', methods=['GET', 'POST'])
    def get_payment_methods():
        payment_methods_response = adyen_payment_methods()
        return payment_methods_response

    @app.route('/api/initiatePayment', methods=['POST'])
    def initiate_payment():
        payment_response = adyen_payments(request)
        return payment_response

    @app.route('/api/submitAdditionalDetails', methods=['POST'])
    def payment_details():
        details_response = get_payment_details(request)
        return details_response

    @app.route('/api/handleShopperRedirect', methods=['POST', 'GET'])
    def handle_redirect():
        values = request.values.to_dict()  # Get values from query params in request object
        details_request = {}

        if "payload" in values:
            details_request["details"] = {"payload": values["payload"]}
        elif "redirectResult" in values:
            details_request["details"] = {"redirectResult": values["redirectResult"]}

        redirect_response = handle_shopper_redirect(details_request)

        # Redirect shopper to landing page depending on payment success/failure
        if redirect_response["resultCode"] == 'Authorised':
            return redirect(url_for('checkout_success'))
        elif redirect_response["resultCode"] == 'Received' or redirect_response["resultCode"] == 'Pending':
            return redirect(url_for('checkout_pending'))
        else:
            return redirect(url_for('checkout_failure'))

    @app.route('/result/success', methods=['GET'])
    def checkout_success():
        return render_template('checkout-success.html')

    @app.route('/result/failed', methods=['GET'])
    def checkout_failure():
        return render_template('checkout-failed.html')

    @app.route('/result/pending', methods=['GET'])
    def checkout_pending():
        return render_template('checkout-success.html')

    @app.route('/result/error', methods=['GET'])
    def checkout_error():
        return render_template('checkout-failed.html')

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                   'img/favicon.ico')

    @app.route('/inStore', methods=['GET'])
    def in_store():
        return render_template('instore.html')

    @app.route('/payInStore', methods=['GET', 'POST'])
    def payInStore():
        fname=request.form['fname']
        lname=request.form['lname']
        address=request.form['address']
        amount=45
        currency="USD"
        serviceID = str(random.randint(1000000000,9999999999))
        timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        transactionID = "test-payment-"+str(random.randint(100,9999))

        #here we need to call the adyen cloud and initiate the payment via the terminal API then wait for the response from the transaction.
        posAPIkey = config.POS_API_key
        MsgToSend = {
            "SaleToPOIRequest":{
                "MessageHeader":{
                    "ProtocolVersion":"3.0",
                    "MessageClass":"Service",
                    "MessageCategory":"Payment",
                    "MessageType":"Request",
                    "SaleID":"POSSystemID12345",
                    "ServiceID": serviceID,
                    "POIID":"V400m-347290316"
                },
                "PaymentRequest":{
                    "SaleData": {
                        "SaleTransactionID": {
                            "TransactionID": transactionID,
                            "TimeStamp": timestamp
                        }
                    },
                    "PaymentTransaction": {
                        "AmountsReq": {
                            "Currency": currency,
                            "RequestedAmount": amount
                        }

                    }
                }
            }
        }
        res = requests.post('https://terminal-api-test.adyen.com/sync', json=MsgToSend, headers={'X-API-Key':posAPIkey, 'Content-Type':'application/json','Accept':'*/*'})
        print('sent request headers: ')
        print(res.request.headers)
        print('sent request body: ' )
        print(res.request.body)
        print('response from server:' + res.text)
        #dictFromServer = res.json()

        return res.text

    return app


def page_not_found(error):
    return render_template('error.html'), 404
