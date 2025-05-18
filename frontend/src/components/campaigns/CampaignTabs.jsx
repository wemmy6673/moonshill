const TABS = [
	{ id: "overview", label: "Overview" },
	{ id: "project-info", label: "Project Info" },
	{ id: "platforms", label: "Platforms" },
	{ id: "settings", label: "Settings" },
	{ id: "analytics", label: "Analytics" },
];

const CampaignTabs = ({ activeTab, setActiveTab }) => {
	return (
		<div className="border-b border-white/10 mb-8">
			<nav className="flex gap-6 -mb-px overflow-x-auto">
				{TABS.map((tab) => (
					<button
						key={tab.id}
						data-tab={tab.id}
						onClick={() => setActiveTab(tab.id)}
						className={`py-4 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
							activeTab === tab.id
								? "border-[#007AFF] text-[#007AFF]"
								: "border-transparent text-white/60 hover:text-white/80 hover:border-white/20"
						}`}
					>
						{tab.label}
					</button>
				))}
			</nav>
		</div>
	);
};

export default CampaignTabs;
