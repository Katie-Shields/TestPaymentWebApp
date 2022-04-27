async function initGiving() {
	try {

    function handleOnDonate(state, component) {
      state.isValid // True or false. Specifies whether the shopper has selected a donation amount.
      state.data // Provides the data that you need to pass in the `/donate` call.
      component // Provides the active component instance that called this event.
			if(state.isValid) {
				try {
					const res = await callServer("api/initiateDonation", state.data);
					handleServerResponse(res, component);
				} catch (error) {
					console.error(error);
					alert("Error occurred. Look at console for details");
				}
			}
    }

    function handleOnCancel(state, component) {
    // Show a message, unmount the component, or redirect to another page.
    }

  const donationConfig = {
      amounts: {
          currency: "USD",
          values: [300, 500, 1000]
      },
      backgroundUrl: "https://example.org/background.png",
      description: "The Charitable Foundation is...",
      logoUrl: "https://example.org/logo.png",
      name: "The Charitable Foundation",
      url: "https://example.org",
      showCancelButton: true,
      onDonate: handleOnDonate,
      onCancel: handleOnCancel
  };

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


initGiving();
