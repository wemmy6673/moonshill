import { motion } from "framer-motion";

const CampaignAnalytics = () => {
	return (
		<div className="bg-white/5 rounded-xl p-4 sm:p-6">
			<h3 className="text-lg font-medium text-white mb-4 sm:mb-6">Campaign Analytics</h3>

			<div className="flex flex-col items-center justify-center py-8 sm:py-16 px-3 sm:px-4 bg-white/5 rounded-xl text-center">
				<motion.div
					initial={{ scale: 0.9, opacity: 0 }}
					animate={{ scale: 1, opacity: 1 }}
					transition={{ duration: 0.5 }}
					className="relative"
				>
					<div className="absolute inset-0 bg-[#007AFF]/20 blur-3xl rounded-full"></div>
					<motion.div
						animate={{
							scale: [1, 1.02, 1],
							rotate: [0, -1, 1, -1, 0],
						}}
						transition={{
							duration: 4,
							repeat: Infinity,
							repeatType: "reverse",
						}}
						className="relative"
					>
						<svg
							className="w-16 h-16 sm:w-24 sm:h-24 text-[#007AFF]"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
						>
							<path
								strokeLinecap="round"
								strokeLinejoin="round"
								strokeWidth={1.5}
								d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
							/>
						</svg>
					</motion.div>
				</motion.div>
				<motion.div
					initial={{ y: 20, opacity: 0 }}
					animate={{ y: 0, opacity: 1 }}
					transition={{ duration: 0.5, delay: 0.2 }}
					className="mt-4 sm:mt-6"
				>
					<h2 className="text-xl sm:text-2xl font-semibold text-white mb-2 sm:mb-3">Analytics Coming Soon</h2>
					<p className="text-sm sm:text-base text-white/60 max-w-md px-4">
						We're working on powerful analytics tools to help you track and optimize your campaign performance. Stay
						tuned for detailed insights and metrics.
					</p>
				</motion.div>
				<motion.div
					initial={{ y: 20, opacity: 0 }}
					animate={{ y: 0, opacity: 1 }}
					transition={{ duration: 0.5, delay: 0.4 }}
					className="mt-6 sm:mt-8 w-full px-4"
				>
					<div className="flex flex-col sm:flex-row sm:items-center sm:justify-center gap-4 sm:gap-8 px-3 sm:px-6 py-3 bg-white/5 rounded-xl max-w-lg mx-auto">
						<div className="text-center">
							<div className="text-[#007AFF] text-sm sm:text-base font-medium">Performance</div>
							<div className="text-white/40 text-xs sm:text-sm">Metrics</div>
						</div>
						<div className="text-center">
							<div className="text-[#007AFF] text-sm sm:text-base font-medium">Engagement</div>
							<div className="text-white/40 text-xs sm:text-sm">Analytics</div>
						</div>
						<div className="text-center">
							<div className="text-[#007AFF] text-sm sm:text-base font-medium">Growth</div>
							<div className="text-white/40 text-xs sm:text-sm">Tracking</div>
						</div>
					</div>
				</motion.div>
			</div>
		</div>
	);
};

export default CampaignAnalytics;
