import { Link } from "wouter";
import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";
import logoWhite from "../assets/logo-white.png";
import logoBlue from "../assets/logo-blue.png";
import Header from "@/components/common/Header";

const Landing = () => {
	const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

	const scrollToSection = (id) => {
		const element = document.getElementById(id);
		if (element) {
			element.scrollIntoView({ behavior: "smooth" });
		}
		setIsMobileMenuOpen(false);
	};

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

	const features = [
		{
			name: "AI-Powered Meme & Content Factory",
			description:
				"Create viral crypto content at scale. From memes to call-to-action posts, our AI crafts high-performing media tailored to your project's tone, trends, and audience. Auto-adapt formats, schedule coordinated drops, and drive narrative dominance.",
			icon: (
				<svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path
						strokeLinecap="round"
						strokeLinejoin="round"
						strokeWidth={2}
						d="M14 10l-2 1m0 0l-2-1m2 1v2.5M20 7l-2 1m2-1l-2-1m2 1v2.5M14 4l-2-1-2 1M4 7l2-1M4 7l2 1M4 7v2.5M12 21l-2-1m2 1l2-1m-2 1v-2.5M6 18l-2-1v-2.5M18 18l2-1v-2.5"
					/>
				</svg>
			),
		},
		{
			name: "Multi-Platform Automation",
			description:
				"One shill, all platforms. Automate engagement across Twitter (X), Telegram, and Discord with AI that speaks fluent degen, hypebeast, or technical analyst — based on audience, time, and sentiment.",
			icon: (
				<svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
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
			name: "Smart Engagement Strategies",
			description:
				"Deploy AI agents that engage like real holders. Simulate influencer threads, reply to trending tweets, stir hype in Telegram groups, and adapt in real time to price action or sentiment swings.",
			icon: (
				<svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path
						strokeLinecap="round"
						strokeLinejoin="round"
						strokeWidth={2}
						d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
					/>
				</svg>
			),
		},
		{
			name: "Advanced Analytics Dashboard",
			description:
				"See what's pumping your bags. Track virality scores, audience reactions, engagement ROI, and wallet-linked conversion metrics — all in one battle-tested dashboard.",
			icon: (
				<svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path
						strokeLinecap="round"
						strokeLinejoin="round"
						strokeWidth={2}
						d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
					/>
				</svg>
			),
		},
		{
			name: "Community Growth Tools",
			description:
				"Find your next 1,000 holders. Automate interactions with wallet-tagged users, onboard lurkers, reward engagement with token-based incentives, and build growth loops into your community.",
			icon: (
				<svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path
						strokeLinecap="round"
						strokeLinejoin="round"
						strokeWidth={2}
						d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
					/>
				</svg>
			),
		},
		{
			name: "Anti-Bot Detection Shield",
			description:
				"Shill smart, stay undetected. Our AI mimics human rhythm, varies tone, delays actions, and avoids over-posting — ensuring your campaigns fly under the radar of anti-bot systems.",
			icon: (
				<svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path
						strokeLinecap="round"
						strokeLinejoin="round"
						strokeWidth={2}
						d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
					/>
				</svg>
			),
		},
	];

	const pricingPlans = [
		{
			name: "Starter Pack",
			credits: "750",
			price: "30",
			description: "Perfect for testing the waters",
			features: [
				"750 AI-generated memes & posts",
				"Basic engagement automation",
				"Platform integration (X, Telegram)",
				"Standard analytics dashboard",
			],
		},
		{
			name: "Growth Pack",
			credits: "2500",
			price: "85",
			description: "Most popular for active projects",
			features: [
				"2500 AI-generated memes & posts",
				"Advanced engagement automation",
				"All platform integrations",
				"Premium analytics dashboard",
				"Custom text context support",
				"Priority support",
			],
			highlighted: true,
		},
		{
			name: "Whale Pack",
			credits: "5000",
			price: "150",
			description: "For serious moon missions",
			features: [
				"5000 AI-generated memes & posts",
				"Full automation suite",
				"Project featured on homepage",
				"PDF/TXT/CSV context support",
				"24/7 priority support",
				"Custom campaign strategies",
			],
		},
	];

	return (
		<div className="min-h-screen bg-[#0a0a0a] text-white">
			<Header />
			{/* Navigation */}
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
							<button onClick={() => scrollToSection("hero")} className="flex items-center">
								<img src={logoWhite} alt="MoonShill" className="h-6 sm:h-8" />
								<span className="ml-2 text-lg sm:text-xl font-semibold">MoonShill</span>
							</button>
						</motion.div>

						<div className="hidden sm:flex items-center space-x-8">
							<motion.div
								initial={{ opacity: 0, y: -10 }}
								animate={{ opacity: 1, y: 0 }}
								className="flex items-center space-x-8"
							>
								<button
									onClick={() => scrollToSection("features")}
									className="text-gray-300 hover:text-white hover:scale-105 transition-all duration-200"
								>
									Features
								</button>
								<button
									onClick={() => scrollToSection("pricing")}
									className="text-gray-300 hover:text-white hover:scale-105 transition-all duration-200"
								>
									Pricing
								</button>
								<Link
									href="/login"
									className="text-gray-300 hover:text-white hover:scale-105 transition-all duration-200"
								>
									Login
								</Link>
								<Link
									href="/signup"
									className="bg-[#007AFF] text-white px-4 py-2 rounded-lg hover:bg-[#0056b3] hover:scale-105 transition-all duration-200"
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
									<button
										onClick={() => scrollToSection("features")}
										className="block text-gray-300 hover:text-white transition-colors py-2 w-full text-left"
									>
										Features
									</button>
									<button
										onClick={() => scrollToSection("pricing")}
										className="block text-gray-300 hover:text-white transition-colors py-2 w-full text-left"
									>
										Pricing
									</button>
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

			{/* Hero Section */}
			<section id="hero" className="relative pt-32 pb-20 px-4 sm:px-6 lg:px-8 overflow-hidden">
				{/* Background Logo */}
				<motion.div
					initial={{ opacity: 0, scale: 0.8 }}
					animate={{ opacity: 0.05, scale: 1 }}
					transition={{ duration: 1, ease: "easeOut" }}
					className="absolute inset-0 flex items-center justify-center pointer-events-none"
				>
					<img src={logoBlue} alt="" className="w-[800px] h-auto" />
				</motion.div>
				<div className="max-w-7xl mx-auto relative">
					<motion.div
						initial={{ opacity: 0, y: 20 }}
						animate={{ opacity: 1, y: 0 }}
						transition={{ duration: 0.5 }}
						className="text-center"
					>
						<motion.div
							initial={{ scale: 0.8, opacity: 0 }}
							animate={{ scale: 1, opacity: 1 }}
							transition={{ duration: 0.5, delay: 0.2 }}
							className="mb-8 flex justify-center"
						>
							<img src={logoBlue} alt="MoonShill" className="h-16 w-auto" />
						</motion.div>
						<motion.h1
							initial={{ opacity: 0, y: 20 }}
							animate={{ opacity: 1, y: 0 }}
							transition={{ duration: 0.5, delay: 0.3 }}
							className="text-4xl sm:text-5xl md:text-6xl font-bold mb-6"
						>
							Automate the Hype.
							<br />
							<span className="text-[#007AFF]">Scale the Moon.</span>
						</motion.h1>
						<motion.p
							initial={{ opacity: 0, y: 20 }}
							animate={{ opacity: 1, y: 0 }}
							transition={{ duration: 0.5, delay: 0.4 }}
							className="text-xl text-gray-400 max-w-3xl mx-auto mb-8"
						>
							AI-powered multi-platform shilling engine for Web3 communities. Amplify your crypto project with
							intelligent meme generation and strategic posting.
						</motion.p>
						<motion.div
							initial={{ opacity: 0, y: 20 }}
							animate={{ opacity: 1, y: 0 }}
							transition={{ duration: 0.5, delay: 0.5 }}
							className="flex flex-col sm:flex-row gap-4 justify-center"
						>
							<Link href="/campaigns?new=1">
								<motion.button
									whileHover={{ scale: 1.05 }}
									whileTap={{ scale: 0.95 }}
									className="w-full sm:w-auto bg-[#007AFF] text-white px-8 py-4 rounded-lg text-lg font-medium hover:bg-[#0056b3] transition-colors"
								>
									Launch a Campaign
								</motion.button>
							</Link>
							<Link href="/campaigns">
								<motion.button
									whileHover={{ scale: 1.05 }}
									whileTap={{ scale: 0.95 }}
									className="w-full sm:w-auto border border-[#2a2a2a] text-[#eaeaea] px-8 py-4 rounded-lg text-lg font-medium hover:bg-[#1a1a1a] transition-colors"
								>
									Explore Campaigns
								</motion.button>
							</Link>
						</motion.div>
					</motion.div>
				</div>
			</section>

			{/* Features Section */}
			<section id="features" className="relative py-20 bg-[#121212]">
				{/* Background Pattern */}
				<motion.div
					initial={{ opacity: 0 }}
					animate={{ opacity: 0.05 }}
					transition={{ duration: 1 }}
					className="absolute inset-0 pointer-events-none"
				>
					<div
						className="absolute inset-0"
						style={{
							backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23007AFF' fill-opacity='0.1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
							backgroundSize: "60px 60px",
						}}
					/>
				</motion.div>
				<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
					<motion.div
						initial={{ opacity: 0, y: 20 }}
						animate={{ opacity: 1, y: 0 }}
						transition={{ duration: 0.5, delay: 0.2 }}
						className="text-center mb-16"
					>
						<h2 className="text-3xl sm:text-4xl font-bold mb-4">Powerful Features</h2>
						<p className="text-gray-400 max-w-2xl mx-auto">
							Everything you need to amplify your Web3 project's presence
						</p>
					</motion.div>

					<div className="mx-auto mt-16 max-w-7xl px-6 sm:mt-20 md:mt-24 lg:px-8">
						<dl className="mx-auto grid max-w-2xl grid-cols-1 gap-x-6 gap-y-10 text-base leading-7 text-gray-300 sm:grid-cols-2 lg:mx-0 lg:max-w-none lg:grid-cols-3 lg:gap-x-8 lg:gap-y-16">
							{features.map((feature) => (
								<motion.div
									key={feature.name}
									initial={{ opacity: 0, y: 20 }}
									whileInView={{ opacity: 1, y: 0 }}
									viewport={{ once: true }}
									className="group relative bg-gradient-to-b from-white/[0.08] to-transparent rounded-2xl p-8 hover:from-white/[0.12] transition-all duration-300"
								>
									<div className="flex h-16 w-16 items-center justify-center rounded-xl bg-gradient-to-r from-[#007AFF]/10 to-[#00C6FF]/10 group-hover:from-[#007AFF]/20 group-hover:to-[#00C6FF]/20 transition-all duration-300">
										<div className="text-gradient bg-gradient-to-r from-[#007AFF] to-[#00C6FF]">{feature.icon}</div>
									</div>
									<dt className="mt-6 text-xl font-semibold text-white group-hover:text-[#007AFF] transition-colors">
										{feature.name}
									</dt>
									<dd className="mt-2 text-white/60 group-hover:text-white/80 transition-colors">
										{feature.description}
									</dd>
								</motion.div>
							))}
						</dl>
					</div>
				</div>
			</section>

			{/* Pricing Section */}
			<section id="pricing" className="relative py-20">
				<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
					<motion.div
						initial={{ opacity: 0, y: 20 }}
						animate={{ opacity: 1, y: 0 }}
						transition={{ duration: 0.5 }}
						className="text-center mb-16"
					>
						<h2 className="text-3xl sm:text-4xl font-bold mb-4">Simple, Credit-Based Pricing</h2>
						<p className="text-gray-400 max-w-2xl mx-auto">
							Purchase credits once, use them across all features. No subscriptions, no hidden fees.
						</p>
					</motion.div>

					<div className="grid grid-cols-1 md:grid-cols-3 gap-8">
						{pricingPlans.map((plan) => (
							<motion.div
								key={plan.name}
								initial={{ opacity: 0, y: 20 }}
								whileInView={{ opacity: 1, y: 0 }}
								viewport={{ once: true }}
								className={`relative bg-gradient-to-b from-white/[0.08] to-transparent rounded-2xl p-8 ${
									plan.highlighted ? "border-2 border-[#007AFF] scale-105 md:scale-110" : "border border-white/10"
								}`}
							>
								{plan.highlighted && (
									<div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
										<span className="bg-[#007AFF] text-white px-3 py-1 rounded-full text-sm">Most Popular</span>
									</div>
								)}
								<div className="text-center mb-8">
									<h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
									<p className="text-gray-400 mb-4">{plan.description}</p>
									<div className="flex items-baseline justify-center">
										<span className="text-4xl font-bold">${plan.price}</span>
										<span className="text-gray-400 ml-2">/ {plan.credits} credits</span>
									</div>
								</div>
								<ul className="space-y-4 mb-8">
									{plan.features.map((feature, index) => (
										<li key={index} className="flex items-center">
											<svg
												className="h-5 w-5 text-[#007AFF] mr-3"
												fill="none"
												viewBox="0 0 24 24"
												stroke="currentColor"
											>
												<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
											</svg>
											{feature}
										</li>
									))}
								</ul>
								<Link href="/signup">
									<motion.button
										whileHover={{ scale: 1.05 }}
										whileTap={{ scale: 0.95 }}
										className={`w-full py-3 rounded-lg font-medium transition-colors ${
											plan.highlighted
												? "bg-[#007AFF] text-white hover:bg-[#0056b3]"
												: "bg-white/10 text-white hover:bg-white/20"
										}`}
									>
										Get Started
									</motion.button>
								</Link>
							</motion.div>
						))}
					</div>

					<div className="mt-16 text-center">
						<p className="text-gray-400">
							Need more credits? Contact us for custom enterprise packages tailored to your needs.
						</p>
					</div>
				</div>
			</section>

			{/* CTA Section */}
			<section className="relative py-20">
				<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
					<motion.div
						initial={{ opacity: 0, y: 20 }}
						animate={{ opacity: 1, y: 0 }}
						transition={{ duration: 0.5 }}
						className="bg-[#007AFF] rounded-2xl p-8 md:p-12 text-center relative overflow-hidden"
					>
						{/* Background Logo */}
						<motion.div
							initial={{ opacity: 0, scale: 0.8 }}
							animate={{ opacity: 0.1, scale: 1 }}
							transition={{ duration: 1, ease: "easeOut" }}
							className="absolute inset-0 flex items-center justify-center pointer-events-none"
						>
							<img src={logoWhite} alt="" className="w-[600px] h-auto" />
						</motion.div>
						<motion.h2
							initial={{ opacity: 0, y: 20 }}
							animate={{ opacity: 1, y: 0 }}
							transition={{ duration: 0.5, delay: 0.2 }}
							className="text-3xl sm:text-4xl font-bold mb-4"
						>
							Ready to Moon?
						</motion.h2>
						<motion.p
							initial={{ opacity: 0, y: 20 }}
							animate={{ opacity: 1, y: 0 }}
							transition={{ duration: 0.5, delay: 0.3 }}
							className="text-xl mb-8 max-w-2xl mx-auto"
						>
							Join thousands of Web3 projects already using MoonShill to grow their community
						</motion.p>
						<Link href="/signup">
							<motion.button
								whileHover={{ scale: 1.05 }}
								whileTap={{ scale: 0.95 }}
								className="bg-white text-[#007AFF] px-8 py-4 rounded-lg text-lg font-medium hover:bg-gray-100 transition-colors"
							>
								Get Started Now
							</motion.button>
						</Link>
					</motion.div>
				</div>
			</section>

			{/* Footer */}
			<footer className="bg-[#121212] border-t border-[#1a1a1a] py-16">
				<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
					<div className="grid grid-cols-1 md:grid-cols-3 gap-12 md:gap-8">
						<div className="col-span-1">
							<motion.div
								initial={{ opacity: 0, x: -20 }}
								animate={{ opacity: 1, x: 0 }}
								transition={{ duration: 0.5 }}
								className="flex items-center space-x-3 mb-6"
							>
								<img src={logoWhite} alt="MoonShill" className="h-8 w-auto" />
								<span className="text-xl font-bold text-[#007AFF]">MoonShill</span>
							</motion.div>
							<p className="text-gray-400 mb-6">Automate the Hype. Scale the Moon.</p>
							<div className="flex space-x-4">
								<a
									href="https://twitter.com/moonshill"
									target="_blank"
									rel="noopener noreferrer"
									className="text-gray-400 hover:text-[#007AFF] transition-colors"
								>
									<svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
										<path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z" />
									</svg>
								</a>
								<a
									href="https://t.me/moonshill"
									target="_blank"
									rel="noopener noreferrer"
									className="text-gray-400 hover:text-[#007AFF] transition-colors"
								>
									<svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
										<path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.562 8.248l-1.97 9.341c-.145.658-.537.818-1.084.508l-3-2.21-1.446 1.394c-.14.18-.357.223-.535.223l.19-2.72 5.56-5.023c.232-.21-.054-.327-.358-.118l-6.871 4.326-2.962-.924c-.643-.204-.657-.643.136-.953l11.57-4.461c.535-.197 1.004.13.832.943z" />
									</svg>
								</a>
								<a
									href="https://discord.gg/moonshill"
									target="_blank"
									rel="noopener noreferrer"
									className="text-gray-400 hover:text-[#007AFF] transition-colors"
								>
									<svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
										<path d="M20.317 4.37a19.791 19.791 0 00-4.885-1.515.074.074 0 00-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 00-5.487 0 12.64 12.64 0 00-.617-1.25.077.077 0 00-.079-.037A19.736 19.736 0 003.677 4.37a.07.07 0 00-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 00.031.057 19.9 19.9 0 005.993 3.03.078.078 0 00.084-.028c.462-.63.874-1.295 1.226-1.994a.076.076 0 00-.041-.106 13.107 13.107 0 01-1.872-.892.077.077 0 01-.008-.128 10.2 10.2 0 00.372-.292.074.074 0 01.077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 01.078.01c.12.098.246.198.373.292a.077.077 0 01-.006.127 12.299 12.299 0 01-1.873.892.077.077 0 00-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 00.084.028 19.839 19.839 0 006.002-3.03.077.077 0 00.032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 00-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z" />
									</svg>
								</a>
							</div>
						</div>

						<div className="col-span-1">
							<h4 className="font-semibold text-lg mb-6">Product</h4>
							<ul className="space-y-4">
								<li>
									<button
										onClick={() => scrollToSection("features")}
										className="text-gray-400 hover:text-[#007AFF] transition-colors"
									>
										Features
									</button>
								</li>
								<li>
									<button
										onClick={() => scrollToSection("pricing")}
										className="text-gray-400 hover:text-[#007AFF] transition-colors"
									>
										Pricing
									</button>
								</li>
								<li>
									<Link href="/campaigns" className="text-gray-400 hover:text-[#007AFF] transition-colors">
										Campaigns
									</Link>
								</li>
							</ul>
						</div>

						<div className="col-span-1">
							<h4 className="font-semibold text-lg mb-6">Resources</h4>
							<ul className="space-y-4">
								<li>
									<a
										href="https://coinmarketcap.com/community/articles/education/crypto-marketing/"
										target="_blank"
										rel="noopener noreferrer"
										className="text-gray-400 hover:text-[#007AFF] transition-colors"
									>
										Crypto Marketing Guide
									</a>
								</li>
								<li>
									<a
										href="https://academy.binance.com/en/articles/crypto-social-media-marketing-guide"
										target="_blank"
										rel="noopener noreferrer"
										className="text-gray-400 hover:text-[#007AFF] transition-colors"
									>
										Social Media Strategy
									</a>
								</li>
								<li>
									<a
										href="https://www.coingecko.com/learn/crypto-marketing"
										target="_blank"
										rel="noopener noreferrer"
										className="text-gray-400 hover:text-[#007AFF] transition-colors"
									>
										Market Analysis
									</a>
								</li>
							</ul>
						</div>
					</div>

					<div className="mt-12 pt-8 border-t border-[#1a1a1a] text-center">
						<p className="text-gray-400">&copy; {new Date().getFullYear()} MoonShill. All rights reserved.</p>
					</div>
				</div>
			</footer>
		</div>
	);
};

export default Landing;
