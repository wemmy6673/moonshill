import { useQuery, useQueryClient } from "@tanstack/react-query";
import { createFetcher } from "../libs/fetcher";
import config from "../libs/config";
import { useState } from "react";
import { getStorage, isStorageAvailable, removeStorage } from "../libs/browserutils";

const useWorkspace = () => {
	const queryClient = useQueryClient();

	let accessToken = isStorageAvailable() ? getStorage("workspaceAccessToken") : null;

	const [accessTokenState, setAccessTokenState] = useState(accessToken);

	const { data, isPending, isSuccess } = useQuery({
		queryKey: ["workspace", accessTokenState],
		queryFn: createFetcher({
			method: "GET",
			url: config.endpoints.getCurrentWorkspace,
			auth: accessTokenState,
		}),

		refetchInterval: 15000,
	});

	return {
		workspace: data ? data.workspace : null,
		pending: isPending && !isSuccess,
		accessToken: accessTokenState,
		logOut: () => {
			removeStorage("workspaceAccessToken");
			setAccessTokenState(null);
			queryClient.invalidateQueries({ queryKey: ["workspace", accessTokenState] });
		},
	};
};

export default useWorkspace;
