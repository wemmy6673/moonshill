import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import useSnack from "@/hooks/useSnack";
import useWorkspace from "@/hooks/useWorkspace";
import { useLocation, useParams } from "wouter";
import PageLoader from "@/components/common/PageLoader";
import ErrorView from "@/components/common/ErrorView";
import ConfirmDialog from "@/components/common/ConfirmDialog";
import { createFetcher } from "@/lib/fetcher";
import config from "../lib/config";
import CampaignForm from "@/components/campaigns/CampaignForm";
import AuthenticatedHeader from "@/components/common/AuthenticatedHeader";

const CampaignDetails = () => {
	const { id } = useParams();
	const [, navigate] = useLocation();
	const snack = useSnack();
	const queryClient = useQueryClient();
	const [isEditing, setIsEditing] = useState(false);
	const [activeTab, setActiveTab] = useState("overview");
	const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

	const { workspace, pending: workspacePending, logOut, accessToken } = useWorkspace();

	// Fetch campaign details
	const {
		data: campaign,
		isPending,
		refetch,
		isError,
	} = useQuery({
		queryKey: ["campaign", id],
		queryFn: createFetcher({
			url: `${config.endpoints.getCampaign}/${id}`,
			method: "GET",
			auth: accessToken,
		}),
		enabled: !!id && !!workspace,
	});

	// Delete campaign mutation
	const deleteMutation = useMutation({
		mutationFn: createFetcher({
			url: `${config.endpoints.deleteCampaign}/${id}`,
			method: "DELETE",
			auth: accessToken,
		}),
	});

	useEffect(() => {
		if (deleteMutation.isSuccess) {
			snack.success("Campaign deleted successfully");
			queryClient.invalidateQueries({ queryKey: ["campaigns", workspace?.id] });
			navigate("/campaigns");
		}
		if (deleteMutation.isError) {
			snack.error(deleteMutation.error.message || "Failed to delete campaign");
		}
	}, [deleteMutation.isSuccess, deleteMutation.isError]);

	// Platform connection mutations
	const connectPlatformMutation = useMutation({
		mutationFn: ({ platform }) =>
			createFetcher({
				url: `${config.endpoints.connectPlatform}/${platform}`,
				method: "POST",
				auth: accessToken,
			})(),
		onSuccess: (_, { platform }) => {
			snack.success(`${platform} connected successfully`);
			queryClient.invalidateQueries({ queryKey: ["campaign", id] });
		},
		onError: (error) => {
			snack.error(error.message || "Failed to connect platform");
		},
	});

	// Campaign status toggle mutation
	const toggleStatusMutation = useMutation({
		mutationFn: createFetcher({
			url: `${config.endpoints.toggleCampaign}/${id}`,
			method: "POST",
			auth: accessToken,
		}),
		onSuccess: () => {
			snack.success("Campaign status updated successfully");
			queryClient.invalidateQueries({ queryKey: ["campaign", id] });
		},
		onError: (error) => {
			snack.error(error.message || "Failed to update campaign status");
		},
	});

	if (workspacePending || isPending) {
		return <PageLoader />;
	}

	if (isError) {
		return <ErrorView message="Failed to load campaign details" retryFunc={refetch} isPageWide />;
	}

	const handleDelete = () => {
		setShowDeleteConfirm(false);
		deleteMutation.mutate();
	};

	const handleToggleStatus = () => {
		toggleStatusMutation.mutate();
	};

	const handleConnectPlatform = (platform) => {
		connectPlatformMutation.mutate({ platform });
	};

	const handleDisconnectPlatform = (platform) => {
		// Implement the logic to disconnect a platform
		console.log(`Disconnecting platform: ${platform}`);
	};

	const tabs = [
		{ id: "overview", label: "Overview" },
		{ id: "analytics", label: "Analytics" },
		{ id: "settings", label: "Settings" },
		{ id: "platforms", label: "Platforms" },
	];

	return (
		<>
			<AuthenticatedHeader workspace={workspace} logOut={logOut} />
			<div className="min-h-screen bg-gradient-to-b from-[#0a0a0a] to-[#1a1a1a] pt-20 sm:pt-24">
				<div className="max-w-7xl mx-auto px-4 sm:px-6 py-8 sm:py-12">
					{/* Header */}
					<div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 sm:gap-6 mb-8">
						<div>
							<div className="flex items-center gap-3 text-white/60">
								<button
									onClick={() => navigate("/campaigns")}
									className="hover:text-white transition-colors flex items-center gap-1"
								>
									<span aria-hidden="true">←</span> Back
								</button>
								<span className="text-white/20">•</span>
								<span>{campaign.campaignType}</span>
							</div>
							<div className="mt-2">
								<h2 className="text-lg font-medium text-white/80">{campaign.projectName}</h2>
								<h1 className="mt-1 text-3xl sm:text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-[#007AFF] to-[#00C6FF]">
									{campaign.campaignName}
								</h1>
								<p className="mt-2 text-white/60">{campaign.projectInfo}</p>
							</div>
						</div>
						<div className="flex flex-col sm:flex-row gap-3">
							<motion.button
								whileHover={{ scale: 1.02 }}
								whileTap={{ scale: 0.98 }}
								onClick={() => setIsEditing(true)}
								className="flex items-center justify-center gap-2 px-4 py-2 rounded-xl bg-white/10 text-white hover:bg-white/20 transition-colors"
							>
								<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path
										strokeLinecap="round"
										strokeLinejoin="round"
										strokeWidth={2}
										d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
									/>
								</svg>
								Edit
							</motion.button>
							<motion.button
								whileHover={{ scale: 1.02 }}
								whileTap={{ scale: 0.98 }}
								onClick={() => setShowDeleteConfirm(true)}
								className="flex items-center justify-center gap-2 px-4 py-2 rounded-xl bg-red-500/10 text-red-500 hover:bg-red-500/20 transition-colors"
							>
								<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path
										strokeLinecap="round"
										strokeLinejoin="round"
										strokeWidth={2}
										d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
									/>
								</svg>
								Delete
							</motion.button>
						</div>
					</div>

					{/* Campaign Status Toggle */}
					<div className="bg-white/5 rounded-xl p-4 sm:p-6 mb-8">
						<div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
							<div>
								<h3 className="text-lg font-medium text-white">Campaign Status</h3>
								<p className="mt-1 text-sm text-white/60">
									{campaign.status === "RUNNING"
										? "Your campaign is currently active and running"
										: "Your campaign is currently paused"}
								</p>
							</div>
							<div className="flex items-center gap-3">
								<span
									className={`px-3 py-1 text-sm rounded-full ${
										campaign.status === "RUNNING"
											? "bg-green-500/10 text-green-500"
											: "bg-yellow-500/10 text-yellow-500"
									}`}
								>
									{campaign.status}
								</span>
								<button
									onClick={handleToggleStatus}
									className={`px-4 py-2 rounded-xl text-sm font-medium transition-colors ${
										campaign.status === "RUNNING"
											? "bg-yellow-500/10 text-yellow-500 hover:bg-yellow-500/20"
											: "bg-green-500/10 text-green-500 hover:bg-green-500/20"
									}`}
								>
									{campaign.status === "RUNNING" ? "Pause Campaign" : "Activate Campaign"}
								</button>
							</div>
						</div>
					</div>

					{/* Status Bar */}
					<div className="bg-white/5 rounded-xl p-4 sm:p-6 mb-8">
						<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
							<div>
								<div className="text-sm text-white/40">Timeline</div>
								<div className="mt-1 text-lg font-medium text-white">{campaign.campaignTimeline}</div>
							</div>
							<div>
								<div className="text-sm text-white/40">Style</div>
								<div className="mt-1 text-lg font-medium text-white">{campaign.engagementStyle}</div>
							</div>
							<div>
								<div className="text-sm text-white/40">Created</div>
								<div className="mt-1 text-lg font-medium text-white">
									{new Date(campaign.createdAt).toLocaleDateString()}
								</div>
							</div>
						</div>
					</div>

					{/* Tabs */}
					<div className="border-b border-white/10 mb-8">
						<nav className="flex gap-6 -mb-px overflow-x-auto">
							{tabs.map((tab) => (
								<button
									key={tab.id}
									onClick={() => setActiveTab(tab.id)}
									className={`py-4 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
										activeTab === tab.id
											? "border-[#007AFF] text-[#007AFF]"
											: "border-transparent text-white/60 hover:text-white/80 hover:border-white/20"
									}`}
								>
									{tab.label}
								</button>
							))}
						</nav>
					</div>

					{/* Tab Content */}
					<div className="space-y-8">
						{activeTab === "overview" && (
							<div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
								{/* Main Content */}
								<div className="lg:col-span-2 space-y-8">
									{/* Project Details */}
									<div className="bg-white/5 rounded-xl p-6">
										<h3 className="text-lg font-medium text-white mb-4">Project Details</h3>
										<div className="space-y-4">
											<div>
												<div className="text-sm text-white/40">Project Name</div>
												<div className="mt-1 text-white">{campaign.projectName}</div>
											</div>

											{campaign.projectWebsite && (
												<div>
													<div className="text-sm text-white/40">Website</div>
													<div className="mt-1">
														<a
															href={campaign.website}
															target="_blank"
															rel="noopener noreferrer"
															className="text-[#007AFF] hover:text-[#00C6FF] transition-colors"
														>
															{campaign.website}
														</a>
													</div>
												</div>
											)}

											<div>
												<div className="text-sm text-white/40">Description</div>
												<div className="mt-1 text-white whitespace-pre-wrap">{campaign.projectInfo}</div>
											</div>
										</div>
									</div>

									{/* Campaign Activity */}
									<div className="bg-white/5 rounded-xl p-6">
										<h3 className="text-lg font-medium text-white mb-4">Recent Activity</h3>
										<div className="space-y-4">
											{!campaign.activities?.length && (
												<div className="mt-2 text-sm text-white/60">No activities yet</div>
											)}
											{campaign.activities?.map((activity) => (
												<div key={activity.id} className="flex items-start gap-4 p-4 bg-white/5 rounded-xl">
													<div className="flex-shrink-0">
														<div className="w-8 h-8 rounded-full bg-[#007AFF]/10 flex items-center justify-center">
															<svg
																className="w-4 h-4 text-[#007AFF]"
																fill="none"
																viewBox="0 0 24 24"
																stroke="currentColor"
															>
																<path
																	strokeLinecap="round"
																	strokeLinejoin="round"
																	strokeWidth={2}
																	d="M13 10V3L4 14h7v7l9-11h-7z"
																/>
															</svg>
														</div>
													</div>
													<div>
														<div className="font-medium text-white">{activity.type}</div>
														<div className="mt-1 text-sm text-white/60">{activity.description}</div>
														<div className="mt-2 text-xs text-white/40">
															{new Date(activity.timestamp).toLocaleString()}
														</div>
													</div>
												</div>
											))}
										</div>
									</div>
								</div>

								{/* Sidebar */}
								<div className="space-y-8">
									{/* Target Platforms */}
									<div className="bg-white/5 rounded-xl p-6">
										<h3 className="text-lg font-medium text-white mb-4">Target Platforms</h3>
										<div className="space-y-4">
											{campaign.targetPlatforms.map((platform, index) => (
												<div key={index} className="flex items-center justify-between">
													<div className="flex items-center gap-3">
														<div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center">
															{platform === "Twitter" ? (
																<svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
																	<path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
																</svg>
															) : platform === "Telegram" ? (
																<svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
																	<path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69a.2.2 0 00-.05-.18c-.06-.05-.14-.03-.21-.02-.09.02-1.49.95-4.22 2.79-.4.27-.76.41-1.08.4-.36-.01-1.04-.2-1.55-.37-.63-.2-1.12-.31-1.08-.66.02-.18.27-.36.74-.55 2.92-1.27 4.86-2.11 5.83-2.51 2.78-1.16 3.35-1.36 3.73-1.36.08 0 .27.02.39.12.1.08.13.19.14.27-.01.06.01.24 0 .24z" />
																</svg>
															) : platform === "Discord" ? (
																<svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
																	<path d="M20.317 4.492c-1.53-.69-3.17-1.2-4.885-1.49a.075.075 0 00-.079.036c-.21.369-.444.85-.608 1.23a18.566 18.566 0 00-5.487 0 12.36 12.36 0 00-.617-1.23A.077.077 0 008.562 3c-1.714.29-3.354.8-4.885 1.491a.07.07 0 00-.032.027C.533 9.093-.32 13.555.099 17.961a.08.08 0 00.031.055 20.03 20.03 0 005.993 2.98.078.078 0 00.084-.026 13.83 13.83 0 001.226-1.963.074.074 0 00-.041-.104 13.201 13.201 0 01-1.872-.878.075.075 0 01-.008-.125c.126-.093.252-.19.372-.287a.075.075 0 01.078-.01c3.927 1.764 8.18 1.764 12.061 0a.075.075 0 01.079.009c.12.098.245.195.372.288a.075.075 0 01-.006.125c-.598.344-1.22.635-1.873.877a.075.075 0 00-.041.105c.36.687.772 1.341 1.225 1.962a.077.077 0 00.084.028 19.963 19.963 0 006.002-2.981.076.076 0 00.032-.054c.5-5.094-.838-9.52-3.549-13.442a.06.06 0 00-.031-.028zM8.02 15.278c-1.182 0-2.157-1.069-2.157-2.38 0-1.312.956-2.38 2.157-2.38 1.21 0 2.176 1.077 2.157 2.38 0 1.312-.956 2.38-2.157 2.38zm7.975 0c-1.183 0-2.157-1.069-2.157-2.38 0-1.312.955-2.38 2.157-2.38 1.21 0 2.176 1.077 2.157 2.38 0 1.312-.946 2.38-2.157 2.38z" />
																</svg>
															) : null}
														</div>
														<div className="text-white">{platform}</div>
													</div>
													{campaign.connectedPlatforms?.includes(platform) ? (
														<div className="text-green-500 text-sm">Connected</div>
													) : (
														<button
															onClick={() => handleConnectPlatform(platform.id)}
															className="text-sm text-[#007AFF] hover:text-[#00C6FF] transition-colors"
														>
															Connect
														</button>
													)}
												</div>
											))}
										</div>
									</div>

									{/* Campaign Settings */}
									<div className="bg-white/5 rounded-xl p-6">
										<h3 className="text-lg font-medium text-white mb-4">Campaign Settings</h3>
										<div className="space-y-4">
											<div>
												<div className="text-sm text-white/40">Target Audience</div>
												<div className="mt-1 text-white">{campaign.targetAudience.join(", ")}</div>
											</div>
											<div>
												<div className="text-sm text-white/40">Goals</div>
												<div className="mt-1 text-white">{campaign.campaignGoals.join(", ")}</div>
											</div>
											<div>
												<div className="text-sm text-white/40">Start Date</div>
												<div className="mt-1 text-white">
													{new Date(campaign.campaignStartDate).toLocaleDateString()}
												</div>
											</div>
										</div>
									</div>
								</div>
							</div>
						)}

						{activeTab === "analytics" && (
							<div className="bg-white/5 rounded-xl p-6">
								<h3 className="text-lg font-medium text-white mb-6">Campaign Analytics</h3>

								<div className="bg-white/5 rounded-xl p-4">
									<div className="mt-2 text-2xl font-semibold text-white">Coming Soon</div>
								</div>
								{/* <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
									{[
										{ label: "Total Engagements", value: "12.5K" },
										{ label: "Engagement Rate", value: "4.8%" },
										{ label: "Impressions", value: "256.8K" },
										{ label: "Conversion Rate", value: "2.3%" },
									].map((stat) => (
										<div key={stat.label} className="bg-white/5 rounded-xl p-4">
											<div className="text-sm text-white/40">{stat.label}</div>
											<div className="mt-2 text-2xl font-semibold text-white">{stat.value}</div>
										</div>
									))}
								</div> */}
								{/* Add charts and detailed analytics here */}
							</div>
						)}

						{activeTab === "settings" && (
							<div className="bg-white/5 rounded-xl p-6">
								<h3 className="text-lg font-medium text-white mb-6">Campaign Settings</h3>
								<div className="space-y-6">
									{/* Engagement Settings */}
									<div>
										<h4 className="text-white font-medium mb-4">Engagement Settings</h4>
										<div className="space-y-4">
											<div className="flex items-center justify-between p-4 bg-white/5 rounded-xl">
												<div>
													<div className="text-white">Meme Generation</div>
													<div className="text-sm text-white/60">
														Automatically generate and post trending crypto memes
													</div>
												</div>
												<label className="relative inline-flex items-center cursor-pointer">
													<input type="checkbox" className="sr-only peer" />
													<div className="w-11 h-6 bg-white/10 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#007AFF]"></div>
												</label>
											</div>
										</div>
									</div>

									{/* Safety Settings */}
									<div>
										<h4 className="text-white font-medium mb-4">Safety Settings</h4>
										<div className="space-y-4">
											<div className="flex items-center justify-between p-4 bg-white/5 rounded-xl">
												<div>
													<div className="text-white">Content Filtering</div>
													<div className="text-sm text-white/60">Filter out inappropriate or harmful content</div>
												</div>
												<label className="relative inline-flex items-center cursor-pointer">
													<input type="checkbox" className="sr-only peer" defaultChecked />
													<div className="w-11 h-6 bg-white/10 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#007AFF]"></div>
												</label>
											</div>
										</div>
									</div>
								</div>
							</div>
						)}

						{activeTab === "platforms" && (
							<div className="space-y-8">
								{/* Platform Authentication */}
								<div className="bg-white/5 rounded-xl p-6">
									<h3 className="text-lg font-medium text-white mb-6">Platform Authentication</h3>
									<div className="space-y-6">
										{[
											{
												id: "twitter",
												name: "Twitter",
												icon: "twitter",
												description: "Connect your Twitter account to enable automated posting and engagement",
											},
											{
												id: "telegram",
												name: "Telegram",
												icon: "telegram",
												description: "Link your Telegram groups or channels for community management",
											},
											{
												id: "discord",
												name: "Discord",
												icon: "discord",
												description: "Integrate with your Discord server for automated moderation and engagement",
											},
										].map((platform) => (
											<div
												key={platform.id}
												className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 bg-white/5 rounded-xl"
											>
												<div className="flex items-center gap-4">
													<div className="w-12 h-12 rounded-xl bg-white/10 flex items-center justify-center">
														{platform.icon === "twitter" ? (
															<svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
																<path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
															</svg>
														) : platform.icon === "telegram" ? (
															<svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
																<path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69a.2.2 0 00-.05-.18c-.06-.05-.14-.03-.21-.02-.09.02-1.49.95-4.22 2.79-.4.27-.76.41-1.08.4-.36-.01-1.04-.2-1.55-.37-.63-.2-1.12-.31-1.08-.66.02-.18.27-.36.74-.55 2.92-1.27 4.86-2.11 5.83-2.51 2.78-1.16 3.35-1.36 3.73-1.36.08 0 .27.02.39.12.1.08.13.19.14.27-.01.06.01.24 0 .24z" />
															</svg>
														) : (
															<svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
																<path d="M20.317 4.492c-1.53-.69-3.17-1.2-4.885-1.49a.075.075 0 00-.079.036c-.21.369-.444.85-.608 1.23a18.566 18.566 0 00-5.487 0 12.36 12.36 0 00-.617-1.23A.077.077 0 008.562 3c-1.714.29-3.354.8-4.885 1.491a.07.07 0 00-.032.027C.533 9.093-.32 13.555.099 17.961a.08.08 0 00.031.055 20.03 20.03 0 005.993 2.98.078.078 0 00.084-.026 13.83 13.83 0 001.226-1.963.074.074 0 00-.041-.104 13.201 13.201 0 01-1.872-.878.075.075 0 01-.008-.125c.126-.093.252-.19.372-.287a.075.075 0 01.078-.01c3.927 1.764 8.18 1.764 12.061 0a.075.075 0 01.079.009c.12.098.245.195.372.288a.075.075 0 01-.006.125c-.598.344-1.22.635-1.873.877a.075.075 0 00-.041.105c.36.687.772 1.341 1.225 1.962a.077.077 0 00.084.028 19.963 19.963 0 006.002-2.981.076.076 0 00.032-.054c.5-5.094-.838-9.52-3.549-13.442a.06.06 0 00-.031-.028zM8.02 15.278c-1.182 0-2.157-1.069-2.157-2.38 0-1.312.956-2.38 2.157-2.38 1.21 0 2.176 1.077 2.157 2.38 0 1.312-.956 2.38-2.157 2.38zm7.975 0c-1.183 0-2.157-1.069-2.157-2.38 0-1.312.955-2.38 2.157-2.38 1.21 0 2.176 1.077 2.157 2.38 0 1.312-.946 2.38-2.157 2.38z" />
															</svg>
														)}
													</div>
													<div>
														<h4 className="text-white font-medium">{platform.name}</h4>
														<p className="mt-1 text-sm text-white/60">{platform.description}</p>
													</div>
												</div>
												{campaign.connectedPlatforms?.includes(platform.id) ? (
													<div className="flex items-center gap-3">
														<div className="text-green-500 text-sm">Connected</div>
														<button
															onClick={() => handleDisconnectPlatform(platform.id)}
															className="px-4 py-2 rounded-xl text-sm font-medium bg-white/10 text-white hover:bg-white/20 transition-colors"
														>
															Disconnect
														</button>
													</div>
												) : (
													<button
														onClick={() => handleConnectPlatform(platform.id)}
														className="px-4 py-2 rounded-xl text-sm font-medium bg-[#007AFF] text-white hover:bg-[#0056b3] transition-colors"
													>
														Connect {platform.name}
													</button>
												)}
											</div>
										))}
									</div>
								</div>

								{/* Platform Settings */}
								{/* <div className="bg-white/5 rounded-xl p-6">
									<h3 className="text-lg font-medium text-white mb-6">Platform Settings</h3>
									<div className="space-y-6">
										{campaign.targetPlatforms?.map((platform) => (
											<div key={platform} className="space-y-4">
												<h4 className="text-white font-medium capitalize">{platform} Settings</h4>
												<div className="space-y-4">
													<div className="flex items-center justify-between p-4 bg-white/5 rounded-xl">
														<div>
															<div className="text-white">Auto-Reply to Messages</div>
															<div className="text-sm text-white/60">
																Automatically respond to direct messages using AI
															</div>
														</div>
														<label className="relative inline-flex items-center cursor-pointer">
															<input type="checkbox" className="sr-only peer" />
															<div className="w-11 h-6 bg-white/10 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#007AFF]"></div>
														</label>
													</div>
													<div className="flex items-center justify-between p-4 bg-white/5 rounded-xl">
														<div>
															<div className="text-white">Engagement Limits</div>
															<div className="text-sm text-white/60">
																Set maximum daily interactions to maintain natural behavior
															</div>
														</div>
														<input
															type="number"
															className="w-24 px-3 py-2 bg-white/10 rounded-lg text-white border-0 focus:ring-2 focus:ring-[#007AFF]"
															placeholder="500"
														/>
													</div>
												</div>
											</div>
										))}
									</div>
								</div> */}
							</div>
						)}
					</div>
				</div>

				<AnimatePresence>
					{isEditing && (
						<CampaignForm
							auth={accessToken}
							campaign={campaign}
							isEditing={isEditing}
							onCancel={() => setIsEditing(false)}
							onSuccess={() => {
								setIsEditing(false);
								refetch();
							}}
						/>
					)}
				</AnimatePresence>

				<ConfirmDialog
					isOpen={showDeleteConfirm}
					onClose={() => setShowDeleteConfirm(false)}
					onConfirm={handleDelete}
					title="Delete Campaign"
					message={`Are you sure you want to delete the campaign "${campaign.campaignName}"? This action cannot be undone.`}
				/>
			</div>
		</>
	);
};

export default CampaignDetails;
