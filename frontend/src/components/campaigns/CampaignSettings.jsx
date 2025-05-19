import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { createFetcher } from "../../libs/fetcher";
import useSnack from "../../hooks/useSnack";
import config from "../../libs/config";
import { useEffect, useRef, useCallback } from "react";
import ErrorView from "../common/ErrorView";
import PageLoader from "../common/PageLoader";

// Mapping between API field names and frontend field names
const FIELD_MAPPING = {
	// Basic settings
	content_filtering: "contentFiltering",
	meme_generation: "memeGeneration",
	sentiment_analysis: "sentimentAnalysis",
	content_approval_required: "contentApprovalRequired",
	max_daily_posts: "maxDailyPosts",
	min_time_between_posts: "minTimeBetweenPosts",

	// Language settings
	language_style: "languageStyle",
	emoji_usage: "emojiUsage",
	hashtag_usage: "hashtagUsage",
	max_hashtags_per_post: "maxHashtagsPerPost",

	// Platform settings
	platform_settings: "platformSettings",
	cross_posting: "crossPosting",
	platform_rotation: "platformRotation",

	// Engagement settings
	auto_reply: "autoReply",
	reply_to_mentions: "replyToMentions",
	engage_with_comments: "engageWithComments",
	max_daily_replies: "maxDailyReplies",
	engagement_hours: "engagementHours",

	// Community settings
	community_guidelines: "communityGuidelines",
	blocked_users: "blockedUsers",
	blocked_keywords: "blockedKeywords",
	auto_moderation: "autoModeration",
	spam_detection: "spamDetection",

	// Analytics settings
	tracking_enabled: "trackingEnabled",
	analytics_granularity: "analyticsGranularity",
	performance_alerts: "performanceAlerts",
	alert_thresholds: "alertThresholds",

	// AI settings
	ai_creativity_level: "aiCreativityLevel",
	ai_response_speed: "aiResponseSpeed",
	ai_memory_retention: "aiMemoryRetention",
	ai_learning_enabled: "aiLearningEnabled",

	// Risk settings
	risk_level: "riskLevel",
	compliance_check_level: "complianceCheckLevel",
	content_backup_enabled: "contentBackupEnabled",
	emergency_stop_enabled: "emergencyStopEnabled",

	// Rate limiting
	rate_limiting_enabled: "rateLimitingEnabled",
	rate_limits: "rateLimits",
};

// Reverse mapping for frontend to API conversion
const REVERSE_FIELD_MAPPING = Object.fromEntries(Object.entries(FIELD_MAPPING).map(([key, value]) => [value, key]));

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

		refetchInterval: 10000,
	});

	const {
		mutate: updateCampaignSettings,

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
			// Revert back to the previous value if there's an error
			const previousSettings = queryClient.getQueryData(["campaignSettings", campaign.id]);
			if (previousSettings) {
				queryClient.setQueryData(["campaignSettings", campaign.id], previousSettings);
			}
			snack.error(errorUpdatingCampaignSettings.message || "Failed to update campaign settings");
			resetUpdatingCampaignSettings();
		}
		if (isSuccessUpdatingCampaignSettings) {
			snack.success("Campaign settings updated");
			queryClient.invalidateQueries({ queryKey: ["campaignSettings", campaign.id] });
		}
	}, [isErrorUpdatingCampaignSettings, errorUpdatingCampaignSettings, isSuccessUpdatingCampaignSettings]);

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
				// Convert frontend field name to API field name if needed
				const apiFieldName = REVERSE_FIELD_MAPPING[fieldName] || fieldName;

				// Optimistically update to the new value
				queryClient.setQueryData(["campaignSettings", campaign.id], (old) => {
					const newSettings = { ...old };
					const frontendFieldName = FIELD_MAPPING[apiFieldName];

					if (!frontendFieldName) {
						console.warn(`No mapping found for field: ${apiFieldName}`);
						return old;
					}

					// Handle nested fields (e.g., engagement_hours)
					if (frontendFieldName.includes(".")) {
						const [parent, child] = frontendFieldName.split(".");
						newSettings[parent] = {
							...newSettings[parent],
							[child]: value,
						};
					} else {
						newSettings[frontendFieldName] = value;
					}

					return newSettings;
				});

				updateCampaignSettings({
					fieldName: apiFieldName,
					value,
				});

				delete debounceTimers.current[fieldName];
			}, 500);
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
						<h3 className="text-lg font-semibold bg-gradient-to-r from-[#007AFF] to-[#00C6FF] bg-clip-text text-transparent">
							Content Generation
						</h3>
						<p className="mt-2 text-sm text-white/60">Control how content is generated and managed</p>
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
								checked={settings.contentFiltering}
								onChange={(e) => handleUpdateCampaignSettings("contentFiltering", e.target.checked)}
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
								value={settings.maxDailyPosts || 10}
								onChange={(e) => handleUpdateCampaignSettings("maxDailyPosts", parseInt(e.target.value))}
								className="w-32 h-1 bg-white/10 rounded-lg appearance-none cursor-pointer accent-[#007AFF]"
							/>
							<span className="text-sm text-white/80 min-w-[2rem]">{settings.maxDailyPosts || 10}</span>
						</div>
					</div>

					<div className="flex items-center justify-between">
						<div>
							<div className="font-medium text-white">Language Style</div>
							<div className="text-sm text-white/60">Tone of generated content</div>
						</div>
						<select
							className="bg-white/10 border-0 rounded-lg text-white text-sm focus:ring-2 focus:ring-[#007AFF] px-3 py-2"
							value={settings.languageStyle || "professional"}
							onChange={(e) => handleUpdateCampaignSettings("languageStyle", e.target.value)}
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
						<h3 className="text-lg font-semibold bg-gradient-to-r from-[#007AFF] to-[#00C6FF] bg-clip-text text-transparent">
							Engagement
						</h3>
						<p className="mt-2 text-sm text-white/60">Configure how we engage with your community</p>
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
							<div className="text-sm text-white/60">Automatically respond to tags, mentions and select comments</div>
						</div>
						<label className="relative inline-flex items-center cursor-pointer">
							<input
								type="checkbox"
								className="sr-only peer"
								checked={settings.autoReply}
								onChange={(e) => handleUpdateCampaignSettings("autoReply", e.target.checked)}
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
							value={settings.aiResponseSpeed || "balanced"}
							onChange={(e) => handleUpdateCampaignSettings("aiResponseSpeed", e.target.value)}
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
								value={settings.engagementHours?.start || "09:00"}
								onChange={(e) =>
									handleUpdateCampaignSettings("engagementHours", {
										...settings.engagementHours,
										start: e.target.value,
									})
								}
								className="bg-white/10 border-0 rounded-lg text-white focus:ring-2 focus:ring-[#007AFF] px-3 py-2"
							/>
							<span className="text-white/60">to</span>
							<input
								type="time"
								value={settings.engagementHours?.end || "21:00"}
								onChange={(e) =>
									handleUpdateCampaignSettings("engagementHours", {
										...settings.engagementHours,
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
						<h3 className="text-lg font-semibold bg-gradient-to-r from-[#007AFF] to-[#00C6FF] bg-clip-text text-transparent">
							Safety & Compliance
						</h3>
						<p className="mt-2 text-sm text-white/60">Protect your campaign and community</p>
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
								checked={settings.spamDetection}
								onChange={(e) => handleUpdateCampaignSettings("spamDetection", e.target.checked)}
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
							value={settings.riskLevel || "moderate"}
							onChange={(e) => handleUpdateCampaignSettings("riskLevel", e.target.value)}
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
								checked={settings.emergencyStopEnabled}
								onChange={(e) => handleUpdateCampaignSettings("emergencyStopEnabled", e.target.checked)}
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
