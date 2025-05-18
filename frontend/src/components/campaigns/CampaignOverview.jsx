const CampaignOverview = ({ campaign }) => {
	return (
		<div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
			{/* Main Content */}
			<div className="lg:col-span-2 space-y-8">
				{/* Project Details */}
				<div className="bg-white/5 rounded-xl p-6">
					<h3 className="text-lg font-medium text-white mb-4">Project Details</h3>
					<div className="space-y-4">
						<div>
							<div className="text-sm text-white/40">Project Name</div>
							<div className="mt-1 text-white">{campaign.projectName}</div>
						</div>

						{campaign.projectWebsite && (
							<div>
								<div className="text-sm text-white/40">Website</div>
								<div className="mt-1 break-all">
									<a
										href={campaign.projectWebsite}
										target="_blank"
										rel="noopener noreferrer"
										className="text-[#007AFF] hover:text-[#00C6FF] transition-colors inline-block max-w-full overflow-hidden text-ellipsis"
									>
										{campaign.projectWebsite}
									</a>
								</div>
							</div>
						)}

						<div>
							<div className="text-sm text-white/40">Description</div>
							{campaign.projectInfo && (
								<div className="relative">
									<div
										className={`mt-1 text-white whitespace-pre-wrap ${
											campaign.projectInfo.length > 300 ? "line-clamp-10" : ""
										}`}
									>
										{campaign.projectInfo}
									</div>
									{campaign.projectInfo.length > 300 && (
										<button
											onClick={(event) => {
												const element = event.target.previousElementSibling;
												if (element.classList.contains("line-clamp-10")) {
													element.classList.remove("line-clamp-10");
													event.target.textContent = "Show less";
												} else {
													element.classList.add("line-clamp-10");
													event.target.textContent = "See more";
												}
											}}
											className="mt-1 text-sm text-[#007AFF] hover:text-[#0056b3] transition-colors"
										>
											See more
										</button>
									)}
								</div>
							)}
						</div>
					</div>
				</div>

				{/* Campaign Activity */}
				<div className="bg-white/5 rounded-xl p-6">
					<h3 className="text-lg font-medium text-white mb-4">Recent Activity</h3>
					<div className="space-y-4">
						{!campaign.activities?.length && <div className="mt-2 text-sm text-white/60">No activities yet</div>}
						{campaign.activities?.map((activity) => (
							<div key={activity.id} className="flex items-start gap-4 p-4 bg-white/5 rounded-xl">
								<div className="flex-shrink-0">
									<div className="w-8 h-8 rounded-full bg-[#007AFF]/10 flex items-center justify-center">
										<svg className="w-4 h-4 text-[#007AFF]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
											<path
												strokeLinecap="round"
												strokeLinejoin="round"
												strokeWidth={2}
												d="M13 10V3L4 14h7v7l9-11h-7z"
											/>
										</svg>
									</div>
								</div>
								<div>
									<div className="font-medium text-white">{activity.type}</div>
									<div className="mt-1 text-sm text-white/60">{activity.description}</div>
									<div className="mt-2 text-xs text-white/40">{new Date(activity.timestamp).toLocaleString()}</div>
								</div>
							</div>
						))}
					</div>
				</div>
			</div>

			{/* Sidebar */}
			<div className="space-y-8">
				{/* Target Platforms */}
				<div className="bg-white/5 rounded-xl p-6">
					<h3 className="text-lg font-medium text-white mb-4">Target Platforms</h3>
					<div className="space-y-4">
						{campaign.targetPlatforms.map((platform, index) => (
							<div key={index} className="flex items-center justify-between">
								<div className="flex items-center gap-3">
									<div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center">
										{platform === "Twitter" ? (
											<svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
												<path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
											</svg>
										) : platform === "Telegram" ? (
											<svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
												<path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69a.2.2 0 00-.05-.18c-.06-.05-.14-.03-.21-.02-.09.02-1.49.95-4.22 2.79-.4.27-.76.41-1.08.4-.36-.01-1.04-.2-1.55-.37-.63-.2-1.12-.31-1.08-.66.02-.18.27-.36.74-.55 2.92-1.27 4.86-2.11 5.83-2.51 2.78-1.16 3.35-1.36 3.73-1.36.08 0 .27.02.39.12.1.08.13.19.14.27-.01.06.01.24 0 .24z" />
											</svg>
										) : platform === "Discord" ? (
											<svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
												<path d="M20.317 4.492c-1.53-.69-3.17-1.2-4.885-1.49a.075.075 0 00-.079.036c-.21.369-.444.85-.608 1.23a18.566 18.566 0 00-5.487 0 12.36 12.36 0 00-.617-1.23A.077.077 0 008.562 3c-1.714.29-3.354.8-4.885 1.491a.07.07 0 00-.032.027C.533 9.093-.32 13.555.099 17.961a.08.08 0 00.031.055 20.03 20.03 0 005.993 2.98.078.078 0 00.084-.026 13.83 13.83 0 001.226-1.963.074.074 0 00-.041-.104 13.201 13.201 0 01-1.872-.878.075.075 0 01-.008-.125c.126-.093.252-.19.372-.287a.075.075 0 01.078-.01c3.927 1.764 8.18 1.764 12.061 0a.075.075 0 01.079.009c.12.098.245.195.372.288a.075.075 0 01-.006.125c-.598.344-1.22.635-1.873.877a.075.075 0 00-.041.105c.36.687.772 1.341 1.225 1.962a.077.077 0 00.084.028 19.963 19.963 0 006.002-2.981.076.076 0 00.032-.054c.5-5.094-.838-9.52-3.549-13.442a.06.06 0 00-.031-.028z" />
											</svg>
										) : null}
									</div>
									<div className="text-white">{platform}</div>
								</div>
								<div className="flex items-center gap-2">
									{campaign.connectedPlatforms?.includes(platform) ? (
										<div className="flex items-center gap-2">
											<svg className="w-5 h-5 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
												<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
											</svg>
											<span className="text-green-500 text-sm">Connected</span>
										</div>
									) : (
										<div className="flex items-center gap-2">
											<svg className="w-5 h-5 text-white/40" fill="none" viewBox="0 0 24 24" stroke="currentColor">
												<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
											</svg>
											<span className="text-white/40 text-sm">Not Connected</span>
										</div>
									)}
								</div>
							</div>
						))}
					</div>
				</div>

				{/* Campaign Settings */}
				<div className="bg-white/5 rounded-xl p-6">
					<h3 className="text-lg font-medium text-white mb-4">Campaign Details</h3>
					<div className="space-y-4">
						<div>
							<div className="text-sm text-white/40">Target Audience</div>
							<div className="mt-1 text-white">{campaign.targetAudience.join(", ")}</div>
						</div>
						<div>
							<div className="text-sm text-white/40">Goals</div>
							<div className="mt-1 text-white">{campaign.campaignGoals.join(", ")}</div>
						</div>
						<div>
							<div className="text-sm text-white/40">Start Date</div>
							<div className="mt-1 text-white">{new Date(campaign.campaignStartDate).toLocaleDateString()}</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	);
};

export default CampaignOverview;
