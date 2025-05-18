import { motion, AnimatePresence } from "framer-motion";
import { useMutation } from "@tanstack/react-query";
import { createFetcher } from "../../libs/fetcher";
import config from "../../libs/config";
import { useEffect } from "react";
import useSnack from "../../hooks/useSnack";

const platformInfo = {
	twitter: {
		permissions: [
			"Read your profile",
			"Read your tweets",
			"Post tweets on your behalf",
			"Stay logged in",
			"See your followers and following",
		],
		icon: (
			<svg className="w-6 h-6 text-[#1DA1F2]" fill="currentColor" viewBox="0 0 24 24">
				<path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
			</svg>
		),
		type: "oauth",
	},
	telegram: {
		description: "A dedicated bot from our pool will be allocated to your campaign. You'll need to:",
		steps: [
			"Add the bot to your Telegram groups",
			"Grant message sending permissions",
			"The bot will handle all campaign interactions",
			"Monitor engagement through our dashboard",
		],
		icon: (
			<svg className="w-6 h-6 text-[#0088cc]" fill="currentColor" viewBox="0 0 24 24">
				<path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69a.2.2 0 00-.05-.18c-.06-.05-.14-.03-.21-.02-.09.02-1.49.95-4.22 2.79-.4.27-.76.41-1.08.4-.36-.01-1.04-.2-1.55-.37-.63-.2-1.12-.31-1.08-.66.02-.18.27-.36.74-.55 2.92-1.27 4.86-2.11 5.83-2.51 2.78-1.16 3.35-1.36 3.73-1.36.08 0 .27.02.39.12.1.08.13.19.14.27-.01.06.01.24 0 .24z" />
			</svg>
		),
		type: "bot",
	},
	discord: {
		permissions: ["Access your servers", "Send messages", "Manage roles", "Read messages"],
		icon: (
			<svg className="w-6 h-6 text-[#7289DA]" fill="currentColor" viewBox="0 0 24 24">
				<path d="M20.317 4.492c-1.53-.69-3.17-1.2-4.885-1.49a.075.075 0 00-.079.036c-.21.369-.444.85-.608 1.23a18.566 18.566 0 00-5.487 0 12.36 12.36 0 00-.617-1.23A.077.077 0 008.562 3c-1.714.29-3.354.8-4.885 1.491a.07.07 0 00-.032.027C.533 9.093-.32 13.555.099 17.961a.08.08 0 00.031.055 20.03 20.03 0 005.993 2.98.078.078 0 00.084-.026 13.83 13.83 0 001.226-1.963.074.074 0 00-.041-.104 13.201 13.201 0 01-1.872-.878.075.075 0 01-.008-.125c.126-.093.252-.19.372-.287a.075.075 0 01.078-.01c3.927 1.764 8.18 1.764 12.061 0a.075.075 0 01.079.009c.12.098.245.195.372.288a.075.075 0 01-.006.125c-.598.344-1.22.635-1.873.877a.075.075 0 00-.041.105c.36.687.772 1.341 1.225 1.962a.077.077 0 00.084.028 19.963 19.963 0 006.002-2.981.076.076 0 00.032-.054c.5-5.094-.838-9.52-3.549-13.442a.06.06 0 00-.031-.028z" />
			</svg>
		),
		type: "oauth",
	},
};

const PlatformConnectDialog = ({ isOpen, onClose, platform, auth, campaignId }) => {
	const snack = useSnack();

	const {
		mutate: connectPlatform,
		isPending,
		isError,
		error,
		isSuccess,
		data,
		reset,
	} = useMutation({
		mutationFn: createFetcher({
			url: `${config.endpoints.connectPlatform}`,
			method: "POST",
			auth,
		}),
	});

	useEffect(() => {
		if (isSuccess) {
			if (data.platform.toLowerCase() === platform.toLowerCase() && data.campaignId === campaignId) {
				window.location.href = data.authUrl;
			} else {
				snack.error("Something went wrong, please try again");
			}
		}

		if (isError) {
			snack.error(error?.message || "Failed to connect platform, please try again");
			reset();
		}
	}, [isSuccess, isError, error]);

	const handleConnect = (platform) => {
		let callbackUrl;

		switch (platform) {
			case "telegram":
				callbackUrl = `${window.location.origin}/platforms/telegram`;
				break;
			default:
				callbackUrl = `https://moonshill.pages.dev/platforms/${platform.toLowerCase()}`;
		}
		return () => {
			connectPlatform({
				platform,
				callbackUrl,
				campaignId,
			});
		};
	};

	const platformData = platformInfo[platform?.toLowerCase()];
	const isTelegram = platform?.toLowerCase() === "telegram";

	return (
		<AnimatePresence>
			{isOpen && (
				<div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
					<motion.div
						initial={{ opacity: 0, scale: 0.95 }}
						animate={{ opacity: 1, scale: 1 }}
						exit={{ opacity: 0, scale: 0.95 }}
						transition={{ duration: 0.2 }}
						className="relative w-full max-w-lg bg-[#1a1a1a] rounded-2xl shadow-xl overflow-hidden"
					>
						<div className="p-4 sm:p-6">
							{/* Header */}
							<div className="flex items-start sm:items-center gap-4 mb-6">
								<div className="w-10 h-10 sm:w-12 sm:h-12 rounded-full bg-white/5 flex items-center justify-center flex-shrink-0">
									{platformData?.icon}
								</div>
								<div className="min-w-0 flex-1">
									<h3 className="text-lg sm:text-xl font-semibold text-white truncate">Connect to {platform}</h3>
									<p className="text-sm text-white/60 mt-0.5">
										{isTelegram
											? "We'll allocate a dedicated bot for your campaign"
											: `You'll be redirected to ${platform} to complete the connection`}
									</p>
								</div>
							</div>

							{/* Content */}
							<div className="space-y-4 sm:space-y-6">
								{isTelegram ? (
									<div>
										<h4 className="text-sm font-medium text-white/80 mb-3">How it works</h4>
										<p className="text-sm text-white/60 mb-4">{platformData.description}</p>
										<div className="space-y-2">
											{platformData.steps.map((step, index) => (
												<div key={index} className="flex items-start gap-2 text-white/60 text-sm">
													<div className="w-5 h-5 rounded-full bg-[#0088cc]/20 flex items-center justify-center flex-shrink-0 mt-0.5">
														<span className="text-[#0088cc] text-xs font-medium">{index + 1}</span>
													</div>
													<span>{step}</span>
												</div>
											))}
										</div>
									</div>
								) : (
									<div>
										<h4 className="text-sm font-medium text-white/80 mb-3">Required Permissions</h4>
										<div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
											{platformData?.permissions.map((permission, index) => (
												<div key={index} className="flex items-center gap-2 text-white/60 text-sm">
													<svg
														className="w-4 h-4 text-[#007AFF] flex-shrink-0"
														fill="none"
														viewBox="0 0 24 24"
														stroke="currentColor"
													>
														<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
													</svg>
													<span className="truncate">{permission}</span>
												</div>
											))}
										</div>
									</div>
								)}

								<div className="bg-[#007AFF]/10 border border-[#007AFF]/20 rounded-xl p-3 sm:p-4">
									<div className="flex gap-3">
										<div className="flex-shrink-0">
											<svg className="w-5 h-5 text-[#007AFF]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
												<path
													strokeLinecap="round"
													strokeLinejoin="round"
													strokeWidth={2}
													d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
												/>
											</svg>
										</div>
										<div className="flex-1 min-w-0">
											<p className="text-sm text-[#007AFF]">
												{isTelegram
													? "Our bots are secure and follow Telegram's guidelines. They only require message sending permissions to function properly."
													: "Your data is secure with us. We follow strict security protocols and only request permissions that are necessary for the campaign's functionality."}
											</p>
										</div>
									</div>
								</div>
							</div>

							{/* Actions */}
							<div className="flex flex-col-reverse sm:flex-row gap-2 sm:gap-3 mt-6 sm:mt-8">
								<button
									onClick={onClose}
									disabled={isPending}
									className="flex-1 px-4 py-2.5 rounded-xl text-sm font-medium text-white bg-white/10 hover:bg-white/20 transition-colors"
								>
									Cancel
								</button>
								<button
									onClick={handleConnect(platform.toLowerCase())}
									disabled={isPending}
									className="flex-1 px-4 py-2.5 rounded-xl text-sm font-medium text-white bg-[#007AFF] hover:bg-[#0056b3] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
								>
									{isPending ? "Connecting..." : "Connect"}
								</button>
							</div>
						</div>
					</motion.div>
				</div>
			)}
		</AnimatePresence>
	);
};

export default PlatformConnectDialog;
