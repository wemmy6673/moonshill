import { motion } from "framer-motion";

const CampaignHeader = ({ campaign, navigate, setIsEditing, setShowDeleteConfirm }) => {
	return (
		<div className="flex flex-col gap-6 mb-8">
			{/* Navigation and Type */}
			<div className="flex items-center gap-3 text-white/60">
				<button
					onClick={() => navigate("/campaigns")}
					className="hover:text-white transition-colors flex items-center gap-1 text-sm"
				>
					<span aria-hidden="true">←</span> Back to Campaigns
				</button>
				<span className="text-white/20">•</span>
				<span className="text-sm font-medium px-2.5 py-1 rounded-full bg-gradient-to-r from-[#007AFF]/10 to-[#00C6FF]/10 text-[#007AFF]">
					{campaign.campaignType}
				</span>
			</div>

			{/* Campaign Info and Actions */}
			<div className="flex flex-col sm:flex-row items-start justify-between gap-4">
				{/* Campaign Details */}
				<div className="flex-1 min-w-0">
					<div className="flex flex-col gap-1">
						<div className="flex items-baseline gap-2">
							<div className="flex items-center gap-3">
								<div className="hidden sm:flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-r from-[#007AFF]/10 to-[#00C6FF]/10">
									<svg className="w-5 h-5 text-[#007AFF]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
										<path
											strokeLinecap="round"
											strokeLinejoin="round"
											strokeWidth={2}
											d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z"
										/>
									</svg>
								</div>
								<h1 className="text-2xl sm:text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-[#007AFF] to-[#00C6FF] truncate">
									{campaign.campaignName}
								</h1>
							</div>
							<span className="hidden sm:inline text-white/40">•</span>
							<h2 className="hidden sm:block text-lg font-medium text-white/60 truncate">{campaign.projectName}</h2>
						</div>
						{/* Show project name below on mobile */}
						<h2 className="sm:hidden text-base font-medium text-white/60 truncate">{campaign.projectName}</h2>
					</div>
				</div>

				{/* Action Buttons */}
				<div className="flex gap-3 self-stretch sm:self-start">
					<motion.button
						whileHover={{ scale: 1.02 }}
						whileTap={{ scale: 0.98 }}
						onClick={() => setIsEditing(true)}
						className="flex-1 sm:flex-initial flex items-center justify-center gap-2 px-4 py-2 rounded-xl 
							bg-gradient-to-r from-[#007AFF]/5 to-[#00C6FF]/5 text-[#007AFF] 
							hover:from-[#007AFF]/10 hover:to-[#00C6FF]/10 transition-all
							border border-[#007AFF]/10"
					>
						<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path
								strokeLinecap="round"
								strokeLinejoin="round"
								strokeWidth={2}
								d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
							/>
						</svg>
						<span>Edit</span>
					</motion.button>
					<motion.button
						whileHover={{ scale: 1.02 }}
						whileTap={{ scale: 0.98 }}
						onClick={() => setShowDeleteConfirm(true)}
						className="flex-1 sm:flex-initial flex items-center justify-center gap-2 px-4 py-2 rounded-xl 
							bg-red-500/5 text-red-500 hover:bg-red-500/10 transition-colors border border-red-500/10"
					>
						<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path
								strokeLinecap="round"
								strokeLinejoin="round"
								strokeWidth={2}
								d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
							/>
						</svg>
						<span>Delete</span>
					</motion.button>
				</div>
			</div>
		</div>
	);
};

export default CampaignHeader;
