import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import useSnack from "@/hooks/useSnack";
import useWorkspace from "@/hooks/useWorkspace";
import { useLocation, useParams } from "wouter";
import PageLoader from "@/components/common/PageLoader";
import ErrorView from "@/components/common/ErrorView";
import ConfirmDialog from "@/components/common/ConfirmDialog";
import { createFetcher } from "@/libs/fetcher";
import config from "../libs/config";
import CampaignForm from "@/components/campaigns/CampaignForm";
import AuthenticatedHeader from "@/components/common/AuthenticatedHeader";
import ProjectInfoForm from "../components/campaign/ProjectInfoForm";
import CampaignHeader from "@/components/campaigns/CampaignHeader";
import CampaignStatus from "@/components/campaigns/CampaignStatus";
import CampaignTabs from "@/components/campaigns/CampaignTabs";
import CampaignOverview from "@/components/campaigns/CampaignOverview";
import CampaignAnalytics from "@/components/campaigns/CampaignAnalytics";
import CampaignSettings from "@/components/campaigns/CampaignSettings";
import CampaignPlatforms from "@/components/campaigns/CampaignPlatforms";

const PlatformConnectDialog = ({ isOpen, onClose, onConfirm, platform }) => {
	const platformInfo = {
		twitter: {
			permissions: [
				"Read your tweets",
				"Post tweets on your behalf",
				"Follow and unfollow accounts",
				"Like and retweet",
			],
			icon: (
				<svg className="w-6 h-6 text-[#1DA1F2]" fill="currentColor" viewBox="0 0 24 24">
					<path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
				</svg>
			),
		},
		telegram: {
			permissions: ["Access your groups", "Send messages", "Manage community", "Read messages"],
			icon: (
				<svg className="w-6 h-6 text-[#0088cc]" fill="currentColor" viewBox="0 0 24 24">
					<path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69a.2.2 0 00-.05-.18c-.06-.05-.14-.03-.21-.02-.09.02-1.49.95-4.22 2.79-.4.27-.76.41-1.08.4-.36-.01-1.04-.2-1.55-.37-.63-.2-1.12-.31-1.08-.66.02-.18.27-.36.74-.55 2.92-1.27 4.86-2.11 5.83-2.51 2.78-1.16 3.35-1.36 3.73-1.36.08 0 .27.02.39.12.1.08.13.19.14.27-.01.06.01.24 0 .24z" />
				</svg>
			),
		},
		discord: {
			permissions: ["Access your servers", "Send messages", "Manage roles", "Read messages"],
			icon: (
				<svg className="w-6 h-6 text-[#7289DA]" fill="currentColor" viewBox="0 0 24 24">
					<path d="M20.317 4.492c-1.53-.69-3.17-1.2-4.885-1.49a.075.075 0 00-.079.036c-.21.369-.444.85-.608 1.23a18.566 18.566 0 00-5.487 0 12.36 12.36 0 00-.617-1.23A.077.077 0 008.562 3c-1.714.29-3.354.8-4.885 1.491a.07.07 0 00-.032.027C.533 9.093-.32 13.555.099 17.961a.08.08 0 00.031.055 20.03 20.03 0 005.993 2.98.078.078 0 00.084-.026 13.83 13.83 0 001.226-1.963.074.074 0 00-.041-.104 13.201 13.201 0 01-1.872-.878.075.075 0 01-.008-.125c.126-.093.252-.19.372-.287a.075.075 0 01.078-.01c3.927 1.764 8.18 1.764 12.061 0a.075.075 0 01.079.009c.12.098.245.195.372.288a.075.075 0 01-.006.125c-.598.344-1.22.635-1.873.877a.075.075 0 00-.041.105c.36.687.772 1.341 1.225 1.962a.077.077 0 00.084.028 19.963 19.963 0 006.002-2.981.076.076 0 00.032-.054c.5-5.094-.838-9.52-3.549-13.442a.06.06 0 00-.031-.028z" />
				</svg>
			),
		},
	};

	return (
		<AnimatePresence>
			{isOpen && (
				<div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
					<motion.div
						initial={{ opacity: 0, scale: 0.95 }}
						animate={{ opacity: 1, scale: 1 }}
						exit={{ opacity: 0, scale: 0.95 }}
						transition={{ duration: 0.2 }}
						className="relative w-full max-w-lg bg-[#1a1a1a] rounded-2xl shadow-xl overflow-hidden"
					>
						<div className="p-4 sm:p-6">
							{/* Header */}
							<div className="flex items-start sm:items-center gap-4 mb-6">
								<div className="w-10 h-10 sm:w-12 sm:h-12 rounded-full bg-white/5 flex items-center justify-center flex-shrink-0">
									{platformInfo[platform.toLowerCase()]?.icon}
								</div>
								<div className="min-w-0 flex-1">
									<h3 className="text-lg sm:text-xl font-semibold text-white truncate">Connect to {platform}</h3>
									<p className="text-sm text-white/60 mt-0.5">
										You'll be redirected to {platform} to complete the connection
									</p>
								</div>
							</div>

							{/* Content */}
							<div className="space-y-4 sm:space-y-6">
								<div>
									<h4 className="text-sm font-medium text-white/80 mb-3">Required Permissions</h4>
									<div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
										{platformInfo[platform.toLowerCase()]?.permissions.map((permission, index) => (
											<div key={index} className="flex items-center gap-2 text-white/60 text-sm">
												<svg
													className="w-4 h-4 text-[#007AFF] flex-shrink-0"
													fill="none"
													viewBox="0 0 24 24"
													stroke="currentColor"
												>
													<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
												</svg>
												<span className="truncate">{permission}</span>
											</div>
										))}
									</div>
								</div>

								<div className="bg-[#007AFF]/10 border border-[#007AFF]/20 rounded-xl p-3 sm:p-4">
									<div className="flex gap-3">
										<div className="flex-shrink-0">
											<svg className="w-5 h-5 text-[#007AFF]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
												<path
													strokeLinecap="round"
													strokeLinejoin="round"
													strokeWidth={2}
													d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
												/>
											</svg>
										</div>
										<div className="flex-1 min-w-0">
											<p className="text-sm text-[#007AFF]">
												Your data is secure with us. We follow strict security protocols and only request permissions
												that are necessary for the campaign's functionality.
											</p>
										</div>
									</div>
								</div>
							</div>

							{/* Actions */}
							<div className="flex flex-col-reverse sm:flex-row gap-2 sm:gap-3 mt-6 sm:mt-8">
								<button
									onClick={onClose}
									className="flex-1 px-4 py-2.5 rounded-xl text-sm font-medium text-white bg-white/10 hover:bg-white/20 transition-colors"
								>
									Cancel
								</button>
								<button
									onClick={onConfirm}
									className="flex-1 px-4 py-2.5 rounded-xl text-sm font-medium text-white bg-[#007AFF] hover:bg-[#0056b3] transition-colors"
								>
									Connect {platform}
								</button>
							</div>
						</div>
					</motion.div>
				</div>
			)}
		</AnimatePresence>
	);
};

const CampaignDetails = () => {
	const { id } = useParams();
	const [, navigate] = useLocation();
	const snack = useSnack();
	const queryClient = useQueryClient();
	const [isEditing, setIsEditing] = useState(false);
	const [activeTab, setActiveTab] = useState("overview");
	const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
	const [connectingPlatform, setConnectingPlatform] = useState(null);

	const { workspace, pending: workspacePending, logOut, accessToken } = useWorkspace();

	// Fetch campaign details
	const {
		data: campaign,
		isPending,
		refetch,
		isError,
	} = useQuery({
		queryKey: ["campaign", parseInt(id)],
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
		setConnectingPlatform(platform);
	};

	const handleConfirmConnect = () => {
		if (connectingPlatform) {
			connectPlatformMutation.mutate({ platform: connectingPlatform });
			setConnectingPlatform(null);
		}
	};

	const handleDisconnectPlatform = (platform) => {
		// Implement the logic to disconnect a platform
		console.log(`Disconnecting platform: ${platform}`);
	};

	return (
		<>
			<AuthenticatedHeader workspace={workspace} logOut={logOut} />
			<div className="min-h-screen bg-gradient-to-b from-[#0a0a0a] to-[#1a1a1a] pt-20 sm:pt-24">
				<div className="max-w-7xl mx-auto px-4 sm:px-6 py-8 sm:py-12">
					<CampaignHeader
						campaign={campaign}
						navigate={navigate}
						setIsEditing={setIsEditing}
						setShowDeleteConfirm={setShowDeleteConfirm}
					/>

					<CampaignStatus campaign={campaign} handleToggleStatus={handleToggleStatus} setActiveTab={setActiveTab} />

					<CampaignTabs activeTab={activeTab} setActiveTab={setActiveTab} />

					{/* Tab Content */}
					<div className="space-y-8">
						{activeTab === "overview" && <CampaignOverview campaign={campaign} />}

						{activeTab === "project-info" && (
							<div data-tab-content="project-info" className="w-full">
								<div className="bg-[#1a1a1a]/50 backdrop-blur-xl rounded-xl p-4 sm:p-6">
									<div className="mb-6">
										<div className="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
											<div>
												<h2 className="text-xl font-semibold text-white mb-2">Project Information</h2>
												<p className="text-gray-400 text-sm">
													Provide detailed information about your project to help us better understand and promote it.
												</p>
											</div>
											<div className="bg-[#007AFF]/10 border border-[#007AFF]/20 rounded-lg p-3 lg:max-w-md flex items-start gap-3">
												<svg
													className="w-5 h-5 text-[#007AFF] flex-shrink-0 mt-0.5"
													fill="none"
													viewBox="0 0 24 24"
													stroke="currentColor"
												>
													<path
														strokeLinecap="round"
														strokeLinejoin="round"
														strokeWidth={2}
														d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
													/>
												</svg>
												<p className="text-sm text-[#007AFF]">
													Complete your project information to help us better promote your campaign. The more details
													you provide, the better we can tailor our services.
												</p>
											</div>
										</div>
									</div>

									<ProjectInfoForm initialData={campaign} auth={accessToken} />
								</div>
							</div>
						)}

						{activeTab === "analytics" && <CampaignAnalytics campaign={campaign} />}

						{activeTab === "settings" && <CampaignSettings campaign={campaign} auth={accessToken} />}

						{activeTab === "platforms" && (
							<CampaignPlatforms
								campaign={campaign}
								handleConnectPlatform={handleConnectPlatform}
								handleDisconnectPlatform={handleDisconnectPlatform}
							/>
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

				<PlatformConnectDialog
					isOpen={!!connectingPlatform}
					onClose={() => setConnectingPlatform(null)}
					onConfirm={handleConfirmConnect}
					platform={connectingPlatform}
				/>
			</div>
		</>
	);
};

export default CampaignDetails;
