import { useState } from "react";
import { Link } from "wouter";
import { motion, AnimatePresence } from "framer-motion";
import ConfirmDialog from "./ConfirmDialog";

const AuthenticatedHeader = ({ workspace, logOut }) => {
	const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
	const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);

	const handleLogout = () => {
		setShowLogoutConfirm(true);
	};

	const confirmLogout = () => {
		setShowLogoutConfirm(false);
		logOut();
	};

	return (
		<header className="fixed inset-x-0 top-0 z-40 bg-[#0a0a0a]/80 backdrop-blur-sm border-b border-white/10">
			<div className="mx-auto w-full max-w-7xl">
				<nav className="px-4" aria-label="Global">
					<div className="flex h-16 items-center  justify-between">
						<div className="flex lg:flex-1">
							<Link to="/" className="-m-1.5 p-1.5 flex items-center gap-2">
								<span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-[#007AFF] to-[#00C6FF]">
									MoonShill
								</span>
							</Link>
						</div>

						{/* Mobile menu button */}
						<div className="flex lg:hidden">
							<button
								type="button"
								className="-m-2.5 inline-flex items-center justify-center rounded-md p-2.5 text-white/60"
								onClick={() => setMobileMenuOpen(true)}
							>
								<span className="sr-only">Open main menu</span>
								<svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
									<path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
								</svg>
							</button>
						</div>

						{/* Desktop navigation */}
						<div className="hidden lg:flex lg:gap-x-8">
							<Link
								to="/campaigns"
								className="text-sm font-semibold leading-6 text-white/80 hover:text-white transition-colors"
							>
								Campaigns
							</Link>
							<Link
								to="/analytics"
								className="text-sm font-semibold leading-6 text-white/60 hover:text-white transition-colors"
							>
								Analytics
							</Link>
							<Link
								to="/settings"
								className="text-sm font-semibold leading-6 text-white/60 hover:text-white transition-colors"
							>
								Settings
							</Link>
						</div>

						{/* User menu */}
						<div className="hidden lg:flex lg:flex-1 lg:justify-end lg:gap-x-6">
							<button className="text-sm font-semibold leading-6 text-white/60 ">
								Workspace · <span className="text-white font-semibold">{workspace?.name}</span>
							</button>
							<button
								onClick={handleLogout}
								className="rounded-xl bg-white/5 px-4 py-2 text-sm font-semibold text-white hover:bg-white/10 transition-colors"
							>
								Logout
							</button>
						</div>
					</div>
				</nav>
			</div>

			{/* Mobile menu */}
			<AnimatePresence>
				{mobileMenuOpen && (
					<>
						{/* Backdrop */}
						<motion.div
							initial={{ opacity: 0 }}
							animate={{ opacity: 1 }}
							exit={{ opacity: 0 }}
							onClick={() => setMobileMenuOpen(false)}
							className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
						/>

						{/* Menu panel */}
						<motion.div
							initial={{ opacity: 0, y: -10 }}
							animate={{ opacity: 1, y: 0 }}
							exit={{ opacity: 0, y: -10 }}
							className="fixed inset-x-0 top-16 z-50 p-4"
						>
							<div className="mx-auto max-w-7xl">
								<div className="rounded-2xl bg-[#0a0a0a] border border-white/10 p-6 shadow-2xl">
									<div className="flex flex-col space-y-4">
										<Link
											to="/campaigns"
											className="text-base font-semibold leading-6 text-white/80 hover:text-white transition-colors"
											onClick={() => setMobileMenuOpen(false)}
										>
											Campaigns
										</Link>
										<Link
											to="/analytics"
											className="text-base font-semibold leading-6 text-white/60 hover:text-white transition-colors"
											onClick={() => setMobileMenuOpen(false)}
										>
											Analytics
										</Link>
										<Link
											to="/settings"
											className="text-base font-semibold leading-6 text-white/60 hover:text-white transition-colors"
											onClick={() => setMobileMenuOpen(false)}
										>
											Settings
										</Link>
										<div className="border-t border-white/10 pt-4 flex flex-col space-y-4">
											<button className="text-base font-semibold leading-6 text-white/60  text-left">
												Workspace · <span className="text-white font-semibold">{workspace?.name}</span>
											</button>
											<button
												onClick={() => {
													setMobileMenuOpen(false);
													setShowLogoutConfirm(true);
												}}
												className="w-full rounded-xl bg-white/5 px-4 py-3 text-base font-semibold text-white hover:bg-white/10 transition-colors text-left"
											>
												Logout
											</button>
										</div>
									</div>
								</div>
							</div>
						</motion.div>
					</>
				)}
			</AnimatePresence>

			<ConfirmDialog
				isOpen={showLogoutConfirm}
				onClose={() => setShowLogoutConfirm(false)}
				onConfirm={confirmLogout}
				title="Confirm Logout"
				message="Are you sure you want to log out? You'll need to sign in again to access your campaigns."
			/>
		</header>
	);
};

export default AuthenticatedHeader;
