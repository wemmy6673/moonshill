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
import PlatformConnectDialog from "../components/campaign/PlatformConnectDialog";

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

	useEffect(() => {
		if (workspacePending) {
			return;
		}
		if (workspace) {
			// snack.success("Welcome to your workspace!");
		} else {
			snack.error("Access expired. Please log in again.");
			navigate("/login", { replace: true });
		}
	}, [workspacePending, workspace]);

	// Fetch campaign details
	const {
		data: campaign,
		isPending,
		refetch,
		isError,
		isSuccess,
	} = useQuery({
		queryKey: ["campaign", parseInt(id)],
		queryFn: createFetcher({
			url: `${config.endpoints.getCampaign}/${id}`,
			method: "GET",
			auth: accessToken,
		}),
		enabled: !!id && !!workspace,
	});

	const { data: platformConnectionStatus } = useQuery({
		queryKey: ["campaign-connection-status", parseInt(id)],
		queryFn: createFetcher({
			url: `${config.endpoints.getCampaignConnectionStatus}/${id}`,
			method: "GET",
			auth: accessToken,
		}),
		refetchInterval: 15000,
		enabled: isSuccess,
	});

	// Disconnect platform connection
	const disconnectPlatformMutation = useMutation({
		mutationFn: createFetcher({
			url: `${config.endpoints.disconnectPlatform}/${id}`,
			method: "POST",
			auth: accessToken,
		}),
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

	// Campaign status toggle mutation

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

	const handleConnectPlatform = (platform) => {
		setConnectingPlatform(platform);
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

					<CampaignStatus
						campaign={campaign}
						setActiveTab={setActiveTab}
						platformConnectionStatus={platformConnectionStatus}
						auth={accessToken}
					/>

					<CampaignTabs activeTab={activeTab} setActiveTab={setActiveTab} />

					{/* Tab Content */}
					<div className="space-y-8">
						{activeTab === "overview" && (
							<CampaignOverview campaign={campaign} platformConnectionStatus={platformConnectionStatus} />
						)}

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

						{activeTab === "settings" && <CampaignSettings campaign={campaign} auth={accessToken} />}
						{activeTab === "analytics" && <CampaignAnalytics campaign={campaign} />}

						{activeTab === "platforms" && (
							<CampaignPlatforms
								campaign={campaign}
								handleConnectPlatform={handleConnectPlatform}
								platformConnectionStatus={platformConnectionStatus}
								disconnectPlatformMutation={disconnectPlatformMutation}
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
					platform={connectingPlatform}
					auth={accessToken}
					campaignId={campaign?.id}
				/>
			</div>
		</>
	);
};

export default CampaignDetails;
