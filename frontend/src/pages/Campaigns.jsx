import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useQuery } from "@tanstack/react-query";
import useSnack from "@/hooks/useSnack";
import CampaignForm from "@/components/campaigns/CampaignForm";
import AuthenticatedHeader from "@/components/common/AuthenticatedHeader";
import useWorkspace from "@/hooks/useWorkspace";
import { useLocation, useSearchParams } from "wouter";
import PageLoader from "@/components/common/PageLoader";
import { createFetcher } from "../libs/fetcher";
import config from "../libs/config";
import ErrorView from "../components/common/ErrorView";

const Campaigns = () => {
	const [isCreating, setIsCreating] = useState(false);
	const snack = useSnack();

	const [, navigate] = useLocation();
	const [searchParams] = useSearchParams();
	const newCampaign = searchParams.get("new");
	const { workspace, pending, logOut, accessToken } = useWorkspace();

	useEffect(() => {
		if (newCampaign && newCampaign === "1" && workspace) {
			setIsCreating(true);
		}
	}, [newCampaign, workspace]);

	useEffect(() => {
		if (pending) {
			return;
		}
		if (workspace) {
			// snack.success("Welcome to your workspace!");
		} else {
			snack.error("Access expired. Please log in again.");
			navigate("/login", { replace: true });
		}
	}, [pending, workspace]);

	const {
		data: campaigns,
		isPending,
		error,
		refetch,
		isError,
	} = useQuery({
		queryKey: ["campaigns", workspace?.id],
		queryFn: createFetcher({
			url: config.endpoints.getCampaigns,
			method: "GET",
			auth: accessToken,
		}),
		enabled: !!workspace,
	});

	useEffect(() => {
		if (error) {
			snack.error(error.message || "Failed to fetch campaigns");
		}
	}, [error, snack]);

	if (pending || isPending) {
		return <PageLoader />;
	}

	if (isError) {
		return <ErrorView message="Failed to fetch campaigns" retryFunc={refetch} isPageWide />;
	}

	if (!campaigns?.length) {
		return (
			<>
				<AuthenticatedHeader workspace={workspace} logOut={logOut} />
				<div className="min-h-screen bg-gradient-to-b from-[#0a0a0a] to-[#1a1a1a] flex flex-col justify-center pt-20">
					{/* Hero Section */}
					<div className="relative mx-auto max-w-7xl px-4 sm:px-6 py-12 sm:py-24 text-center">
						<motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="relative z-10">
							<h1 className="text-4xl sm:text-5xl md:text-7xl font-bold tracking-tight text-white bg-clip-text bg-gradient-to-r from-[#007AFF] to-[#00C6FF]">
								Launch Your Next
								<br />
								Crypto Campaign
							</h1>
							<p className="mt-4 sm:mt-6 text-base sm:text-lg leading-7 sm:leading-8 text-white/80 max-w-2xl mx-auto px-4">
								Leverage our advanced AI to automate your project's presence across crypto platforms. Our human-like
								engagement system ensures authentic interactions while maximizing your reach and impact.
							</p>
							<div className="mt-8 sm:mt-10 flex flex-col sm:flex-row items-center justify-center gap-4 sm:gap-x-6">
								<motion.button
									whileHover={{ scale: 1.05 }}
									whileTap={{ scale: 0.95 }}
									onClick={() => setIsCreating(true)}
									className="w-full sm:w-auto rounded-xl bg-gradient-to-r from-[#007AFF] to-[#00C6FF] px-6 sm:px-8 py-3 sm:py-4 text-base font-semibold text-white shadow-lg hover:shadow-[#007AFF]/20 hover:from-[#0056b3] hover:to-[#00A6FF] transition-all duration-300"
								>
									Create Campaign
								</motion.button>
								<motion.a
									whileHover={{ x: 5 }}
									href="#features"
									className="text-base font-semibold leading-6 text-white/80 hover:text-white transition-colors flex items-center gap-2"
								>
									Learn more <span aria-hidden="true">→</span>
								</motion.a>
							</div>
						</motion.div>

						{/* Animated Background */}
						<div className="absolute inset-0 -z-10 overflow-hidden">
							<div className="absolute inset-0 bg-[#007AFF]/5 backdrop-blur-3xl" />
							<div className="absolute top-0 left-1/2 -translate-x-1/2 w-[90vw] max-w-[800px] aspect-square bg-gradient-radial from-[#007AFF]/20 to-transparent rounded-full blur-3xl" />
						</div>
					</div>

					{/* Features Grid */}
					<div id="features" className="relative py-12 sm:py-24 bg-[#0a0a0a]/80">
						<div className="mx-auto max-w-7xl px-4 sm:px-6">
							<motion.div
								initial={{ opacity: 0 }}
								whileInView={{ opacity: 1 }}
								viewport={{ once: true }}
								className="grid grid-cols-1 gap-6 sm:gap-8 sm:grid-cols-2 lg:grid-cols-3"
							>
								{[
									{
										title: "AI-Powered Shilling",
										description:
											"Automated, human-like engagement across multiple platforms to boost your project's visibility",
										icon: (
											<svg className="h-6 w-6 sm:h-8 sm:w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
												<path
													strokeLinecap="round"
													strokeLinejoin="round"
													strokeWidth={2}
													d="M13 10V3L4 14h7v7l9-11h-7z"
												/>
											</svg>
										),
									},
									{
										title: "Multi-Platform Presence",
										description: "Seamless automated posting and engagement across X, Telegram, and Discord",
										icon: (
											<svg className="h-6 w-6 sm:h-8 sm:w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
												<path
													strokeLinecap="round"
													strokeLinejoin="round"
													strokeWidth={2}
													d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
												/>
											</svg>
										),
									},
									{
										title: "Human-Like Engagement",
										description:
											"Advanced AI ensures natural interactions that blend seamlessly with organic community activity",
										icon: (
											<svg className="h-6 w-6 sm:h-8 sm:w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
												<path
													strokeLinecap="round"
													strokeLinejoin="round"
													strokeWidth={2}
													d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
												/>
											</svg>
										),
									},
								].map((feature, index) => (
									<motion.div
										key={feature.title}
										initial={{ opacity: 0, y: 20 }}
										whileInView={{ opacity: 1, y: 0 }}
										viewport={{ once: true }}
										transition={{ delay: index * 0.2 }}
										className="group relative bg-gradient-to-b from-white/[0.08] to-transparent rounded-2xl p-6 sm:p-8 hover:from-white/[0.12] transition-all duration-300"
									>
										<div className="flex h-12 w-12 sm:h-16 sm:w-16 items-center justify-center rounded-xl bg-gradient-to-r from-[#007AFF]/10 to-[#00C6FF]/10 group-hover:from-[#007AFF]/20 group-hover:to-[#00C6FF]/20 transition-all duration-300">
											<div className="text-gradient bg-gradient-to-r from-[#007AFF] to-[#00C6FF]">{feature.icon}</div>
										</div>
										<h3 className="mt-4 sm:mt-6 text-lg sm:text-xl font-semibold text-white group-hover:text-[#007AFF] transition-colors">
											{feature.title}
										</h3>
										<p className="mt-2 text-sm sm:text-base text-white/60 group-hover:text-white/80 transition-colors">
											{feature.description}
										</p>
									</motion.div>
								))}
							</motion.div>
						</div>
					</div>

					<AnimatePresence>
						{isCreating && (
							<CampaignForm auth={accessToken} onCancel={() => setIsCreating(false)} workspaceId={workspace?.id} />
						)}
					</AnimatePresence>
				</div>
			</>
		);
	}

	return (
		<>
			<AuthenticatedHeader workspace={workspace} logOut={logOut} />
			<div className="min-h-screen bg-gradient-to-b from-[#0a0a0a] to-[#1a1a1a] pt-20 sm:pt-24">
				<div className="max-w-7xl mx-auto px-4 sm:px-6 py-8 sm:py-12">
					<div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4 sm:gap-0 mb-8 sm:mb-12">
						<div>
							<h1 className="text-3xl sm:text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-[#007AFF] to-[#00C6FF]">
								Your Campaigns
							</h1>
							<p className="mt-2 text-white/60">Manage and track your crypto marketing campaigns</p>
						</div>
						<motion.button
							whileHover={{ scale: 1.05 }}
							whileTap={{ scale: 0.95 }}
							onClick={() => setIsCreating(true)}
							className="w-full sm:w-auto rounded-xl bg-gradient-to-r from-[#007AFF] to-[#00C6FF] px-6 py-3 text-base font-semibold text-white shadow-lg hover:shadow-[#007AFF]/20 hover:from-[#0056b3] hover:to-[#00A6FF] transition-all duration-300"
						>
							Create Campaign
						</motion.button>
					</div>

					<div className="grid grid-cols-1 gap-4 sm:gap-6 md:grid-cols-2 lg:grid-cols-3">
						<AnimatePresence>
							{campaigns.map((campaign, index) => (
								<motion.div
									key={campaign.id}
									initial={{ opacity: 0, y: 20 }}
									animate={{ opacity: 1, y: 0 }}
									exit={{ opacity: 0, y: -20 }}
									transition={{ delay: index * 0.1 }}
									className="group relative bg-gradient-to-b from-white/[0.08] to-transparent rounded-2xl p-4 sm:p-6 hover:from-white/[0.12] transition-all duration-300"
								>
									<div className="absolute inset-0 bg-gradient-to-r from-[#007AFF]/0 to-[#00C6FF]/0 group-hover:from-[#007AFF]/5 group-hover:to-[#00C6FF]/5 rounded-2xl transition-all duration-300" />
									<div className="relative space-y-3 sm:space-y-4">
										{/* Header Section */}
										<div className="flex items-start justify-between gap-3">
											<div className="min-w-0 flex-1">
												<h3 className="text-lg sm:text-xl font-semibold text-white group-hover:text-[#007AFF] transition-colors truncate">
													{campaign.campaignName}
												</h3>
												<div className="mt-1 flex items-center gap-2 text-sm text-white/60">
													<span className="truncate">{campaign.projectName}</span>
													<span className="text-white/20 shrink-0">•</span>
													<span className="truncate">{campaign.campaignType}</span>
												</div>
											</div>
											<div
												className={`shrink-0 px-3 py-1 text-sm rounded-full ${
													campaign.status === "RUNNING"
														? "bg-green-500/10 text-green-500"
														: campaign.status === "PENDING"
														? "bg-yellow-500/10 text-yellow-500"
														: campaign.status === "COMPLETED"
														? "bg-[#007AFF]/10 text-[#007AFF]"
														: "bg-red-500/10 text-red-500"
												}`}
											>
												{campaign.status}
											</div>
										</div>

										{/* Info Section */}
										<p className="text-white/60 group-hover:text-white/80 transition-colors line-clamp-2 text-sm sm:text-base">
											{campaign.projectInfo}
										</p>

										{/* Stats Grid */}
										<div className="grid grid-cols-3 gap-2">
											<div className="bg-white/5 rounded-xl p-2 sm:p-3">
												<div className="text-xs text-white/40">Platforms</div>
												<div className="mt-1 flex items-center gap-1 sm:gap-2">
													{campaign.targetPlatforms.map((platform) => (
														<span key={platform} className="text-white/80">
															{platform === "Twitter" ? (
																<svg className="w-3 h-3 sm:w-4 sm:h-4" fill="currentColor" viewBox="0 0 24 24">
																	<path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
																</svg>
															) : platform === "Telegram" ? (
																<svg className="w-3 h-3 sm:w-4 sm:h-4" fill="currentColor" viewBox="0 0 24 24">
																	<path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69a.2.2 0 00-.05-.18c-.06-.05-.14-.03-.21-.02-.09.02-1.49.95-4.22 2.79-.4.27-.76.41-1.08.4-.36-.01-1.04-.2-1.55-.37-.63-.2-1.12-.31-1.08-.66.02-.18.27-.36.74-.55 2.92-1.27 4.86-2.11 5.83-2.51 2.78-1.16 3.35-1.36 3.73-1.36.08 0 .27.02.39.12.1.08.13.19.14.27-.01.06.01.24 0 .24z" />
																</svg>
															) : (
																<svg className="w-3 h-3 sm:w-4 sm:h-4" fill="currentColor" viewBox="0 0 24 24">
																	<path d="M20.317 4.492c-1.53-.69-3.17-1.2-4.885-1.49a.075.075 0 00-.079.036c-.21.369-.444.85-.608 1.23a18.566 18.566 0 00-5.487 0 12.36 12.36 0 00-.617-1.23A.077.077 0 008.562 3c-1.714.29-3.354.8-4.885 1.491a.07.07 0 00-.032.027C.533 9.093-.32 13.555.099 17.961a.08.08 0 00.031.055 20.03 20.03 0 005.993 2.98.078.078 0 00.084-.026 13.83 13.83 0 001.226-1.963.074.074 0 00-.041-.104 13.201 13.201 0 01-1.872-.878.075.075 0 01-.008-.125c.126-.093.252-.19.372-.287a.075.075 0 01.078-.01c3.927 1.764 8.18 1.764 12.061 0a.075.075 0 01.079.009c.12.098.245.195.372.288a.075.075 0 01-.006.125c-.598.344-1.22.635-1.873.877a.075.075 0 00-.041.105c.36.687.772 1.341 1.225 1.962a.077.077 0 00.084.028 19.963 19.963 0 006.002-2.981.076.076 0 00.032-.054c.5-5.094-.838-9.52-3.549-13.442a.06.06 0 00-.031-.028zM8.02 15.278c-1.182 0-2.157-1.069-2.157-2.38 0-1.312.956-2.38 2.157-2.38 1.21 0 2.176 1.077 2.157 2.38 0 1.312-.956 2.38-2.157 2.38zm7.975 0c-1.183 0-2.157-1.069-2.157-2.38 0-1.312.955-2.38 2.157-2.38 1.21 0 2.176 1.077 2.157 2.38 0 1.312-.946 2.38-2.157 2.38z" />
																</svg>
															)}
														</span>
													))}
												</div>
											</div>
											<div className="bg-white/5 rounded-xl p-2 sm:p-3">
												<div className="text-xs text-white/40">Timeline</div>
												<div className="mt-1 text-xs sm:text-sm text-white/80 truncate">
													{campaign.campaignTimeline}
												</div>
											</div>
											<div className="bg-white/5 rounded-xl p-2 sm:p-3">
												<div className="text-xs text-white/40">Style</div>
												<div className="mt-1 text-xs sm:text-sm text-white/80 truncate">{campaign.engagementStyle}</div>
											</div>
										</div>

										{/* Action Section */}
										<div className="pt-2 flex items-center justify-end">
											<button
												onClick={() => navigate(`/campaigns/${campaign.id}`)}
												className="group/btn text-[#007AFF] hover:text-[#00C6FF] transition-colors flex items-center gap-2 text-sm sm:text-base"
											>
												View Details
												<span aria-hidden="true" className="transition-transform group-hover/btn:translate-x-0.5">
													→
												</span>
											</button>
										</div>
									</div>
								</motion.div>
							))}
						</AnimatePresence>
					</div>
				</div>
				<AnimatePresence>
					{isCreating && (
						<CampaignForm auth={accessToken} onCancel={() => setIsCreating(false)} workspaceId={workspace?.id} />
					)}
				</AnimatePresence>
			</div>
		</>
	);
};

export default Campaigns;
