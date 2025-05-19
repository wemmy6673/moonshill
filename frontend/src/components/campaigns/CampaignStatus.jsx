import { motion } from "framer-motion";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createFetcher } from "../../libs/fetcher";
import config from "../../libs/config";
import useSnack from "../../hooks/useSnack";
import { useEffect, useState } from "react";
import ConfirmDialog from "../common/ConfirmDialog";

const CampaignStatus = ({ campaign, setActiveTab, platformConnectionStatus, auth }) => {
	const [isConfirmDialogOpen, setIsConfirmDialogOpen] = useState(false);

	const snack = useSnack();
	const queryClient = useQueryClient();
	const {
		mutate: togglePublish,
		isPending: isTogglingPublish,
		isError: isTogglingPublishError,
		error: togglingPublishError,
		isSuccess: isTogglingPublishSuccess,
		reset: resetTogglingPublish,
	} = useMutation({
		mutationFn: createFetcher({
			url: `${config.endpoints.togglePublish}/${campaign.id}`,
			method: "GET",
			auth,
		}),
	});

	useEffect(() => {
		if (isTogglingPublishSuccess) {
			snack.success("Campaign updated");
			queryClient.invalidateQueries({ queryKey: ["campaigns"] });
			queryClient.invalidateQueries({ queryKey: ["campaign", campaign.id] });
			queryClient.invalidateQueries({ queryKey: ["campaign-settings", campaign.id] });
			queryClient.invalidateQueries({ queryKey: ["campaign-connection-status", campaign.id] });
		}
		if (isTogglingPublishError) {
			snack.error(togglingPublishError.message || "Failed to update campaign status");
			resetTogglingPublish();
		}
	}, [isTogglingPublishSuccess, isTogglingPublishError, togglingPublishError]);

	const handleTogglePublish = () => {
		setIsConfirmDialogOpen(false);
		if (campaign && campaign.completionPercentage < 70) {
			snack.info("You need to complete at least 70% of the campaign information to publish it.");
			return;
		}

		if (campaign && Object.entries(platformConnectionStatus).filter(([_, value]) => value.isConnected).length < 1) {
			snack.info("You need to connect at least one platform to publish the campaign.");
			return;
		}
		togglePublish();
	};

	return (
		<div className="bg-white/5 rounded-xl p-4 sm:p-6 mb-8">
			<div className="flex flex-col gap-6">
				{/* Status Section */}
				<div className="flex items-center gap-4 p-4 bg-white/5 rounded-xl">
					<div className="flex items-center gap-3">
						<div
							className={`w-3 h-3 rounded-full ${
								campaign.status === "RUNNING"
									? "bg-green-500 shadow-lg shadow-green-500/30"
									: "bg-yellow-500 shadow-lg shadow-yellow-500/30"
							}`}
						></div>
						<div>
							<div className="text-sm font-medium text-white/80">Status</div>
							<div className="text-lg font-semibold text-white">
								{campaign.status === "RUNNING" ? "Campaign Active" : "Campaign Paused"}
							</div>
						</div>
					</div>

					<motion.button
						disabled={isTogglingPublish}
						whileHover={{ scale: 1.02 }}
						whileTap={{ scale: 0.98 }}
						onClick={() => setIsConfirmDialogOpen(true)}
						className={`ml-auto px-6 h-11 rounded-xl text-sm font-medium transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed ${
							campaign.status === "RUNNING"
								? "bg-gradient-to-r from-red-500/80 to-red-600/80 text-white hover:from-red-500 hover:to-red-600"
								: "bg-gradient-to-r from-orange-500/80 to-amber-500/80 text-white hover:from-orange-500 hover:to-amber-500"
						}`}
					>
						{isTogglingPublish && (
							<svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
								<circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
								<path
									className="opacity-75"
									fill="currentColor"
									d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
								></path>
							</svg>
						)}
						{campaign.status === "RUNNING" ? (
							<>
								{!isTogglingPublish && (
									<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
										<path
											strokeLinecap="round"
											strokeLinejoin="round"
											strokeWidth={2}
											d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z"
										/>
									</svg>
								)}
								<span>Pause Campaign</span>
							</>
						) : (
							<>
								{!isTogglingPublish && (
									<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
										<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
									</svg>
								)}
								<span>Publish Campaign</span>
							</>
						)}
					</motion.button>

					<ConfirmDialog
						isOpen={isConfirmDialogOpen}
						onClose={() => setIsConfirmDialogOpen(false)}
						onConfirm={handleTogglePublish}
						title={campaign.status === "RUNNING" ? "Pause Campaign" : "Publish Campaign"}
						message={
							campaign.status === "RUNNING"
								? "Are you sure you want to pause the campaign? This will stop the campaign from running and MoonShill will not post to your platforms."
								: "Are you sure you want to publish the campaign? This will start the campaign and activate MoonShill to post to your platforms."
						}
					/>
				</div>

				{/* Action Buttons */}
				<div className="flex flex-col sm:flex-row gap-3">
					<button
						onClick={() => {
							setActiveTab("project-info");
							document.querySelector('[data-tab="project-info"]')?.scrollIntoView({
								behavior: "smooth",
								block: "start",
							});
						}}
						disabled={campaign.completionPercentage === 100}
						className={`flex items-center justify-center gap-2 h-11 px-6 rounded-xl text-white transition-all sm:flex-1 ${
							campaign.completionPercentage === 100
								? "bg-green-500/20 cursor-not-allowed"
								: "bg-[#007AFF] hover:opacity-90"
						}`}
					>
						<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path
								strokeLinecap="round"
								strokeLinejoin="round"
								strokeWidth={2}
								d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
							/>
						</svg>
						{campaign.completionPercentage === 100 ? (
							"Project Info Complete"
						) : (
							<>
								Complete Project Info
								<span className="ml-1 px-1.5 py-0.5 text-xs bg-white/10 rounded">{campaign.completionPercentage}%</span>
							</>
						)}
					</button>
					<button
						onClick={() => {
							setActiveTab("platforms");
							document.querySelector('[data-tab="platforms"]')?.scrollIntoView({
								behavior: "smooth",
								block: "start",
							});
						}}
						className="flex items-center justify-center gap-2 h-11 px-6 rounded-xl border border-white/10 bg-white/5 text-white hover:bg-white/10 transition-all sm:flex-1"
					>
						<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path
								strokeLinecap="round"
								strokeLinejoin="round"
								strokeWidth={2}
								d="M8 11h4m4 0h-4m0 0V7m0 4v4M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
							/>
						</svg>
						Connect Platforms{" "}
						<span className="text-xs bg-white/10 px-1.5 py-0.5 rounded">
							{platformConnectionStatus &&
								Object.entries(platformConnectionStatus).filter(([, value]) => value.isConnected).length}
							/ {platformConnectionStatus && Object.keys(platformConnectionStatus).length}
						</span>
					</button>
				</div>
			</div>
		</div>
	);
};

export default CampaignStatus;
