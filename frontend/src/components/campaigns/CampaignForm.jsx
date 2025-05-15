import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Formik, Form, Field } from "formik";
import * as Yup from "yup";
import { createFetcher } from "@/libs/fetcher";
import config from "../../libs/config";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import useSnack from "@/hooks/useSnack";

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

const CustomCheckboxGroup = ({ field, form, options, label }) => (
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
		{form.touched[field.name] && form.errors[field.name] && (
			<div className="mt-2 text-sm text-red-500">{form.errors[field.name]}</div>
		)}
	</div>
);

const campaignTypes = [
	{ value: "Meme Shilling", label: "Meme Shilling" },
	{ value: "Token Launch", label: "Token Launch" },
	{ value: "Price Action", label: "Price Action" },
	{ value: "Community Growth", label: "Community Growth" },
	{ value: "Partnership Shilling", label: "Partnership Shilling" },
	{ value: "Custom Shilling", label: "Custom Shilling" },
];

const platforms = [
	{ value: "Twitter", label: "X (Twitter)", description: "Automated shilling on X with trending topics" },
	{ value: "Telegram", label: "Telegram", description: "Group and channel engagement" },
	{ value: "Discord", label: "Discord", description: "Server-wide automated presence" },
];

const engagementStyles = [
	{ value: "Standard", label: "Standard (Moderate)" },
	{ value: "Aggressive", label: "Aggressive (High Frequency)" },
	{ value: "Passive", label: "Passive (Low Frequency)" },
];

const targetAudiences = [
	{ value: "Active Traders", label: "Active Traders", description: "Day traders and swing traders" },
	{ value: "Long-Term Investors", label: "Long-Term Investors", description: "HODLers and value investors" },
	{ value: "DeFi Enthusiasts", label: "DeFi Enthusiasts", description: "Yield farmers and DeFi users" },
	{ value: "Crypto Influencers", label: "Crypto Influencers", description: "KOLs and community leaders" },
];

const goals = [
	{ value: "Brand Awareness", label: "Brand Awareness", description: "Increase project visibility" },
	{ value: "Community Engagement", label: "Community Engagement", description: "Boost interaction and discussions" },
	{ value: "Increase Holders", label: "Increase Holders", description: "Attract new token holders" },
	{ value: "Trading Volume", label: "Trading Volume", description: "Boost market activity" },
];

const timelines = [
	{ value: "1 Week", label: "1 Week Campaign" },
	{ value: "2 Weeks", label: "2 Weeks Campaign" },
	{ value: "1 Month", label: "1 Month Campaign" },
	{ value: "2 Months", label: "2 Months Campaign" },
	{ value: "3 Months", label: "3 Months Campaign" },
	{ value: "6 Months", label: "6 Months Campaign" },
	{ value: "1 Year", label: "1 Year Campaign" },
];

// Split validation schema into steps
const step1ValidationSchema = Yup.object().shape({
	name: Yup.string().required("Campaign name is required"),
	type: Yup.string().required("Campaign type is required"),
	platforms: Yup.array()
		.min(1, "Select at least one platform for your campaign")
		.required("Select at least one platform"),
	engagementStyle: Yup.string().required("Engagement style is required"),
	startDate: Yup.date().required("Start date is required").min(new Date(), "Start date must be in the future"),
	timeline: Yup.string().required("Timeline is required"),
});

const step2ValidationSchema = Yup.object().shape({
	projectName: Yup.string().required("Project name is required"),
	projectInfo: Yup.string().required("Project information is required"),
	targetAudience: Yup.array()
		.min(1, "Select at least one target audience for your campaign")
		.required("Select at least one target audience"),
	goals: Yup.array().min(1, "Select at least one goal for your campaign").required("Select at least one goal"),
	website: Yup.string().url("Must be a valid URL").nullable(),
	whitepaper: Yup.string().url("Must be a valid URL").nullable(),
	logo: Yup.string().url("Must be a valid URL").nullable(),
	banner: Yup.string().url("Must be a valid URL").nullable(),
	twitter: Yup.string().url("Must be a valid URL").nullable(),
	telegram: Yup.string().url("Must be a valid URL").nullable(),
	discord: Yup.string().url("Must be a valid URL").nullable(),
});

const CampaignForm = ({ onCancel, auth, isEditing = false, campaign, workspaceId }) => {
	const [step, setStep] = useState(1);
	const snack = useSnack();
	const queryClient = useQueryClient();

	let editModeInitialValues = {};

	if (isEditing && campaign) {
		editModeInitialValues = {
			name: campaign.campaignName,
			type: campaign.campaignType,
			platforms: campaign.targetPlatforms,
			engagementStyle: campaign.engagementStyle,
			startDate: new Date(campaign.campaignStartDate).toISOString().split("T")[0],
			timeline: campaign.campaignTimeline,
			projectName: campaign.projectName,
			projectInfo: campaign.projectInfo,
			targetAudience: campaign.targetAudience,
			goals: campaign.campaignGoals,
			website: campaign.projectWebsite,
			whitepaper: campaign.projectWhitepaper,
			logo: campaign.projectLogo,
			banner: campaign.projectBanner,
			projectTwitter: campaign.projectTwitter,
			projectTelegram: campaign.projectTelegram,
			projectDiscord: campaign.projectDiscord,
		};
	}
	const initialValues = {
		// Step 1: Campaign Setup
		name: "",
		type: "Meme Shilling",
		platforms: [],
		engagementStyle: "Standard",
		startDate: new Date(Date.now() + 86400000).toISOString().split("T")[0],
		timeline: "1 Month",

		// Step 2: Project Details
		projectName: "",
		projectInfo: "",
		targetAudience: [],
		goals: [],
		website: "",
		whitepaper: "",
		logo: "",
		banner: "",
		projectTwitter: "",
		projectTelegram: "",
		projectDiscord: "",
	};

	const renderStepIndicator = () => (
		<div className="flex items-center justify-center mb-6">
			<div className="flex items-center space-x-4">
				<div
					className={`flex items-center justify-center w-8 h-8 rounded-full border-2 ${
						step === 1 ? "border-[#007AFF] bg-[#007AFF] text-white" : "border-white/20 text-white/60"
					}`}
				>
					1
				</div>
				<div className={`w-16 h-0.5 ${step === 1 ? "bg-white/20" : "bg-[#007AFF]"}`} />
				<div
					className={`flex items-center justify-center w-8 h-8 rounded-full border-2 ${
						step === 2 ? "border-[#007AFF] bg-[#007AFF] text-white" : "border-white/20 text-white/60"
					}`}
				>
					2
				</div>
			</div>
		</div>
	);

	const renderStepTitle = () => {
		const titles = {
			1: {
				title: "Campaign Setup",
				subtitle: "Configure your campaign's basic settings",
			},
			2: {
				title: "Project Details",
				subtitle: "Tell us about your project",
			},
		};

		return (
			<div>
				<h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-[#007AFF] to-[#00C6FF]">
					{titles[step].title}
				</h2>
				<p className="mt-1 text-white/60">{titles[step].subtitle}</p>
			</div>
		);
	};

	const {
		mutate: createCampaign,
		isPending,
		reset,
		isSuccess,
		isError,
		error,
	} = useMutation({
		mutationKey: ["createCampaign"],
		mutationFn: createFetcher({
			url: config.endpoints.createCampaign,
			method: "POST",
			auth,
		}),
	});

	useEffect(() => {
		if (isSuccess) {
			snack.success("Campaign created successfully! 🚀");
			queryClient.invalidateQueries({ queryKey: ["campaigns", workspaceId] });
			reset();
			onCancel();
		}

		if (isError) {
			snack.error(error?.message || "Failed to create campaign. Please try again.");
			reset();
		}
	}, [isSuccess, isError, error, workspaceId]);

	const {
		mutate: updateCampaign,
		isPending: isUpdating,
		isSuccess: isUpdateSuccess,
		isError: isUpdateError,
		error: updateError,
	} = useMutation({
		mutationKey: ["updateCampaign"],
		mutationFn: createFetcher({
			url: `${config.endpoints.updateCampaign}/${campaign?.id}`,
			method: "PUT",
			auth,
		}),
	});

	useEffect(() => {
		if (isUpdateSuccess) {
			snack.success("Campaign updated successfully! 🚀");
			queryClient.invalidateQueries({ queryKey: ["campaigns", workspaceId] });
			queryClient.invalidateQueries({ queryKey: ["campaign", campaign?.id] });
			onCancel();
		}

		if (isUpdateError) {
			snack.error(updateError?.message || "Failed to update campaign. Please try again.");
			reset();
		}
	}, [isUpdateSuccess, isUpdateError, updateError, campaign?.id, workspaceId]);

	const handleSubmit = async (values, { setSubmitting }) => {
		if (step === 1) {
			const isValid = await step1ValidationSchema.isValid(values);
			if (isValid) {
				setStep(2);
			}
			setSubmitting(false);
		} else {
			setSubmitting(false);

			const formattedValues = {
				campaignName: values.name,
				campaignType: values.type,
				targetPlatforms: values.platforms,
				engagementStyle: values.engagementStyle,
				campaignStartDate: values.startDate,
				campaignTimeline: values.timeline,

				projectName: values.projectName,
				projectInfo: values.projectInfo,
				targetAudience: values.targetAudience,
				campaignGoals: values.goals,
				projectWebsite: values.website || undefined,
				projectWhitepaper: values.whitepaper || undefined,
				projectLogo: values.logo || undefined,
				projectBanner: values.banner || undefined,
				projectTwitter: values.projectTwitter || undefined,
				projectTelegram: values.projectTelegram || undefined,
				projectDiscord: values.projectDiscord || undefined,
			};

			if (isEditing) {
				updateCampaign(formattedValues);
			} else {
				createCampaign(formattedValues);
			}
		}
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
					<div className="flex items-start justify-between mb-6">
						{renderStepTitle()}
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
					{renderStepIndicator()}
				</div>

				<Formik
					initialValues={isEditing ? editModeInitialValues : initialValues}
					validationSchema={step === 1 ? step1ValidationSchema : step2ValidationSchema}
					onSubmit={handleSubmit}
					validateOnMount={false}
					validateOnChange={true}
					validateOnBlur={true}
				>
					{({ isSubmitting, errors, touched, isValid }) => (
						<Form className="p-6 space-y-6">
							<AnimatePresence mode="wait">
								{step === 1 ? (
									<motion.div
										key="step1"
										initial={{ opacity: 0, x: -20 }}
										animate={{ opacity: 1, x: 0 }}
										exit={{ opacity: 0, x: 20 }}
										className="space-y-6"
									>
										{/* Campaign Name */}
										<div>
											<label htmlFor="name" className="block text-sm font-medium text-white/80 mb-2">
												Campaign Name
											</label>
											<Field
												type="text"
												name="name"
												placeholder="Enter your campaign name"
												className="block w-full rounded-xl bg-white/5 border border-white/10 px-4 py-3 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-[#007AFF]/50 focus:border-transparent transition-all"
											/>
											{errors.name && touched.name && <div className="mt-1 text-sm text-red-500">{errors.name}</div>}
										</div>

										{/* Campaign Type */}
										<Field name="type" component={CustomSelect} options={campaignTypes} label="Campaign Type" />

										{/* Platforms */}
										<Field
											name="platforms"
											component={CustomCheckboxGroup}
											options={platforms}
											label="Target Platforms"
										/>

										{/* Engagement Style */}
										<Field
											name="engagementStyle"
											component={CustomSelect}
											options={engagementStyles}
											label="Engagement Style"
										/>

										{/* Start Date */}
										<div>
											<label htmlFor="startDate" className="block text-sm font-medium text-white/80 mb-2">
												Campaign Start Date
											</label>
											<Field
												type="date"
												name="startDate"
												min={new Date().toISOString().split(".")[0]}
												className="block w-full rounded-xl bg-white/5 border border-white/10 px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-[#007AFF]/50 focus:border-transparent transition-all"
											/>
											{errors.startDate && touched.startDate && (
												<div className="mt-1 text-sm text-red-500">{errors.startDate}</div>
											)}
										</div>

										{/* Timeline */}
										<Field name="timeline" component={CustomSelect} options={timelines} label="Campaign Timeline" />
									</motion.div>
								) : (
									<motion.div
										key="step2"
										initial={{ opacity: 0, x: 20 }}
										animate={{ opacity: 1, x: 0 }}
										exit={{ opacity: 0, x: -20 }}
										className="space-y-6"
									>
										{/* Project Name */}
										<div>
											<label htmlFor="projectName" className="block text-sm font-medium text-white/80 mb-2">
												Project Name
											</label>
											<Field
												type="text"
												name="projectName"
												placeholder="Enter your project name"
												className="block w-full rounded-xl bg-white/5 border border-white/10 px-4 py-3 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-[#007AFF]/50 focus:border-transparent transition-all"
											/>
											{errors.projectName && touched.projectName && (
												<div className="mt-1 text-sm text-red-500">{errors.projectName}</div>
											)}
										</div>

										{/* Project Information */}
										<div>
											<label htmlFor="projectInfo" className="block text-sm font-medium text-white/80 mb-2">
												Project Information
											</label>
											<Field
												as="textarea"
												name="projectInfo"
												rows={4}
												placeholder="Describe your project's features, tokenomics, and unique value proposition"
												className="block w-full rounded-xl bg-white/5 border border-white/10 px-4 py-3 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-[#007AFF]/50 focus:border-transparent transition-all resize-none"
											/>
											{errors.projectInfo && touched.projectInfo && (
												<div className="mt-1 text-sm text-red-500">{errors.projectInfo}</div>
											)}
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

										{/* Project Assets Section */}
										<div className="border-t border-white/10 pt-6">
											<h3 className="text-lg font-semibold text-white mb-4">Project Assets</h3>
											<div className="space-y-4">
												{/* Website URL */}
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
													{errors.website && touched.website && (
														<div className="mt-1 text-sm text-red-500">{errors.website}</div>
													)}
												</div>

												{/* Whitepaper URL */}
												<div>
													<label htmlFor="whitepaper" className="block text-sm font-medium text-white/80 mb-2">
														Whitepaper URL (Optional)
													</label>
													<Field
														type="url"
														name="whitepaper"
														placeholder="https://your-project.com/whitepaper"
														className="block w-full rounded-xl bg-white/5 border border-white/10 px-4 py-3 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-[#007AFF]/50 focus:border-transparent transition-all"
													/>
													{errors.whitepaper && touched.whitepaper && (
														<div className="mt-1 text-sm text-red-500">{errors.whitepaper}</div>
													)}
												</div>

												{/* Logo URL */}
												<div>
													<label htmlFor="logo" className="block text-sm font-medium text-white/80 mb-2">
														Logo URL (Optional)
													</label>
													<Field
														type="url"
														name="logo"
														placeholder="https://your-project.com/logo.png"
														className="block w-full rounded-xl bg-white/5 border border-white/10 px-4 py-3 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-[#007AFF]/50 focus:border-transparent transition-all"
													/>
													{errors.logo && touched.logo && (
														<div className="mt-1 text-sm text-red-500">{errors.logo}</div>
													)}
													<p className="mt-1 text-xs text-white/40">Recommended: Square image, minimum 512x512px</p>
												</div>

												{/* Banner URL */}
												<div>
													<label htmlFor="banner" className="block text-sm font-medium text-white/80 mb-2">
														Banner URL (Optional)
													</label>
													<Field
														type="url"
														name="banner"
														placeholder="https://your-project.com/banner.png"
														className="block w-full rounded-xl bg-white/5 border border-white/10 px-4 py-3 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-[#007AFF]/50 focus:border-transparent transition-all"
													/>
													{errors.banner && touched.banner && (
														<div className="mt-1 text-sm text-red-500">{errors.banner}</div>
													)}
													<p className="mt-1 text-xs text-white/40">Recommended: 1200x630px for optimal display</p>
												</div>
											</div>
										</div>

										{/* Project Socials */}
										<div className="grid grid-cols-1 md:grid-cols-3 gap-4">
											<div>
												<label htmlFor="projectTwitter" className="block text-sm font-medium text-white/80 mb-2">
													Twitter (Optional)
												</label>
												<div className="relative">
													<Field
														type="text"
														name="projectTwitter"
														placeholder="https://x.com/username"
														className="block w-full rounded-xl bg-white/5 border border-white/10 px-4 py-3 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-[#007AFF]/50 focus:border-transparent transition-all"
													/>
												</div>
											</div>

											<div>
												<label htmlFor="projectTelegram" className="block text-sm font-medium text-white/80 mb-2">
													Telegram (Optional)
												</label>
												<div className="relative">
													<Field
														type="text"
														name="projectTelegram"
														placeholder="https://t.me/groupname"
														className="block w-full rounded-xl bg-white/5 border border-white/10 px-4 py-3 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-[#007AFF]/50 focus:border-transparent transition-all"
													/>
												</div>
											</div>

											<div>
												<label htmlFor="projectDiscord" className="block text-sm font-medium text-white/80 mb-2">
													Discord (Optional)
												</label>
												<div className="relative">
													<Field
														type="text"
														name="projectDiscord"
														placeholder="https://discord.gg/invite-code"
														className="block w-full rounded-xl bg-white/5 border border-white/10 px-4 py-3 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-[#007AFF]/50 focus:border-transparent transition-all"
													/>
												</div>
											</div>
										</div>
									</motion.div>
								)}
							</AnimatePresence>

							<div className="flex items-center justify-between gap-4 pt-6 border-t border-white/10">
								<div>
									{step === 2 && (
										<button
											type="button"
											onClick={() => setStep(1)}
											className="px-6 py-3 text-sm font-medium text-white/60 hover:text-white transition-colors"
										>
											Back
										</button>
									)}
								</div>
								<div className="flex items-center gap-4">
									<button
										type="button"
										onClick={onCancel}
										className="px-6 py-3 text-sm font-medium text-white/60 hover:text-white transition-colors"
									>
										Cancel
									</button>
									<button
										type="submit"
										disabled={isSubmitting || !isValid || isPending || isUpdating}
										className="rounded-xl bg-gradient-to-r from-[#007AFF] to-[#00C6FF] px-6 py-3 text-sm font-semibold text-white shadow-lg hover:shadow-[#007AFF]/20 hover:from-[#0056b3] hover:to-[#00A6FF] transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
									>
										{isPending || isUpdating ? (
											<span className="flex items-center gap-2">
												<svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
													<circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
													<path
														className="opacity-75"
														fill="currentColor"
														d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
													/>
												</svg>
												{isEditing ? "Updating..." : "Creating..."}
											</span>
										) : step === 1 ? (
											"Next"
										) : isEditing ? (
											"Update Campaign"
										) : (
											"Create Campaign"
										)}
									</button>
								</div>
							</div>
						</Form>
					)}
				</Formik>
			</motion.div>
		</motion.div>
	);
};

export default CampaignForm;
