import useSnack from "../../hooks/useSnack";
import { useEffect, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import ConfirmDialog from "@/components/common/ConfirmDialog";

const CampaignPlatforms = ({
	campaign,
	handleConnectPlatform,
	platformConnectionStatus,
	disconnectPlatformMutation,
}) => {
	const [isConfirmDialogOpen, setIsConfirmDialogOpen] = useState(false);
	const [platformToDisconnect, setPlatformToDisconnect] = useState(null);

	const snack = useSnack();
	const queryClient = useQueryClient();
	const {
		mutate: disconnectPlatform,
		isPending: isDisconnecting,
		isError: isDisconnectError,
		isSuccess: isDisconnectSuccess,
		reset: resetDisconnect,
		error: disconnectError,
	} = disconnectPlatformMutation;

	useEffect(() => {
		if (isDisconnectError) {
			snack.error(disconnectError.message || "Failed to disconnect platform");
			resetDisconnect();
			setPlatformToDisconnect(null);
		}
		if (isDisconnectSuccess) {
			snack.success("Platform disconnected successfully");
			queryClient.invalidateQueries({ queryKey: ["campaign", campaign.id] });
			queryClient.invalidateQueries({ queryKey: ["campaign-connection-status", campaign.id] });
			setPlatformToDisconnect(null);
		}
	}, [isDisconnectError, isDisconnectSuccess, disconnectError]);

	const handleDisconnectPlatform = (platform) => {
		console.log(platform);
		setIsConfirmDialogOpen(false);
		setPlatformToDisconnect(platform);
		disconnectPlatform({ platform });
	};

	return (
		<div className="space-y-8">
			{/* Platform Authentication */}
			<div className="bg-white/5 rounded-xl p-6">
				<h3 className="text-lg font-medium text-white mb-6">Platform Authentication</h3>
				<div className="space-y-6">
					{[
						{
							id: "twitter",
							name: "Twitter",
							icon: "twitter",
							description: "Connect your Twitter account to enable automated posting and engagement",
						},
						{
							id: "telegram",
							name: "Telegram",
							icon: "telegram",
							description: "Link your Telegram bot to your campaign for automated shilling in your channels and groups",
						},
						{
							id: "discord",
							name: "Discord",
							icon: "discord",
							description: "Integrate with your Discord bot for automated shilling in your channels",
							disabled: true,
						},
					].map((platform) => (
						<div
							key={platform.id}
							className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 bg-white/5 rounded-xl"
						>
							<div className="flex items-center gap-4">
								<div className="hidden sm:flex w-10 h-10 rounded-full bg-white/5 items-center justify-center">
									{platform.icon === "twitter" ? (
										<svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
											<path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
										</svg>
									) : platform.icon === "telegram" ? (
										<svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
											<path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69a.2.2 0 00-.05-.18c-.06-.05-.14-.03-.21-.02-.09.02-1.49.95-4.22 2.79-.4.27-.76.41-1.08.4-.36-.01-1.04-.2-1.55-.37-.63-.2-1.12-.31-1.08-.66.02-.18.27-.36.74-.55 2.92-1.27 4.86-2.11 5.83-2.51 2.78-1.16 3.35-1.36 3.73-1.36.08 0 .27.02.39.12.1.08.13.19.14.27-.01.06.01.24 0 .24z" />
										</svg>
									) : (
										<svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
											<path d="M20.317 4.492c-1.53-.69-3.17-1.2-4.885-1.49a.075.075 0 00-.079.036c-.21.369-.444.85-.608 1.23a18.566 18.566 0 00-5.487 0 12.36 12.36 0 00-.617-1.23A.077.077 0 008.562 3c-1.714.29-3.354.8-4.885 1.491a.07.07 0 00-.032.027C.533 9.093-.32 13.555.099 17.961a.08.08 0 00.031.055 20.03 20.03 0 005.993 2.98.078.078 0 00.084-.026 13.83 13.83 0 001.226-1.963.074.074 0 00-.041-.104 13.201 13.201 0 01-1.872-.878.075.075 0 01-.008-.125c.126-.093.252-.19.372-.287a.075.075 0 01.078-.01c3.927 1.764 8.18 1.764 12.061 0a.075.075 0 01.079.009c.12.098.245.195.372.288a.075.075 0 01-.006.125c-.598.344-1.22.635-1.873.877a.075.075 0 00-.041.105c.36.687.772 1.341 1.225 1.962a.077.077 0 00.084.028 19.963 19.963 0 006.002-2.981.076.076 0 00.032-.054c.5-5.094-.838-9.52-3.549-13.442a.06.06 0 00-.031-.028z" />
										</svg>
									)}
								</div>
								<div className="sm:hidden">
									{platform.icon === "twitter" ? (
										<svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
											<path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
										</svg>
									) : platform.icon === "telegram" ? (
										<svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
											<path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69a.2.2 0 00-.05-.18c-.06-.05-.14-.03-.21-.02-.09.02-1.49.95-4.22 2.79-.4.27-.76.41-1.08.4-.36-.01-1.04-.2-1.55-.37-.63-.2-1.12-.31-1.08-.66.02-.18.27-.36.74-.55 2.92-1.27 4.86-2.11 5.83-2.51 2.78-1.16 3.35-1.36 3.73-1.36.08 0 .27.02.39.12.1.08.13.19.14.27-.01.06.01.24 0 .24z" />
										</svg>
									) : (
										<svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
											<path d="M20.317 4.492c-1.53-.69-3.17-1.2-4.885-1.49a.075.075 0 00-.079.036c-.21.369-.444.85-.608 1.23a18.566 18.566 0 00-5.487 0 12.36 12.36 0 00-.617-1.23A.077.077 0 008.562 3c-1.714.29-3.354.8-4.885 1.491a.07.07 0 00-.032.027C.533 9.093-.32 13.555.099 17.961a.08.08 0 00.031.055 20.03 20.03 0 005.993 2.98.078.078 0 00.084-.026 13.83 13.83 0 001.226-1.963.074.074 0 00-.041-.104 13.201 13.201 0 01-1.872-.878.075.075 0 01-.008-.125c.126-.093.252-.19.372-.287a.075.075 0 01.078-.01c3.927 1.764 8.18 1.764 12.061 0a.075.075 0 01.079.009c.12.098.245.195.372.288a.075.075 0 01-.006.125c-.598.344-1.22.635-1.873.877a.075.075 0 00-.041.105c.36.687.772 1.341 1.225 1.962a.077.077 0 00.084.028 19.963 19.963 0 006.002-2.981.076.076 0 00.032-.054c.5-5.094-.838-9.52-3.549-13.442a.06.06 0 00-.031-.028z" />
										</svg>
									)}
								</div>
								<div>
									<h4 className="text-white font-medium">{platform.name} </h4>
									<p className="mt-1 text-sm text-white/60">{platform.description}</p>
								</div>
							</div>
							{platform.disabled ? (
								<span className="inline-block mt-2 sm:mt-0 sm:ml-2 text-xs font-medium px-2 py-1 sm:px-1.5 sm:py-0.5 rounded-full bg-yellow-500/10 text-yellow-400 border border-yellow-500/20 w-fit">
									Coming Soon
								</span>
							) : platformConnectionStatus && platformConnectionStatus[platform.id.toLowerCase()]?.isConnected ? (
								<>
									<button
										disabled={isDisconnecting && platformToDisconnect === platform.id}
										onClick={() => setIsConfirmDialogOpen(true)}
										className="px-4 py-2 rounded-xl text-sm font-medium bg-white/10 text-white hover:bg-white/20 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
									>
										{isDisconnecting && platformToDisconnect === platform.id ? (
											<div className="flex items-center gap-2">
												<svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
													<circle
														className="opacity-25"
														cx="12"
														cy="12"
														r="10"
														stroke="currentColor"
														strokeWidth="4"
													></circle>
													<path
														className="opacity-75"
														fill="currentColor"
														d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
													></path>
												</svg>
												Disconnecting...
											</div>
										) : (
											<>Disconnect {platform.name}</>
										)}
									</button>

									<ConfirmDialog
										isOpen={isConfirmDialogOpen}
										onClose={() => setIsConfirmDialogOpen(false)}
										onConfirm={() => handleDisconnectPlatform(platform.id)}
										title="Disconnect Platform"
										message={`Are you sure you want to disconnect ${platform.name}? You will no longer be able to use this platform to post to your campaign.`}
									/>
								</>
							) : (
								<button
									onClick={() => handleConnectPlatform(platform.name)}
									className="px-4 py-2 rounded-xl text-sm font-medium bg-[#007AFF] text-white hover:bg-[#0056b3] transition-colors"
								>
									Connect {platform.name}
								</button>
							)}
						</div>
					))}
				</div>
			</div>
		</div>
	);
};

export default CampaignPlatforms;
