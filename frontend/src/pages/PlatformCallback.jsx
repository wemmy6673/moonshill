import { useEffect, useState } from "react";
import { useLocation, useSearchParams, useParams } from "wouter";
import { motion, AnimatePresence } from "framer-motion";
import { useMutation } from "@tanstack/react-query";
import { createFetcher } from "../libs/fetcher";
import config from "../libs/config";
import PageLoader from "../components/common/PageLoader";
import useWorkspace from "../hooks/useWorkspace";
import useSnack from "../hooks/useSnack";
const PLATFORM_CONFIGS = {
	twitter: {
		name: "Twitter",
		icon: (
			<svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
				<path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
			</svg>
		),
		color: "#1DA1F2",
	},
	discord: {
		name: "Discord",
		icon: (
			<svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
				<path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515a.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0a12.64 12.64 0 0 0-.617-1.25a.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057a19.9 19.9 0 0 0 5.993 3.03a.078.078 0 0 0 .084-.028a14.09 14.09 0 0 0 1.226-1.994a.076.076 0 0 0-.041-.106a13.107 13.107 0 0 1-1.872-.892a.077.077 0 0 1-.008-.128a10.2 10.2 0 0 0 .372-.292a.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127a12.299 12.299 0 0 1-1.873.892a.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028a19.839 19.839 0 0 0 6.002-3.03a.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419c0-1.333.956-2.419 2.157-2.419c1.21 0 2.176 1.096 2.157 2.42c0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419c0-1.333.955-2.419 2.157-2.419c1.21 0 2.176 1.096 2.157 2.42c0 1.333-.946 2.418-2.157 2.418z" />
			</svg>
		),
		color: "#7289DA",
	},
	telegram: {
		name: "Telegram",
		icon: (
			<svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
				<path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12a12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472c-.18 1.898-.962 6.502-1.36 8.627c-.168.9-.499 1.201-.82 1.23c-.696.065-1.225-.46-1.9-.902c-1.056-.693-1.653-1.124-2.678-1.8c-1.185-.78-.417-1.21.258-1.91c.177-.184 3.247-2.977 3.307-3.23c.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345c-.48.33-.913.49-1.302.48c-.428-.008-1.252-.241-1.865-.44c-.752-.245-1.349-.374-1.297-.789c.027-.216.325-.437.893-.663c3.498-1.524 5.83-2.529 6.998-3.014c3.332-1.386 4.025-1.627 4.476-1.635z" />
			</svg>
		),
		color: "#0088cc",
	},
};

const HelpIcon = ({ onMouseEnter, onMouseLeave, isHovered }) => (
	<motion.div
		className="absolute top-4 right-4 cursor-help"
		whileHover={{ scale: 1.1 }}
		onMouseEnter={onMouseEnter}
		onMouseLeave={onMouseLeave}
	>
		<div className="relative">
			<svg
				className="w-5 h-5 text-white/40 hover:text-white/60 transition-colors"
				fill="none"
				viewBox="0 0 24 24"
				stroke="currentColor"
			>
				<path
					strokeLinecap="round"
					strokeLinejoin="round"
					strokeWidth={2}
					d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M12 21a9 9 0 110-18 9 9 0 010 18z"
				/>
			</svg>
			<AnimatePresence>
				{isHovered && (
					<motion.div
						initial={{ opacity: 0, y: 10 }}
						animate={{ opacity: 1, y: 0 }}
						exit={{ opacity: 0, y: 10 }}
						className="absolute bottom-full right-0 mb-2 w-64 p-3 bg-[#1a1a1a] rounded-xl shadow-xl text-sm text-white/80 border border-white/10"
					>
						Having issues with the connection? Contact our support team at support@moonshill.com for assistance.
					</motion.div>
				)}
			</AnimatePresence>
		</div>
	</motion.div>
);

const PlatformCallback = () => {
	const { platform } = useParams();
	const [searchParams] = useSearchParams();
	const [, navigate] = useLocation();
	const [error, setError] = useState(null);
	const [isHelpHovered, setIsHelpHovered] = useState(false);
	const snack = useSnack();
	const { workspace, pending, accessToken } = useWorkspace();

	const platformConfig = PLATFORM_CONFIGS[platform?.toLowerCase()];

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
		mutate: processPlatformCallback,
		data,
		isError,
		isSuccess,
		error: mutationError,
	} = useMutation({
		mutationFn: createFetcher({
			method: "POST",
			url: `${config.endpoints.platformCallback}/${platform}`,
			auth: accessToken,
		}),
	});

	useEffect(() => {
		if (isSuccess) {
			if (data.isConnected) {
				snack.success("Platform connected successfully");
				navigate(`/campaigns/${data.campaignId}`);
			} else {
				setError("Platform connection failed");
				snack.error("Platform connection failed");
				navigate("/campaigns");
			}
		}
	}, [isSuccess, data]);

	useEffect(() => {
		if (!platformConfig) {
			setError("Invalid platform specified");
			return;
		}

		const state = searchParams.get("state");

		// Process the OAuth callback
		processPlatformCallback({ state, platform, authResUrl: window.location.href });
	}, [platform, searchParams, processPlatformCallback, navigate, platformConfig]);

	if (pending) {
		return <PageLoader />;
	}

	if (!platformConfig) {
		return (
			<motion.div
				initial={{ opacity: 0 }}
				animate={{ opacity: 1 }}
				exit={{ opacity: 0 }}
				className="min-h-screen bg-[#0A0A0A] flex items-center justify-center p-4"
			>
				<motion.div
					initial={{ scale: 0.9, y: 20 }}
					animate={{ scale: 1, y: 0 }}
					className="w-full max-w-md p-6 rounded-2xl bg-white/5 text-center relative"
				>
					<HelpIcon
						onMouseEnter={() => setIsHelpHovered(true)}
						onMouseLeave={() => setIsHelpHovered(false)}
						isHovered={isHelpHovered}
					/>
					<motion.div
						initial={{ scale: 0.5, opacity: 0 }}
						animate={{ scale: 1, opacity: 1 }}
						className="text-red-500 mb-4"
					>
						<svg className="w-12 h-12 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path
								strokeLinecap="round"
								strokeLinejoin="round"
								strokeWidth={2}
								d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
							/>
						</svg>
					</motion.div>
					<h1 className="text-xl font-bold text-white mb-2">Invalid Platform</h1>
					<p className="text-white/60 mb-6">The specified platform is not supported.</p>
					<motion.button
						whileHover={{ scale: 1.02 }}
						whileTap={{ scale: 0.98 }}
						onClick={() => navigate("/campaigns")}
						className="w-full px-4 py-2 rounded-xl bg-white/10 text-white hover:bg-white/20 transition-colors"
					>
						Return to Campaigns
					</motion.button>
				</motion.div>
			</motion.div>
		);
	}

	return (
		<motion.div
			initial={{ opacity: 0 }}
			animate={{ opacity: 1 }}
			exit={{ opacity: 0 }}
			className="min-h-screen bg-[#0A0A0A] flex items-center justify-center p-4"
		>
			<motion.div
				initial={{ scale: 0.9, y: 20 }}
				animate={{ scale: 1, y: 0 }}
				className="w-full max-w-md p-6 rounded-2xl bg-white/5 text-center relative"
			>
				<HelpIcon
					onMouseEnter={() => setIsHelpHovered(true)}
					onMouseLeave={() => setIsHelpHovered(false)}
					isHovered={isHelpHovered}
				/>
				{!isError && !error ? (
					<>
						<div className="mb-6">
							<motion.div
								initial={{ scale: 0.5, opacity: 0 }}
								animate={{ scale: 1, opacity: 1 }}
								className="w-16 h-16 rounded-2xl mx-auto mb-4 flex items-center justify-center"
								style={{ backgroundColor: `${platformConfig.color}20` }}
							>
								<motion.div
									animate={{
										scale: [1, 1.1, 1],
										rotate: [0, 5, -5, 0],
									}}
									transition={{
										duration: 2,
										repeat: Infinity,
										ease: "easeInOut",
									}}
									className={`text-[${platformConfig.color}]`}
								>
									{platformConfig.icon}
								</motion.div>
							</motion.div>
							<motion.h1
								initial={{ y: 20, opacity: 0 }}
								animate={{ y: 0, opacity: 1 }}
								className="text-xl font-bold text-white mb-2"
							>
								Connecting to {platformConfig.name}
							</motion.h1>
							<motion.p
								initial={{ y: 20, opacity: 0 }}
								animate={{ y: 0, opacity: 1 }}
								transition={{ delay: 0.1 }}
								className="text-white/60"
							>
								Please wait while we process your authentication...
							</motion.p>
						</div>
						<motion.div
							animate={{
								opacity: [1, 0.5, 1],
							}}
							transition={{
								duration: 1.5,
								repeat: Infinity,
								ease: "easeInOut",
							}}
						>
							<PageLoader isPageWide={false} />
						</motion.div>
					</>
				) : (
					<motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}>
						<motion.div
							initial={{ scale: 0.5, opacity: 0 }}
							animate={{ scale: 1, opacity: 1 }}
							className="text-red-500 mb-4"
						>
							<svg className="w-12 h-12 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path
									strokeLinecap="round"
									strokeLinejoin="round"
									strokeWidth={2}
									d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
								/>
							</svg>
						</motion.div>
						<motion.h1
							initial={{ y: 20, opacity: 0 }}
							animate={{ y: 0, opacity: 1 }}
							className="text-xl font-bold text-white mb-2"
						>
							Authentication Failed
						</motion.h1>
						<motion.p
							initial={{ y: 20, opacity: 0 }}
							animate={{ y: 0, opacity: 1 }}
							transition={{ delay: 0.1 }}
							className="text-white/60 mb-6"
						>
							{error || mutationError?.message}
						</motion.p>
						<motion.button
							whileHover={{ scale: 1.02 }}
							whileTap={{ scale: 0.98 }}
							onClick={() => navigate("/campaigns")}
							className="w-full px-4 py-2 rounded-xl bg-white/10 text-white hover:bg-white/20 transition-colors"
						>
							Return to Campaigns
						</motion.button>
					</motion.div>
				)}
			</motion.div>
		</motion.div>
	);
};

export default PlatformCallback;
