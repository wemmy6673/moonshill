import { motion } from "framer-motion";

const CampaignHeader = ({ campaign, navigate, setIsEditing, setShowDeleteConfirm }) => {
	return (
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
	);
};

export default CampaignHeader;
