import { useState } from "react";
import { motion } from "framer-motion";
import { Formik, Form, Field } from "formik";
import * as Yup from "yup";

const CustomSelect = ({ field, form, options, label, ...props }) => (
	<div className="relative">
		<label className="block text-sm font-medium text-white/80 mb-2">{label}</label>
		<div className="relative">
			<select
				{...field}
				{...props}
				className="block w-full rounded-xl bg-white/5 border border-white/10 px-4 py-3 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-[#007AFF]/50 focus:border-transparent transition-all appearance-none"
			>
				{options.map((option) => (
					<option key={option.value} value={option.value} className="bg-[#1a1a1a] text-white">
						{option.label}
					</option>
				))}
			</select>
			<div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-white/40">
				<svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
				</svg>
			</div>
		</div>
	</div>
);

const CustomCheckboxGroup = ({ field, form, options, label, ...props }) => (
	<div>
		<label className="block text-sm font-medium text-white/80 mb-2">{label}</label>
		<div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
			{options.map((option) => (
				<label
					key={option.value}
					className="relative flex items-start p-4 rounded-xl bg-white/5 border border-white/10 hover:bg-white/[0.07] transition-colors cursor-pointer group"
				>
					<div className="flex items-center h-5">
						<input
							type="checkbox"
							checked={field.value.includes(option.value)}
							onChange={(e) => {
								const set = new Set(field.value);
								if (e.target.checked) {
									set.add(option.value);
								} else {
									set.delete(option.value);
								}
								form.setFieldValue(field.name, Array.from(set));
							}}
							className="h-4 w-4 rounded border-white/20 bg-white/5 text-[#007AFF] focus:ring-[#007AFF]/50 focus:ring-offset-0"
						/>
					</div>
					<div className="ml-3">
						<span className="block text-sm font-medium text-white group-hover:text-[#007AFF] transition-colors">
							{option.label}
						</span>
						{option.description && (
							<span className="block text-xs text-white/40 group-hover:text-white/60 transition-colors">
								{option.description}
							</span>
						)}
					</div>
				</label>
			))}
		</div>
	</div>
);

const campaignTypes = [
	{ value: "meme", label: "Meme Shilling" },
	{ value: "token", label: "Token Launch Shilling" },
	{ value: "price", label: "Price Action Shilling" },
	{ value: "community", label: "Community Growth" },
	{ value: "partnership", label: "Partnership Shilling" },
	{ value: "custom", label: "Custom Shilling" },
];

const platforms = [
	{ value: "twitter", label: "X (Twitter)", description: "Automated shilling on X with trending topics" },
	{ value: "telegram", label: "Telegram", description: "Group and channel engagement" },
	{ value: "discord", label: "Discord", description: "Server-wide automated presence" },
];

const engagementStyles = [
	{ value: "aggressive", label: "Aggressive (High Frequency)" },
	{ value: "standard", label: "Standard (Moderate)" },
	{ value: "passive", label: "Passive (Low Frequency)" },
];

const targetAudiences = [
	{ value: "traders", label: "Active Traders", description: "Day traders and swing traders" },
	{ value: "investors", label: "Long-term Investors", description: "HODLers and value investors" },
	{ value: "degens", label: "DeFi Enthusiasts", description: "Yield farmers and DeFi users" },
	{ value: "influencers", label: "Crypto Influencers", description: "KOLs and community leaders" },
];

const goals = [
	{ value: "awareness", label: "Brand Awareness", description: "Increase project visibility" },
	{ value: "engagement", label: "Community Engagement", description: "Boost interaction and discussions" },
	{ value: "holders", label: "Increase Holders", description: "Attract new token holders" },
	{ value: "volume", label: "Trading Volume", description: "Boost market activity" },
];

const timelines = [
	{ value: "1week", label: "1 Week Campaign" },
	{ value: "2weeks", label: "2 Weeks Campaign" },
	{ value: "1month", label: "1 Month Campaign" },
	{ value: "3months", label: "3 Months Campaign" },
	{ value: "custom", label: "Custom Timeline" },
];

const validationSchema = Yup.object().shape({
	name: Yup.string().required("Campaign name is required"),
	type: Yup.string().required("Campaign type is required"),
	platforms: Yup.array().min(1, "Select at least one platform"),
	engagementStyle: Yup.string().required("Engagement style is required"),
	projectInfo: Yup.string().required("Project information is required"),
	targetAudience: Yup.array().min(1, "Select at least one target audience"),
	goals: Yup.array().min(1, "Select at least one goal"),
	timeline: Yup.string().required("Timeline is required"),
	startDate: Yup.date().required("Start date is required").min(new Date(), "Start date must be in the future"),
	website: Yup.string().url("Must be a valid URL").nullable(),
	twitterHandle: Yup.string().nullable(),
	telegramGroup: Yup.string().nullable(),
	discordServer: Yup.string().nullable(),
});

const CampaignForm = ({ onSubmit, onCancel }) => {
	const initialValues = {
		name: "",
		type: "",
		platforms: [],
		engagementStyle: "",
		projectInfo: "",
		targetAudience: [],
		goals: [],
		timeline: "",
		startDate: "",
		website: "",
		twitterHandle: "",
		telegramGroup: "",
		discordServer: "",
	};

	return (
		<motion.div
			initial={{ opacity: 0 }}
			animate={{ opacity: 1 }}
			exit={{ opacity: 0 }}
			className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-start justify-center overflow-y-auto py-8"
		>
			<motion.div
				initial={{ scale: 0.95, opacity: 0 }}
				animate={{ scale: 1, opacity: 1 }}
				exit={{ scale: 0.95, opacity: 0 }}
				className="relative bg-[#0a0a0a] border border-white/10 rounded-2xl w-full max-w-4xl mx-4"
			>
				<div className="bg-[#0a0a0a] rounded-t-2xl p-6 border-b border-white/10">
					<div className="flex items-start justify-between">
						<div>
							<h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-[#007AFF] to-[#00C6FF]">
								Configure AI Shilling Campaign
							</h2>
							<p className="mt-1 text-white/60">Set up your automated crypto marketing campaign</p>
						</div>
						<button
							onClick={onCancel}
							className="rounded-lg p-2 text-white/40 hover:text-white hover:bg-white/5 transition-colors"
							aria-label="Close modal"
						>
							<svg className="w-5 h-5" viewBox="0 0 20 20" fill="currentColor">
								<path
									fillRule="evenodd"
									d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
									clipRule="evenodd"
								/>
							</svg>
						</button>
					</div>
				</div>

				<Formik
					initialValues={initialValues}
					validationSchema={validationSchema}
					onSubmit={async (values, { setSubmitting }) => {
						await onSubmit(values);
						setSubmitting(false);
					}}
				>
					{({ isSubmitting, errors, touched }) => (
						<Form className="p-6 space-y-6">
							{/* Campaign Name */}
							<div>
								<label htmlFor="name" className="block text-sm font-medium text-white/80 mb-2">
									Campaign Name
								</label>
								<Field
									type="text"
									name="name"
									placeholder="Enter a memorable name for your campaign"
									className="block w-full rounded-xl bg-white/5 border border-white/10 px-4 py-3 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-[#007AFF]/50 focus:border-transparent transition-all"
								/>
								{errors.name && touched.name && <div className="mt-1 text-sm text-red-500">{errors.name}</div>}
							</div>

							{/* Campaign Type */}
							<Field name="type" component={CustomSelect} options={campaignTypes} label="Campaign Type" />

							{/* Platforms */}
							<Field name="platforms" component={CustomCheckboxGroup} options={platforms} label="Target Platforms" />

							{/* Engagement Style */}
							<Field
								name="engagementStyle"
								component={CustomSelect}
								options={engagementStyles}
								label="Engagement Style"
							/>

							{/* Project Information */}
							<div>
								<label htmlFor="projectInfo" className="block text-sm font-medium text-white/80 mb-2">
									Project Information
								</label>
								<Field
									as="textarea"
									name="projectInfo"
									rows={4}
									placeholder="Describe your project, including tokenomics, key features, and unique selling points"
									className="block w-full rounded-xl bg-white/5 border border-white/10 px-4 py-3 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-[#007AFF]/50 focus:border-transparent transition-all resize-none"
								/>
							</div>

							{/* Target Audience */}
							<Field
								name="targetAudience"
								component={CustomCheckboxGroup}
								options={targetAudiences}
								label="Target Audience"
							/>

							{/* Campaign Goals */}
							<Field name="goals" component={CustomCheckboxGroup} options={goals} label="Campaign Goals" />

							{/* Timeline */}
							<Field name="timeline" component={CustomSelect} options={timelines} label="Campaign Timeline" />

							{/* Start Date */}
							<div>
								<label htmlFor="startDate" className="block text-sm font-medium text-white/80 mb-2">
									Campaign Start Date
								</label>
								<Field
									type="datetime-local"
									name="startDate"
									min={new Date().toISOString().split(".")[0]}
									className="block w-full rounded-xl bg-white/5 border border-white/10 px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-[#007AFF]/50 focus:border-transparent transition-all"
								/>
								{errors.startDate && touched.startDate && (
									<div className="mt-1 text-sm text-red-500">{errors.startDate}</div>
								)}
							</div>

							{/* Project Website */}
							<div>
								<label htmlFor="website" className="block text-sm font-medium text-white/80 mb-2">
									Project Website (Optional)
								</label>
								<Field
									type="url"
									name="website"
									placeholder="https://your-project.com"
									className="block w-full rounded-xl bg-white/5 border border-white/10 px-4 py-3 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-[#007AFF]/50 focus:border-transparent transition-all"
								/>
								{errors.website && touched.website && <div className="mt-1 text-sm text-red-500">{errors.website}</div>}
							</div>

							{/* Project Socials */}
							<div className="grid grid-cols-1 md:grid-cols-3 gap-4">
								<div>
									<label htmlFor="twitterHandle" className="block text-sm font-medium text-white/80 mb-2">
										Twitter Handle (Optional)
									</label>
									<div className="relative">
										<span className="absolute inset-y-0 left-0 pl-4 flex items-center text-white/40">@</span>
										<Field
											type="text"
											name="twitterHandle"
											placeholder="username"
											className="block w-full rounded-xl bg-white/5 border border-white/10 pl-8 pr-4 py-3 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-[#007AFF]/50 focus:border-transparent transition-all"
										/>
									</div>
								</div>

								<div>
									<label htmlFor="telegramGroup" className="block text-sm font-medium text-white/80 mb-2">
										Telegram Group (Optional)
									</label>
									<div className="relative">
										<span className="absolute inset-y-0 left-0 pl-4 flex items-center text-white/40">t.me/</span>
										<Field
											type="text"
											name="telegramGroup"
											placeholder="groupname"
											className="block w-full rounded-xl bg-white/5 border border-white/10 pl-16 pr-4 py-3 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-[#007AFF]/50 focus:border-transparent transition-all"
										/>
									</div>
								</div>

								<div>
									<label htmlFor="discordServer" className="block text-sm font-medium text-white/80 mb-2">
										Discord Server (Optional)
									</label>
									<div className="relative">
										<span className="absolute inset-y-0 left-0 pl-4 flex items-center text-white/40">discord.gg/</span>
										<Field
											type="text"
											name="discordServer"
											placeholder="invite-code"
											className="block w-full rounded-xl bg-white/5 border border-white/10 pl-24 pr-4 py-3 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-[#007AFF]/50 focus:border-transparent transition-all"
										/>
									</div>
								</div>
							</div>

							<div className="flex items-center justify-end gap-4 pt-6 border-t border-white/10">
								<button
									type="button"
									onClick={onCancel}
									className="px-6 py-3 text-sm font-medium text-white/60 hover:text-white transition-colors"
								>
									Cancel
								</button>
								<button
									type="submit"
									disabled={isSubmitting}
									className="rounded-xl bg-gradient-to-r from-[#007AFF] to-[#00C6FF] px-6 py-3 text-sm font-semibold text-white shadow-lg hover:shadow-[#007AFF]/20 hover:from-[#0056b3] hover:to-[#00A6FF] transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
								>
									{isSubmitting ? "Creating..." : "Create Campaign"}
								</button>
							</div>
						</Form>
					)}
				</Formik>
			</motion.div>
		</motion.div>
	);
};

export default CampaignForm;
