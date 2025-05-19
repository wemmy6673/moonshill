const config = {
	apiUrl: import.meta.env.VITE_API_URL || "http://localhost:7001",

	endpoints: {
		createWorkspace: "/api/workspaces",
		getAccessToken: "/api/workspaces/access-token",
		getCurrentWorkspace: "/api/workspaces/current",
		createCampaign: "/api/campaigns",
		getCampaigns: "/api/campaigns",
		getCampaign: "/api/campaigns",
		updateCampaign: "/api/campaigns",
		deleteCampaign: "/api/campaigns",
		updateTokenomics: "/api/campaigns/tokenomics",
		updateTechnicalInfo: "/api/campaigns/technical",
		updateMarketInfo: "/api/campaigns/market",
		getCampaignSettings: "/api/campaigns/settings",
		updateCampaignSettings: "/api/campaigns/settings",
		connectPlatform: "/api/platforms/connect",
		platformCallback: "/api/platforms/callbacks",
		getCampaignConnectionStatus: "/api/platforms/statuses",
		disconnectPlatform: "/api/platforms/disconnect",
		togglePublish: "/api/campaigns/toggle-publish",
	},
};

export default config;
