const CampaignStatus = ({ campaign, handleToggleStatus, setActiveTab }) => {
	return (
		<div className="bg-white/5 rounded-xl p-4 sm:p-6 mb-8">
			<div className="flex flex-col gap-6">
				{/* Status Section */}
				<div className="flex items-center gap-4 p-4 bg-white/5 rounded-xl">
					<div className="flex items-center gap-3">
						<div
							className={`w-3 h-3 rounded-full ${
								campaign.status === "RUNNING"
									? "bg-green-500 shadow-lg shadow-green-500/30"
									: "bg-yellow-500 shadow-lg shadow-yellow-500/30"
							}`}
						></div>
						<div>
							<div className="text-sm font-medium text-white/80">Status</div>
							<div className="text-lg font-semibold text-white">
								{campaign.status === "RUNNING" ? "Campaign Active" : "Campaign Paused"}
							</div>
						</div>
					</div>
					<button
						onClick={handleToggleStatus}
						className={`ml-auto px-6 h-11 rounded-xl text-sm font-medium transition-all ${
							campaign.status === "RUNNING"
								? "bg-gradient-to-r from-yellow-500 to-yellow-600 text-white hover:opacity-90"
								: "bg-gradient-to-r from-green-500 to-green-600 text-white hover:opacity-90"
						}`}
					>
						{campaign.status === "RUNNING" ? "Pause Campaign" : "Activate Campaign"}
					</button>
				</div>

				{/* Action Buttons */}
				<div className="flex flex-col sm:flex-row gap-3">
					<button
						onClick={() => {
							setActiveTab("project-info");
							document.querySelector('[data-tab="project-info"]')?.scrollIntoView({
								behavior: "smooth",
								block: "start",
							});
						}}
						disabled={campaign.completionPercentage === 100}
						className={`flex items-center justify-center gap-2 h-11 px-6 rounded-xl text-white transition-all sm:flex-1 ${
							campaign.completionPercentage === 100
								? "bg-green-500/20 cursor-not-allowed"
								: "bg-[#007AFF] hover:opacity-90"
						}`}
					>
						<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path
								strokeLinecap="round"
								strokeLinejoin="round"
								strokeWidth={2}
								d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
							/>
						</svg>
						{campaign.completionPercentage === 100 ? (
							"Project Info Complete"
						) : (
							<>
								Complete Project Info
								<span className="ml-1 px-1.5 py-0.5 text-xs bg-white/10 rounded">{campaign.completionPercentage}%</span>
							</>
						)}
					</button>
					<button
						onClick={() => {
							setActiveTab("platforms");
							document.querySelector('[data-tab="platforms"]')?.scrollIntoView({
								behavior: "smooth",
								block: "start",
							});
						}}
						className="flex items-center justify-center gap-2 h-11 px-6 rounded-xl border border-white/10 bg-white/5 text-white hover:bg-white/10 transition-all sm:flex-1"
					>
						<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
						</svg>
						Connect Platforms
					</button>
				</div>
			</div>
		</div>
	);
};

export default CampaignStatus;
