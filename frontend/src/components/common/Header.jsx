import { useState } from "react";
import { Link } from "wouter";
import { motion, AnimatePresence } from "framer-motion";
import logoWhite from "../../assets/logo-white.png";
import logoBlue from "../../assets/logo-blue.png";

const Header = () => {
	const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

	const mobileMenuVariants = {
		closed: {
			opacity: 0,
			x: "100%",
			transition: {
				duration: 0.3,
				ease: "easeInOut",
			},
		},
		open: {
			opacity: 1,
			x: 0,
			transition: {
				duration: 0.3,
				ease: "easeInOut",
			},
		},
	};

	return (
		<>
			<nav
				className={`fixed top-0 left-0 right-0 z-40 transition-all duration-300 ${
					isMobileMenuOpen ? "bg-transparent" : "bg-[#0a0a0a]/80 backdrop-blur-lg"
				} border-b border-[#1a1a1a]`}
			>
				<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
					<div className="flex items-center justify-between h-16 sm:h-20">
						<motion.div
							initial={{ opacity: 0, x: -20 }}
							animate={{ opacity: 1, x: 0 }}
							className="flex items-center space-x-2 sm:space-x-3"
						>
							<Link href="/" className="flex items-center">
								<img src={logoWhite} alt="MoonShill" className="h-6 sm:h-8" />
								<span className="ml-2 text-lg sm:text-xl font-semibold">MoonShill</span>
							</Link>
						</motion.div>

						<div className="hidden sm:flex items-center space-x-8">
							<motion.div
								initial={{ opacity: 0, y: -10 }}
								animate={{ opacity: 1, y: 0 }}
								className="flex items-center space-x-8"
							>
								<Link href="/features" className="text-gray-300 hover:text-white transition-colors">
									Features
								</Link>
								<Link href="/pricing" className="text-gray-300 hover:text-white transition-colors">
									Pricing
								</Link>
								<Link href="/login" className="text-gray-300 hover:text-white transition-colors">
									Login
								</Link>
								<Link
									href="/signup"
									className="bg-[#007AFF] text-white px-4 py-2 rounded-lg hover:bg-[#0056b3] transition-colors"
								>
									Get Started
								</Link>
							</motion.div>
						</div>

						{/* Mobile menu button */}
						<div className="sm:hidden">
							<button
								type="button"
								className="text-gray-300 hover:text-white focus:outline-none"
								onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
							>
								{isMobileMenuOpen ? (
									<svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
										<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
									</svg>
								) : (
									<svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
										<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
									</svg>
								)}
							</button>
						</div>
					</div>
				</div>
			</nav>

			{/* Mobile Menu Overlay */}
			<AnimatePresence>
				{isMobileMenuOpen && (
					<>
						{/* Backdrop */}
						<motion.div
							initial={{ opacity: 0 }}
							animate={{ opacity: 1 }}
							exit={{ opacity: 0 }}
							className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 sm:hidden"
							onClick={() => setIsMobileMenuOpen(false)}
						/>
						{/* Menu */}
						<motion.div
							variants={mobileMenuVariants}
							initial="closed"
							animate="open"
							exit="closed"
							className="fixed top-0 right-0 bottom-0 w-64 bg-[#121212] border-l border-[#1a1a1a] z-50 sm:hidden"
						>
							<div className="flex flex-col h-full">
								<div className="p-4 border-b border-[#1a1a1a]">
									<div className="flex items-center space-x-3">
										<img src={logoWhite} alt="MoonShill" className="h-8 w-auto" />
										<span className="text-xl font-bold text-[#007AFF]">MoonShill</span>
									</div>
								</div>
								<div className="flex-1 p-4 space-y-4">
									<Link
										href="/features"
										className="block text-gray-300 hover:text-white transition-colors py-2"
										onClick={() => setIsMobileMenuOpen(false)}
									>
										Features
									</Link>
									<Link
										href="/pricing"
										className="block text-gray-300 hover:text-white transition-colors py-2"
										onClick={() => setIsMobileMenuOpen(false)}
									>
										Pricing
									</Link>
									<Link
										href="/login"
										className="block text-gray-300 hover:text-white transition-colors py-2"
										onClick={() => setIsMobileMenuOpen(false)}
									>
										Login
									</Link>
									<Link
										href="/signup"
										className="block bg-[#007AFF] text-white px-4 py-2 rounded-lg hover:bg-[#0056b3] transition-colors text-center"
										onClick={() => setIsMobileMenuOpen(false)}
									>
										Get Started
									</Link>
								</div>
							</div>
						</motion.div>
					</>
				)}
			</AnimatePresence>
		</>
	);
};

export default Header;
