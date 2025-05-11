import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import useSnack from "@/hooks/useSnack";
import { getStorage } from "@/lib/browserutils";
import CampaignForm from "@/components/campaigns/CampaignForm";
import Loader from "@/components/common/Loader";
import AuthenticatedHeader from "@/components/common/AuthenticatedHeader";

const Campaigns = () => {
	const [isCreating, setIsCreating] = useState(false);
	const { showSnack } = useSnack();
	const queryClient = useQueryClient();
	const walletAddress = getStorage("walletAddress");

	const {
		data: campaigns,
		isPending,
		error,
	} = useQuery({
		queryKey: ["campaigns", walletAddress],
		queryFn: async () => {
			// TODO: Replace with actual API call
			return [];
		},
		enabled: !!walletAddress,
	});

	const createCampaignMutation = useMutation({
		mutationFn: async (campaignData) => {
			// TODO: Replace with actual API call
			return { id: Date.now(), ...campaignData, status: "draft" };
		},
		onSuccess: () => {
			queryClient.invalidateQueries(["campaigns", walletAddress]);
			showSnack("Campaign created successfully", "success");
			setIsCreating(false);
		},
		onError: (error) => {
			showSnack(error.message || "Failed to create campaign", "error");
		},
	});

	useEffect(() => {
		if (error) {
			showSnack(error.message || "Failed to fetch campaigns", "error");
		}
	}, [error, showSnack]);

	const handleCreateCampaign = async (values) => {
		await createCampaignMutation.mutateAsync(values);
	};

	if (!campaigns?.length) {
		return (
			<>
				<AuthenticatedHeader />
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
						{isCreating && <CampaignForm onSubmit={handleCreateCampaign} onCancel={() => setIsCreating(false)} />}
					</AnimatePresence>
				</div>
			</>
		);
	}

	return (
		<>
			<AuthenticatedHeader />
			<div className="min-h-screen bg-gradient-to-b from-[#0a0a0a] to-[#1a1a1a] pt-24">
				<div className="max-w-7xl mx-auto px-6 py-12">
					<div className="flex justify-between items-center mb-12">
						<div>
							<h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-[#007AFF] to-[#00C6FF]">
								Your Campaigns
							</h1>
							<p className="mt-2 text-white/60">Manage and track your crypto marketing campaigns</p>
						</div>
						<motion.button
							whileHover={{ scale: 1.05 }}
							whileTap={{ scale: 0.95 }}
							onClick={() => setIsCreating(true)}
							className="rounded-xl bg-gradient-to-r from-[#007AFF] to-[#00C6FF] px-6 py-3 text-base font-semibold text-white shadow-lg hover:shadow-[#007AFF]/20 hover:from-[#0056b3] hover:to-[#00A6FF] transition-all duration-300"
						>
							Create Campaign
						</motion.button>
					</div>

					<div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
						<AnimatePresence>
							{campaigns.map((campaign, index) => (
								<motion.div
									key={campaign.id}
									initial={{ opacity: 0, y: 20 }}
									animate={{ opacity: 1, y: 0 }}
									exit={{ opacity: 0, y: -20 }}
									transition={{ delay: index * 0.1 }}
									className="group relative bg-gradient-to-b from-white/[0.08] to-transparent rounded-2xl p-6 hover:from-white/[0.12] transition-all duration-300"
								>
									<div className="absolute inset-0 bg-gradient-to-r from-[#007AFF]/0 to-[#00C6FF]/0 group-hover:from-[#007AFF]/5 group-hover:to-[#00C6FF]/5 rounded-2xl transition-all duration-300" />
									<div className="relative">
										<h3 className="text-xl font-semibold text-white group-hover:text-[#007AFF] transition-colors">
											{campaign.name}
										</h3>
										<p className="mt-2 text-white/60 group-hover:text-white/80 transition-colors">
											{campaign.description}
										</p>
										<div className="mt-6 flex items-center justify-between">
											<span className="px-3 py-1 text-sm rounded-full bg-[#007AFF]/10 text-[#007AFF]">
												{campaign.status}
											</span>
											<button className="text-[#007AFF] hover:text-[#00C6FF] transition-colors flex items-center gap-2">
												View Details <span aria-hidden="true">→</span>
											</button>
										</div>
									</div>
								</motion.div>
							))}
						</AnimatePresence>
					</div>
				</div>
				<AnimatePresence>
					{isCreating && <CampaignForm onSubmit={handleCreateCampaign} onCancel={() => setIsCreating(false)} />}
				</AnimatePresence>
			</div>
		</>
	);
};

export default Campaigns;
