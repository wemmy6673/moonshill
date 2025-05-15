import config from "./config";

export function makeUrl(pathname) {
	return `${config.apiUrl}${pathname}`;
}

export async function fetchUtil({
	url,
	surfix = "",
	method,
	body,
	formEncoded = false,
	auth = null,
	headers = {},
	opts = {},
}) {
	const options = {
		credentials: "omit",
		method,
		...opts,
	};

	if (method === "POST" || method === "PUT") {
		if (formEncoded) {
			const form = new FormData();
			for (let key of Object.keys(body)) {
				form.append(key, body[key]);
			}

			options.body = form;
			// console.log(form)
		} else {
			options.body = JSON.stringify(body);
			options.headers = {
				...options.headers,
				"Content-Type": "application/json",
			};
		}
	}

	if (auth) {
		options.headers = {
			...options.headers,
			Authorization: `${auth.tokenType || auth.token_type} ${auth.accessToken || auth.access_token}`,
		};
	}

	if (headers) {
		options.headers = {
			...options.headers,
			...headers,
		};

		try {
			const res = await fetch(url + surfix, options);

			if (res.ok) {
				return {
					success: true,
					data: await res.json(),
					headers: res.headers,
				};
			} else {
				const json = await res.json();
				console.log("fetchUtil: ", json);
				return {
					success: false,
					errorMessage: json?.detail?.message || res.statusText,
					statusText: res.statusText,
					status: res.status,
					error: json,
					headers: res.headers,
				};
			}
		} catch (err) {
			console.log("fetchUtil: ", err.message);
			return {
				success: false,
				errorMessage: err.message,
				statusText: null,
				status: null,
			};
		}
	}
}

export function createFetcher({ url, method, body = null, surfix = "", auth = null, formEncoded = false }) {
	return async (params = null) => {
		const res = await fetchUtil({
			url: makeUrl(url),
			method,
			body: body || params,
			surfix,
			auth,
			formEncoded,
		});

		if (res.success) {
			return res.data;
		}

		console.log("createFetcher Error: ", res.error);

		const extractedErrorMsg = extractErrorMessage(res);

		let action = null;

		if (res.headers && res.headers.has("X-ACTION")) {
			action = res.headers.get("X-ACTION");
		}

		const errorObj = {
			message: extractedErrorMsg,
			action,
		};

		throw errorObj;
	};
}

export function extractErrorMessage(res) {
	const msg = getErrMsg(res);

	if (typeof msg === "string") {
		return msg;
	}

	if (typeof msg === "object") {
		return JSON.stringify(msg);
	}

	return "An unknown error occurred";
}

export function getErrMsg(res) {
	if (typeof res === "string") {
		return res;
	}

	if (res instanceof Error) {
		return res?.message;
	}

	if (typeof res.error === "object") {
		return res.error.detail || res.error.message || res.error.error;
	}

	if (typeof res.errorMessage === "string") {
		return res.errorMessage;
	}

	if (typeof res.statusText === "string") {
		return res.statusText;
	}

	return res;
}

export const fetcher = createFetcher;
