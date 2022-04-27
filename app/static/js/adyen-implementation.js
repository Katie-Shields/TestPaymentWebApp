const clientKey = JSON.parse(document.getElementById('client-key').innerHTML);
const type = JSON.parse(document.getElementById('integration-type').innerHTML);
const useCase = JSON.parse(document.getElementById('use-case').innerHTML);

var cardConfig = {};

if( useCase === 'IndiaSub' ) {
	cardConfig = {
		hasHolderName: true,
		holderNameRequired: true,
		name: "Credit or debit card",
		countryCode: "IN",
		hideCVC: false,
		amount: {
			value: 45000,
			currency: "INR"
		}
	};
} else {
	cardConfig = {
		hasHolderName: true,
		holderNameRequired: true,
		name: "Credit or debit card",
		hideCVC: false,
		amount: {
			value: 1000,
			currency: "USD"
		}
	};
};

async function initCheckout() {
	try {
		const paymentMethodsResponse = await callServer("/api/getPaymentMethods", {});
		const configuration = {
			paymentMethodsResponse: filterUnimplemented(paymentMethodsResponse),
			clientKey,
			locale: "en_US",
			environment: "test",
			showPayButton: true,
			paymentMethodsConfiguration: {
				klarna_account: {
					amount: {
						value: 1000,
						currency: "USD"
					},
					countryCode: "US"
				},
				ideal: {
					showImage: true
				},
				card: cardConfig,
				paypal: {
					amount: {
						currency: "USD",
						value: 1000
					},
					environment: "test", // Change this to "live" when you're ready to accept live PayPal payments
					countryCode: "US" // Only needed for test. This will be automatically retrieved when you are in production
				},
				paywithgoogle: {
					configuration: {
					    gatewayMerchantId: "KatieShields"
					},
					environment: "TEST",
					amount: {
						currency: "USD",
						value: 1000
					},
					allowedAuthMethods: ['PAN_ONLY'],
					allowPrepaidCards:false
				}
			},
			onSubmit: (state, component) => {
				console.log(state);
				console.log (component);

				if (state.isValid) {
					handleSubmission(state, component, "/api/initiatePayment");
				}
			},
			onAdditionalDetails: (state, component) => {
				handleSubmission(state, component, "/api/submitAdditionalDetails");
			}
		};

		const checkout = new AdyenCheckout(configuration);
		checkout.create(type).mount("#component");
	} catch (error) {
		console.error(error);
		alert("Error occurred. Look at console for details");
	}
}

function filterUnimplemented(pm) {
	pm.paymentMethods = pm.paymentMethods.filter((it) =>
		[
			"scheme",
			"ideal",
			"dotpay",
			"giropay",
			"sepadirectdebit",
			"directEbanking",
			"ach",
			"alipay",
			"applepay",
			"klarna_paynow",
			"klarna",
			"klarna_account",
			"paypal",
			"boletobancario_santander",
			"paywithgoogle"
		].includes(it.type)
	);
	return pm;
}

// Event handlers called when the shopper selects the pay button,
// or when additional information is required to complete the payment
async function handleSubmission(state, component, url) {
	try {
		state.data.amount = component.props.amount;
		console.log(state.data.amount);
		const res = await callServer(url, state.data);
		handleServerResponse(res, component);
	} catch (error) {
		console.error(error);
		alert("Error occurred. Look at console for details");
	}
}

// Calls your server endpoints
async function callServer(url, data) {
	const res = await fetch(url, {
		method: "POST",
		body: data ? JSON.stringify(data) : "",
		headers: {
			"Content-Type": "application/json"
		}
	});

	return await res.json();
}

// Handles responses sent from your server to the client
function handleServerResponse(res, component) {
	if (res.action) {
		component.handleAction(res.action);
	} else {
		switch (res.resultCode) {
			case "Authorised":
				window.location.href = "/result/success";
				break;
			case "Pending":
			case "Received":
				window.location.href = "/result/pending";
				break;
			case "Refused":
				window.location.href = "/result/failed";
				break;
			default:
				window.location.href = "/result/error";
				break;
		}
	}
}

initCheckout();
