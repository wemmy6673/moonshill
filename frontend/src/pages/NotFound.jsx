import { Link } from "wouter";
import { motion } from "framer-motion";

const NotFound = () => {
	return (
		<div className="min-h-screen bg-[#0e0e10] flex items-center justify-center p-4">
			<div className="text-center">
				<motion.div
					initial={{ opacity: 0, y: 20 }}
					animate={{ opacity: 1, y: 0 }}
					transition={{ duration: 0.5 }}
					className="space-y-6"
				>
					{/* Animated Moon Icon */}
					<motion.div
						animate={{
							rotate: [0, 10, -10, 0],
							scale: [1, 1.1, 1],
						}}
						transition={{
							duration: 4,
							repeat: Infinity,
							repeatType: "reverse",
						}}
						className="text-8xl mb-4"
					>
						🌕
					</motion.div>

					{/* 404 Text */}
					<motion.h1
						initial={{ opacity: 0 }}
						animate={{ opacity: 1 }}
						transition={{ delay: 0.2 }}
						className="text-9xl font-bold text-[#eaeaea] mb-4"
					>
						404
					</motion.h1>

					{/* Message */}
					<motion.div
						initial={{ opacity: 0 }}
						animate={{ opacity: 1 }}
						transition={{ delay: 0.4 }}
						className="space-y-4"
					>
						<h2 className="text-2xl font-semibold text-[#eaeaea]">Oops! Page Not Found</h2>
						<p className="text-gray-400 max-w-md mx-auto">
							Looks like this page has mooned to another dimension. Let's get you back on track!
						</p>
					</motion.div>

					{/* Action Buttons */}
					<motion.div
						initial={{ opacity: 0 }}
						animate={{ opacity: 1 }}
						transition={{ delay: 0.6 }}
						className="flex flex-col sm:flex-row gap-4 justify-center mt-8"
					>
						<Link href="/">
							<motion.button
								whileHover={{ scale: 1.02 }}
								whileTap={{ scale: 0.98 }}
								className="px-8 py-3 bg-[#007AFF] text-white rounded-lg font-medium hover:bg-[#0056b3] transition-colors duration-200"
							>
								Go Home
							</motion.button>
						</Link>
						<Link href="/campaigns">
							<motion.button
								whileHover={{ scale: 1.02 }}
								whileTap={{ scale: 0.98 }}
								className="px-8 py-3 border border-[#2a2a2a] text-[#eaeaea] rounded-lg font-medium hover:bg-[#1a1a1a] transition-colors duration-200"
							>
								Explore Campaigns
							</motion.button>
						</Link>
					</motion.div>

					{/* Decorative Elements */}
					<motion.div
						initial={{ opacity: 0 }}
						animate={{ opacity: 1 }}
						transition={{ delay: 0.8 }}
						className="mt-12 text-gray-500 text-sm"
					>
						<p>Need help? Contact our support team</p>
						<div className="flex justify-center gap-4 mt-4">
							<motion.a
								href="https://twitter.com/moonshill"
								target="_blank"
								rel="noopener noreferrer"
								whileHover={{ scale: 1.1 }}
								className="text-gray-400 hover:text-[#007AFF] transition-colors"
							>
								<svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
									<path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z" />
								</svg>
							</motion.a>
							<motion.a
								href="https://t.me/moonshill"
								target="_blank"
								rel="noopener noreferrer"
								whileHover={{ scale: 1.1 }}
								className="text-gray-400 hover:text-[#007AFF] transition-colors"
							>
								<svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
									<path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.562 8.248-1.97 9.341c-.145.658-.537.818-1.084.508l-3-2.21-1.446 1.394c-.14.18-.357.223-.535.223l.19-2.72 5.56-5.023c.232-.21-.054-.327-.358-.118l-6.871 4.326-2.962-.924c-.643-.204-.657-.643.136-.953l11.57-4.461c.535-.197 1.004.13.832.943z" />
								</svg>
							</motion.a>
						</div>
					</motion.div>
				</motion.div>
			</div>
		</div>
	);
};

export default NotFound;
