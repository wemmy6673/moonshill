import { motion } from "framer-motion";

const ErrorView = ({ message = "Something went wrong", description, retryFunc, isPageWide = false }) => {
	const containerStyles = isPageWide
		? "fixed inset-0 bg-[#0a0a0a] flex items-center justify-center p-4 sm:p-6 z-50"
		: "w-full flex items-center justify-center p-4 sm:p-6";

	return (
		<motion.div
			initial={{ opacity: 0, y: 20 }}
			animate={{ opacity: 1, y: 0 }}
			exit={{ opacity: 0, y: -20 }}
			className={containerStyles}
		>
			<div className="w-full max-w-lg bg-gradient-to-b from-white/[0.05] to-white/[0.02] backdrop-blur-sm border border-white/10 rounded-2xl p-4 sm:p-6 text-center space-y-4">
				{/* Error Icon */}
				<div className="mb-3 sm:mb-4 relative">
					<div className="absolute inset-0 bg-red-500/20 blur-2xl rounded-full" />
					<div className="relative w-12 h-12 sm:w-16 sm:h-16 mx-auto bg-gradient-to-br from-red-500/80 to-red-600/80 rounded-full flex items-center justify-center">
						<svg
							className="w-6 h-6 sm:w-8 sm:h-8 text-white"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
							strokeWidth={2}
						>
							<path
								strokeLinecap="round"
								strokeLinejoin="round"
								d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
							/>
						</svg>
					</div>
				</div>

				{/* Error Message */}
				<h3 className=" sm:text-lg lg:font-semibold text-white mb-2">{message}</h3>

				{/* Optional Description */}
				{description && (
					<p className="text-sm sm:text-base text-white/60 mb-4 sm:mb-6 max-w-md mx-auto">{description}</p>
				)}

				{/* Retry Button */}
				{retryFunc && (
					<motion.button
						whileHover={{ scale: 1.02 }}
						whileTap={{ scale: 0.98 }}
						onClick={retryFunc}
						className="inline-flex items-center px-4 sm:px-6 py-2 sm:py-3 rounded-xl bg-gradient-to-r from-[#007AFF] to-[#00C6FF] text-sm sm:text-base text-white font-medium shadow-lg shadow-[#007AFF]/10 hover:shadow-[#007AFF]/20 transition-shadow"
					>
						<svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
							<path
								strokeLinecap="round"
								strokeLinejoin="round"
								d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
							/>
						</svg>
						Try Again
					</motion.button>
				)}
			</div>
		</motion.div>
	);
};

export default ErrorView;
