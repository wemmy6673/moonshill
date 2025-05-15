import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { createFetcher } from "../../lib/fetcher";
import useSnack from "../../hooks/useSnack";
import config from "../../lib/config";
import { useEffect, useRef, useCallback } from "react";
import ErrorView from "../common/ErrorView";
import PageLoader from "../common/PageLoader";

const CampaignSettings = ({ auth, campaign }) => {
	const snack = useSnack();
	const queryClient = useQueryClient();
	const debounceTimers = useRef({});

	const {
		data: campaignSettings,
		isPending: isLoadingCampaignSettings,
		isError: isErrorCampaignSettings,
		refetch: refetchCampaignSettings,
	} = useQuery({
		queryKey: ["campaignSettings", campaign.id],
		queryFn: createFetcher({
			method: "GET",
			url: `${config.endpoints.getCampaignSettings}/${campaign.id}`,
			auth,
		}),
	});

	const {
		mutate: updateCampaignSettings,
		isPending: isUpdatingCampaignSettings,
		isError: isErrorUpdatingCampaignSettings,
		error: errorUpdatingCampaignSettings,
		isSuccess: isSuccessUpdatingCampaignSettings,
		reset: resetUpdatingCampaignSettings,
	} = useMutation({
		mutationFn: createFetcher({
			method: "PUT",
			url: `${config.endpoints.updateCampaignSettings}/${campaign.id}`,
			auth,
		}),
	});

	useEffect(() => {
		if (isErrorUpdatingCampaignSettings) {
			snack.error(errorUpdatingCampaignSettings.message);
			resetUpdatingCampaignSettings();
		}
		if (isSuccessUpdatingCampaignSettings) {
			queryClient.invalidateQueries({ queryKey: ["campaignSettings", campaign.id] });
			snack.success("Campaign settings updated successfully");
		}
	}, [isErrorUpdatingCampaignSettings, errorUpdatingCampaignSettings, isSuccessUpdatingCampaignSettings]);

	// Cleanup debounce timers on unmount
	useEffect(() => {
		return () => {
			Object.values(debounceTimers.current).forEach((timer) => clearTimeout(timer));
		};
	}, []);

	const handleUpdateCampaignSettings = useCallback(
		(fieldName, value) => {
			// Clear existing timer for this field if it exists
			if (debounceTimers.current[fieldName]) {
				clearTimeout(debounceTimers.current[fieldName]);
			}

			// Set new timer for this field
			debounceTimers.current[fieldName] = setTimeout(() => {
				updateCampaignSettings({
					fieldName,
					value,
				});
				// Clear the timer reference after it's executed
				delete debounceTimers.current[fieldName];
			}, 500); // 500ms debounce delay
		},
		[updateCampaignSettings]
	);

	if (isLoadingCampaignSettings) {
		return <PageLoader isPageWide={false} />;
	}

	if (isErrorCampaignSettings) {
		return <ErrorView message="Failed to load campaign settings" retryFunc={refetchCampaignSettings} />;
	}

	const settings = campaignSettings || {};

	return (
		<div data-tab-content="settings" className="space-y-8">
			{/* Content Generation */}
			<div className="bg-white/5 rounded-xl p-6">
				<div className="flex items-center justify-between mb-6">
					<div>
						<h3 className="text-lg font-medium text-white">Content Generation</h3>
						<p className="mt-1 text-sm text-white/60">Control how content is generated and managed</p>
					</div>
					<div className="w-10 h-10 rounded-full bg-[#007AFF]/10 flex items-center justify-center">
						<svg className="w-5 h-5 text-[#007AFF]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path
								strokeLinecap="round"
								strokeLinejoin="round"
								strokeWidth={2}
								d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
							/>
						</svg>
					</div>
				</div>
				<div className="space-y-6">
					<div className="flex items-center justify-between">
						<div>
							<div className="font-medium text-white">Content Filtering</div>
							<div className="text-sm text-white/60">Filter out inappropriate content</div>
						</div>
						<label className="relative inline-flex items-center cursor-pointer">
							<input
								type="checkbox"
								className="sr-only peer"
								checked={settings.content_filtering}
								onChange={(e) => handleUpdateCampaignSettings("content_filtering", e.target.checked)}
							/>
							<div className="w-11 h-6 bg-white/10 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#007AFF]"></div>
						</label>
					</div>

					<div className="flex items-center justify-between">
						<div>
							<div className="font-medium text-white">Posts Per Day</div>
							<div className="text-sm text-white/60">Maximum daily post limit</div>
						</div>
						<div className="flex items-center gap-4">
							<input
								type="range"
								min="1"
								max="20"
								value={settings.max_daily_posts || 10}
								onChange={(e) => handleUpdateCampaignSettings("max_daily_posts", parseInt(e.target.value))}
								className="w-32 h-1 bg-white/10 rounded-lg appearance-none cursor-pointer accent-[#007AFF]"
							/>
							<span className="text-sm text-white/80 min-w-[2rem]">{settings.max_daily_posts || 10}</span>
						</div>
					</div>

					<div className="flex items-center justify-between">
						<div>
							<div className="font-medium text-white">Content Style</div>
							<div className="text-sm text-white/60">Tone of generated content</div>
						</div>
						<select
							className="bg-white/10 border-0 rounded-lg text-white text-sm focus:ring-2 focus:ring-[#007AFF] px-3 py-2"
							value={settings.language_style || "professional"}
							onChange={(e) => handleUpdateCampaignSettings("language_style", e.target.value)}
						>
							<option className="bg-[#1a1a1a] text-white" value="professional">
								Professional
							</option>
							<option className="bg-[#1a1a1a] text-white" value="casual">
								Casual
							</option>
							<option className="bg-[#1a1a1a] text-white" value="mixed">
								Mixed
							</option>
						</select>
					</div>
				</div>
			</div>

			{/* Engagement Settings */}
			<div className="bg-white/5 rounded-xl p-6">
				<div className="flex items-center justify-between mb-6">
					<div>
						<h3 className="text-lg font-medium text-white">Engagement</h3>
						<p className="mt-1 text-sm text-white/60">Configure how we engage with your community</p>
					</div>
					<div className="w-10 h-10 rounded-full bg-[#007AFF]/10 flex items-center justify-center">
						<svg className="w-5 h-5 text-[#007AFF]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path
								strokeLinecap="round"
								strokeLinejoin="round"
								strokeWidth={2}
								d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z"
							/>
						</svg>
					</div>
				</div>
				<div className="space-y-6">
					<div className="flex items-center justify-between">
						<div>
							<div className="font-medium text-white">Auto-Reply</div>
							<div className="text-sm text-white/60">Automatically respond to mentions and messages</div>
						</div>
						<label className="relative inline-flex items-center cursor-pointer">
							<input
								type="checkbox"
								className="sr-only peer"
								checked={settings.auto_reply}
								onChange={(e) => handleUpdateCampaignSettings("auto_reply", e.target.checked)}
							/>
							<div className="w-11 h-6 bg-white/10 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#007AFF]"></div>
						</label>
					</div>

					<div className="flex items-center justify-between">
						<div>
							<div className="font-medium text-white">AI Response Speed</div>
							<div className="text-sm text-white/60">Balance between speed and quality</div>
						</div>
						<select
							className="bg-white/10 border-0 rounded-lg text-white text-sm focus:ring-2 focus:ring-[#007AFF] px-3 py-2"
							value={settings.ai_response_speed || "balanced"}
							onChange={(e) => handleUpdateCampaignSettings("ai_response_speed", e.target.value)}
						>
							<option className="bg-[#1a1a1a] text-white" value="fast">
								Fast
							</option>
							<option className="bg-[#1a1a1a] text-white" value="balanced">
								Balanced
							</option>
							<option className="bg-[#1a1a1a] text-white" value="thorough">
								Thorough
							</option>
						</select>
					</div>

					<div className="flex items-center justify-between">
						<div>
							<div className="font-medium text-white">Engagement Hours</div>
							<div className="text-sm text-white/60">Active hours for engagement</div>
						</div>
						<div className="flex items-center gap-2 text-sm">
							<input
								type="time"
								value={settings.engagement_hours?.start || "09:00"}
								onChange={(e) =>
									handleUpdateCampaignSettings("engagement_hours", {
										...settings.engagement_hours,
										start: e.target.value,
									})
								}
								className="bg-white/10 border-0 rounded-lg text-white focus:ring-2 focus:ring-[#007AFF] px-3 py-2"
							/>
							<span className="text-white/60">to</span>
							<input
								type="time"
								value={settings.engagement_hours?.end || "21:00"}
								onChange={(e) =>
									handleUpdateCampaignSettings("engagement_hours", {
										...settings.engagement_hours,
										end: e.target.value,
									})
								}
								className="bg-white/10 border-0 rounded-lg text-white focus:ring-2 focus:ring-[#007AFF] px-3 py-2"
							/>
						</div>
					</div>
				</div>
			</div>

			{/* Safety & Compliance */}
			<div className="bg-white/5 rounded-xl p-6">
				<div className="flex items-center justify-between mb-6">
					<div>
						<h3 className="text-lg font-medium text-white">Safety & Compliance</h3>
						<p className="mt-1 text-sm text-white/60">Protect your campaign and community</p>
					</div>
					<div className="w-10 h-10 rounded-full bg-[#007AFF]/10 flex items-center justify-center">
						<svg className="w-5 h-5 text-[#007AFF]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path
								strokeLinecap="round"
								strokeLinejoin="round"
								strokeWidth={2}
								d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
							/>
						</svg>
					</div>
				</div>
				<div className="space-y-6">
					<div className="flex items-center justify-between">
						<div>
							<div className="font-medium text-white">Spam Detection</div>
							<div className="text-sm text-white/60">Automatically filter spam content</div>
						</div>
						<label className="relative inline-flex items-center cursor-pointer">
							<input
								type="checkbox"
								className="sr-only peer"
								checked={settings.spam_detection}
								onChange={(e) => handleUpdateCampaignSettings("spam_detection", e.target.checked)}
							/>
							<div className="w-11 h-6 bg-white/10 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#007AFF]"></div>
						</label>
					</div>

					<div className="flex items-center justify-between">
						<div>
							<div className="font-medium text-white">Risk Level</div>
							<div className="text-sm text-white/60">Set campaign risk tolerance and content moderation level</div>
							<div className="mt-1 text-xs text-white/40">
								Conservative: Strict content filtering, slower posting
								<br />
								Moderate: Balanced approach with standard safeguards
								<br />
								Aggressive: Faster posting, minimal content restrictions
							</div>
						</div>
						<select
							className="bg-white/10 border-0 rounded-lg text-white text-sm focus:ring-2 focus:ring-[#007AFF] px-3 py-2"
							value={settings.risk_level || "moderate"}
							onChange={(e) => handleUpdateCampaignSettings("risk_level", e.target.value)}
						>
							<option className="bg-[#1a1a1a] text-white" value="conservative">
								Conservative
							</option>
							<option className="bg-[#1a1a1a] text-white" value="moderate">
								Moderate
							</option>
							<option className="bg-[#1a1a1a] text-white" value="aggressive">
								Aggressive
							</option>
						</select>
					</div>

					<div className="flex items-center justify-between">
						<div>
							<div className="font-medium text-white">Emergency Stop</div>
							<div className="text-sm text-white/60">Pause all activity immediately</div>
						</div>
						<label className="relative inline-flex items-center cursor-pointer">
							<input
								type="checkbox"
								className="sr-only peer"
								checked={settings.emergency_stop_enabled}
								onChange={(e) => handleUpdateCampaignSettings("emergency_stop_enabled", e.target.checked)}
							/>
							<div className="w-11 h-6 bg-white/10 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#007AFF]"></div>
						</label>
					</div>
				</div>
			</div>
		</div>
	);
};

export default CampaignSettings;
