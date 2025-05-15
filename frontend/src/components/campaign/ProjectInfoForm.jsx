import { useEffect, useState } from "react";
import { AnimatePresence } from "framer-motion";
import { Field, Form, Formik, useFormikContext, ErrorMessage } from "formik";
import * as Yup from "yup";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createFetcher } from "../../libs/fetcher";
import config from "../../libs/config";
import useSnack from "../../hooks/useSnack";

const detectAddress = (a) => {
	const p = {
		ethereum: /^0x[a-fA-F0-9]{40}$/,
		bitcoin: /^(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}$/,
		solana: /^[1-9A-HJ-NP-Za-km-z]{32,44}$/,
		tron: /^T[a-zA-HJ-NP-Z0-9]{33}$/,
	};
	return Object.entries(p).reduce((r, [k, v]) => (v.test(a) ? { valid: true, chain: k } : r), {
		valid: false,
		chain: null,
	});
};

const validationSchema = {
	basic: Yup.object().shape({
		projectName: Yup.string().required("Project name is required").label("Project Name"),
		projectInfo: Yup.string().required("Project description is required").label("Project Description"),
		projectWebsite: Yup.string().url("Must be a valid URL").label("Project Website"),
		projectTwitter: Yup.string().url("Must be a valid URL").label("Project Twitter"),
		projectTelegram: Yup.string().url("Must be a valid URL").label("Project Telegram"),
		projectDiscord: Yup.string().url("Must be a valid URL").label("Project Discord"),
		projectWhitepaper: Yup.string().url("Must be a valid URL").label("Project Whitepaper"),
		projectLogo: Yup.string().url("Must be a valid URL").label("Project Logo"),
		projectBanner: Yup.string().url("Must be a valid URL").label("Project Banner"),
	}),
	tokenomics: Yup.object().shape({
		projectTokenAddress: Yup.string()
			.test("is-valid-address", "Must be a valid address", (value) => {
				if (!value) return true;
				const { valid } = detectAddress(value);
				return valid;
			})
			.label("Project Token Address"),
		projectTokenSymbol: Yup.string()
			.matches(/^[a-zA-Z0-9]+$/, "Must be alphanumeric")
			.label("Project Token Symbol"),
		projectTokenDecimals: Yup.number().min(0).max(18).typeError("Must be a number").label("Project Token Decimals"),
		projectTokenSupply: Yup.number().positive().typeError("Must be a number").label("Project Token Supply"),
		projectTokenInitialPrice: Yup.number()
			.positive()
			.typeError("Must be a number")
			.label("Project Token Initial Price"),
		projectMarketCap: Yup.number().positive().typeError("Must be a number").label("Project Market Cap"),
		projectLaunchDate: Yup.date()
			.typeError("Must be a valid date")
			.test("is-future-date", "Must be a future date", (value) => {
				if (!value) return true;
				return new Date(value) > new Date();
			})
			.label("Project Launch Date"),
	}),
	technical: Yup.object().shape({
		blockchainNetworks: Yup.array().of(Yup.string()).label("Blockchain Networks"),
		smartContractFeatures: Yup.array().of(Yup.string()).label("Smart Contract Features"),
		technologyStack: Yup.array().of(Yup.string()).label("Technology Stack"),
		githubRepository: Yup.string().url("Must be a valid URL").label("GitHub Repository"),
	}),
	market: Yup.object().shape({
		targetMarkets: Yup.array().of(Yup.string()).label("Target Markets"),
		uniqueSellingPoints: Yup.array().of(Yup.string()).label("Unique Selling Points"),
		marketPositioning: Yup.string().label("Market Positioning"),
	}),
};

const Input = ({ label, name, type = "text", placeholder, required = false }) => (
	<div className="space-y-2">
		<label className="block text-sm font-medium text-white/80">
			{label} {required && <span className="text-red-400">*</span>}
		</label>
		<Field
			type={type}
			name={name}
			placeholder={placeholder}
			className="w-full px-4 py-2.5 bg-white/5 rounded-xl border border-white/10 text-white placeholder-white/40 focus:outline-none focus:border-[#007AFF] transition-colors"
		/>

		<ErrorMessage name={name} component="div" className="text-red-400 text-sm" />
	</div>
);

const TextArea = ({ label, name, placeholder, required = false, rows = 4 }) => (
	<div className="space-y-2">
		<label className="block text-sm font-medium text-white/80">
			{label} {required && <span className="text-red-400">*</span>}
		</label>
		<Field
			as="textarea"
			name={name}
			placeholder={placeholder}
			rows={rows}
			className="w-full px-4 py-2.5 bg-white/5 rounded-xl border border-white/10 text-white placeholder-white/40 focus:outline-none focus:border-[#007AFF] transition-colors resize-y min-h-[100px]"
		/>
	</div>
);

const Section = ({
	title,
	children,
	optional = false,
	isSubmitting,
	disableSave = false,
	buttonText = "Save Changes",
}) => {
	const [isOpen, setIsOpen] = useState(true);

	return (
		<div
			className={`rounded-xl border border-white/10 overflow-hidden transition-colors hover:border-white/20 ${
				isOpen ? "bg-white/5" : ""
			}`}
		>
			<button
				type="button"
				onClick={() => setIsOpen(!isOpen)}
				className="w-full px-6 py-4 flex items-center justify-between gap-4 transition-colors hover:bg-white/5"
			>
				<div className="flex flex-col sm:flex-row sm:items-center gap-2">
					<h3 className="text-base font-medium text-white">{title}</h3>
					{optional && (
						<span className="text-[11px] px-2.5 py-0.5 leading-relaxed rounded-full bg-white/5 text-white/50 font-medium tracking-wide">
							Optional
						</span>
					)}
				</div>
				<svg
					className={`w-5 h-5 text-[#007AFF] transition-transform ${isOpen ? "rotate-180" : ""}`}
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
				>
					<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
				</svg>
			</button>
			<AnimatePresence>
				{isOpen && (
					<div className="px-6 pb-6">
						<div className="space-y-4 pt-4">
							{children}
							<div className="flex justify-end pt-2">
								<button
									type="submit"
									disabled={isSubmitting || disableSave}
									className="px-6 py-2.5 bg-[#007AFF] text-white rounded-xl hover:bg-[#0056b3] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 font-medium"
								>
									{isSubmitting ? (
										<>
											<svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
												<circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
												<path
													className="opacity-75"
													fill="currentColor"
													d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
												/>
											</svg>
											Saving...
										</>
									) : (
										buttonText
									)}
								</button>
							</div>
						</div>
					</div>
				)}
			</AnimatePresence>
		</div>
	);
};

const ArrayInput = ({ label, name, placeholder }) => {
	const { values, setFieldValue } = useFormikContext();
	const [inputValue, setInputValue] = useState("");

	const handleAdd = (e) => {
		if (e.key === "Enter" && inputValue.trim()) {
			e.preventDefault();
			const currentValues = values[name] || [];
			setFieldValue(name, [...currentValues, inputValue.trim()]);
			setInputValue("");
		}
	};

	const handleRemove = (index) => {
		const currentValues = values[name] || [];
		setFieldValue(
			name,
			currentValues.filter((_, i) => i !== index)
		);
	};

	return (
		<div className="space-y-3">
			<label className="block text-sm font-medium text-white/80">{label}</label>
			<div className="relative">
				<input
					type="text"
					value={inputValue}
					onChange={(e) => setInputValue(e.target.value)}
					onKeyDown={handleAdd}
					placeholder={`${placeholder} (Press Enter to add)`}
					className="w-full px-4 py-2.5 bg-white/5 rounded-xl border border-white/10 text-white placeholder-white/40 focus:outline-none focus:border-[#007AFF] transition-colors"
				/>
			</div>
			{values[name]?.length > 0 && (
				<div className="flex flex-wrap gap-2">
					{values[name].map((item, index) => (
						<span key={index} className="inline-flex items-center gap-2 px-3 py-1.5 bg-white/10 rounded-full text-sm">
							{item}
							<button
								type="button"
								onClick={() => handleRemove(index)}
								className="p-0.5 hover:text-red-400 transition-colors rounded-full"
							>
								<svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
								</svg>
							</button>
						</span>
					))}
				</div>
			)}
		</div>
	);
};

const ProjectInfoForm = ({ initialData = {}, auth }) => {
	const snack = useSnack();
	const queryClient = useQueryClient();

	// BASIC INFO

	const updateBasicInfoMutation = useMutation({
		mutationKey: ["updateBasicInfo", initialData.id],
		mutationFn: createFetcher({
			method: "PUT",
			url: `${config.endpoints.updateCampaign}/${initialData.id}`,
			auth,
		}),
	});

	useEffect(() => {
		if (updateBasicInfoMutation.isSuccess) {
			snack.success("Project information updated successfully");
			queryClient.invalidateQueries({ queryKey: ["campaign", initialData.id] });
		}

		if (updateBasicInfoMutation.isError) {
			snack.error(updateBasicInfoMutation.error.message || "Failed to update project information");
			updateBasicInfoMutation.reset();
		}
	}, [updateBasicInfoMutation.isSuccess, updateBasicInfoMutation.isError, updateBasicInfoMutation.error]);

	// TOKENOMICS

	const updateTokenomicsMutation = useMutation({
		mutationKey: ["updateTokenomics", initialData.id],
		mutationFn: createFetcher({
			method: "PUT",
			url: `${config.endpoints.updateTokenomics}/${initialData.id}`,
			auth,
		}),
	});

	useEffect(() => {
		if (updateTokenomicsMutation.isSuccess) {
			snack.success("Tokenomics updated successfully");
			queryClient.invalidateQueries({ queryKey: ["campaign", initialData.id] });
		}

		if (updateTokenomicsMutation.isError) {
			snack.error(updateTokenomicsMutation.error.message || "Failed to update tokenomics");
			updateTokenomicsMutation.reset();
		}
	}, [updateTokenomicsMutation.isSuccess, updateTokenomicsMutation.isError, updateTokenomicsMutation.error]);

	// TECHNICAL

	const updateTechnicalMutation = useMutation({
		mutationKey: ["updateTechnical", initialData.id],
		mutationFn: createFetcher({
			method: "PUT",
			url: `${config.endpoints.updateTechnicalInfo}/${initialData.id}`,
			auth,
		}),
	});

	useEffect(() => {
		if (updateTechnicalMutation.isSuccess) {
			snack.success("Technical information updated successfully");
			queryClient.invalidateQueries({ queryKey: ["campaign", initialData.id] });
		}

		if (updateTechnicalMutation.isError) {
			snack.error(updateTechnicalMutation.error.message || "Failed to update technical information");
			updateTechnicalMutation.reset();
		}
	}, [updateTechnicalMutation.isSuccess, updateTechnicalMutation.isError, updateTechnicalMutation.error]);

	// MARKET

	const updateMarketMutation = useMutation({
		mutationKey: ["updateMarket", initialData.id],
		mutationFn: createFetcher({
			method: "PUT",
			url: `${config.endpoints.updateMarketInfo}/${initialData.id}`,
			auth,
		}),
	});

	useEffect(() => {
		if (updateMarketMutation.isSuccess) {
			snack.success("Market information updated successfully");
			queryClient.invalidateQueries({ queryKey: ["campaign", initialData.id] });
		}

		if (updateMarketMutation.isError) {
			snack.error(updateMarketMutation.error.message || "Failed to update market information");
			updateMarketMutation.reset();
		}
	}, [updateMarketMutation.isSuccess, updateMarketMutation.isError, updateMarketMutation.error]);

	// submit handlers

	const handleBasicInfoSubmit = (values, { setSubmitting }) => {
		updateBasicInfoMutation.mutate({
			campaignName: initialData.campaignName,
			campaignType: initialData.campaignType,
			targetPlatforms: initialData.targetPlatforms,
			engagementStyle: initialData.engagementStyle,
			campaignStartDate: new Date(initialData.campaignStartDate).toISOString().split("T")[0],
			campaignTimeline: initialData.campaignTimeline,
			campaignGoals: initialData.campaignGoals,

			projectName: values.projectName,
			projectInfo: values.projectInfo,
			targetAudience: initialData.targetAudience,

			projectWebsite: values.projectWebsite || undefined,
			projectWhitepaper: values.projectWhitepaper || undefined,
			projectLogo: values.projectLogo || undefined,
			projectBanner: values.projectBanner || undefined,
			projectTwitter: values.projectTwitter || undefined,
			projectTelegram: values.projectTelegram || undefined,
			projectDiscord: values.projectDiscord || undefined,
		});
		setSubmitting(false);
	};

	const handleTokenomicsSubmit = (values, { setSubmitting }) => {
		updateTokenomicsMutation.mutate({
			projectTokenAddress: values.projectTokenAddress || undefined,
			projectTokenSymbol: values.projectTokenSymbol || undefined,
			projectTokenDecimals: values.projectTokenDecimals || undefined,
			totalSupply: values.projectTokenSupply || undefined,
			initialPrice: values.projectTokenInitialPrice || undefined,
			marketCap: values.projectMarketCap || undefined,
			launchDate: values.projectLaunchDate ? new Date(values.projectLaunchDate).toISOString().split("T")[0] : undefined,
		});
		setSubmitting(false);
	};

	const handleTechnicalSubmit = (values, { setSubmitting }) => {
		updateTechnicalMutation.mutate({
			githubRepository: values.githubRepository || undefined,
			blockchainNetworks: values.blockchainNetworks || [],
			smartContractFeatures: values.smartContractFeatures || [],
			technologyStack: values.technologyStack || [],
		});
		setSubmitting(false);
	};

	const handleMarketSubmit = (values, { setSubmitting }) => {
		updateMarketMutation.mutate({
			targetMarket: values.targetMarket || [],
			uniqueSellingPoints: values.uniqueSellingPoints || [],
			marketPositioning: values.marketPositioning || undefined,
		});
		setSubmitting(false);
	};

	return (
		<div className="space-y-6">
			<Formik
				initialValues={{
					projectName: initialData.projectName || "",
					projectInfo: initialData.projectInfo || "",
					projectWebsite: initialData.projectWebsite || "",
					projectTwitter: initialData.projectTwitter || "",
					projectTelegram: initialData.projectTelegram || "",
					projectDiscord: initialData.projectDiscord || "",
					projectWhitepaper: initialData.projectWhitepaper || "",
					projectLogo: initialData.projectLogo || "",
					projectBanner: initialData.projectBanner || "",
				}}
				validationSchema={validationSchema.basic}
				onSubmit={handleBasicInfoSubmit}
			>
				{({ isSubmitting, isValid, dirty }) => (
					<Form>
						<Section
							title="Basic Information"
							isSubmitting={isSubmitting}
							disableSave={!isValid || updateBasicInfoMutation.isPending || !dirty}
						>
							<Input label="Project Name" name="projectName" placeholder="Enter project name" required />
							<TextArea
								label="Project Description"
								name="projectInfo"
								placeholder="Provide a detailed description of your project, including its main features, goals, and target audience..."
								required
								rows={6}
							/>
							<Input label="Website" name="projectWebsite" placeholder="http://..." />
							<Input label="Whitepaper" name="projectWhitepaper" placeholder="http://..." />
							<Input label="Logo" name="projectLogo" placeholder="http://..." />
							<Input label="Banner" name="projectBanner" placeholder="http://..." />
							<Input label="Twitter" name="projectTwitter" placeholder="http://x.com/..." />
							<Input label="Telegram" name="projectTelegram" placeholder="http://t.me/..." />
							<Input label="Discord" name="projectDiscord" placeholder="http://discord.gg/..." />
						</Section>
					</Form>
				)}
			</Formik>

			<Formik
				initialValues={{
					projectTokenAddress: initialData.tokenomics?.projectTokenAddress || "",
					projectTokenSymbol: initialData.tokenomics?.projectTokenSymbol || "",
					projectTokenDecimals: initialData.tokenomics?.projectTokenDecimals || "",
					projectTokenSupply: initialData.tokenomics?.totalSupply || "",
					projectTokenInitialPrice: initialData.tokenomics?.initialPrice || "",
					projectMarketCap: initialData.tokenomics?.marketCap || "",
					projectLaunchDate: initialData.tokenomics?.launchDate
						? new Date(initialData.tokenomics.launchDate).toISOString().split("T")[0]
						: "",
				}}
				validationSchema={validationSchema.tokenomics}
				onSubmit={handleTokenomicsSubmit}
			>
				{({ isSubmitting, isValid, dirty }) => (
					<Form>
						<Section
							title="Tokenomics"
							optional
							isSubmitting={isSubmitting}
							disableSave={!isValid || updateTokenomicsMutation.isPending || !dirty}
						>
							<Input label="Token Address" name="projectTokenAddress" placeholder="0x..." />
							<Input label="Token Symbol" name="projectTokenSymbol" placeholder="e.g., ETH" />
							<Input label="Token Decimals" name="projectTokenDecimals" type="number" placeholder="18" />
							<Input label="Total Supply" name="projectTokenSupply" type="number" placeholder="1000000" />
							<Input label="Initial Price (USD)" name="projectTokenInitialPrice" type="number" placeholder="0.001" />
							<Input label="Market Cap (USD)" name="projectMarketCap" type="number" placeholder="1000000" />
							<Input label="Launch Date" name="projectLaunchDate" type="date" placeholder="2024-01-01" />
						</Section>
					</Form>
				)}
			</Formik>

			<Formik
				initialValues={{
					blockchainNetworks: initialData.technicalInfo?.blockchainNetworks || [],
					smartContractFeatures: initialData.technicalInfo?.smartContractFeatures || [],
					githubRepository: initialData.technicalInfo?.githubRepository || "",
					technologyStack: initialData.technicalInfo?.technologyStack || [],
					tempNetwork: "",
					tempFeature: "",
					tempTechnology: "",
				}}
				validationSchema={validationSchema.technical}
				onSubmit={handleTechnicalSubmit}
			>
				{({ isSubmitting, values, setFieldValue, isValid, dirty }) => (
					<Form>
						<Section
							title="Technical Information"
							optional
							isSubmitting={isSubmitting}
							disableSave={!isValid || updateTechnicalMutation.isPending || !dirty}
						>
							<div className="space-y-6">
								<div>
									<label className="block text-sm font-medium text-white/80 mb-2">Blockchain Networks</label>
									<div className="relative flex items-center gap-2">
										<input
											type="text"
											placeholder="e.g., Ethereum, BSC"
											value={values.tempNetwork || ""}
											onChange={(e) => setFieldValue("tempNetwork", e.target.value)}
											onKeyDown={(e) => {
												if (e.key === "Enter" && e.target.value.trim()) {
													e.preventDefault();
													const networks = values.blockchainNetworks || [];
													setFieldValue("blockchainNetworks", [...networks, e.target.value.trim()]);
													setFieldValue("tempNetwork", "");
												}
											}}
											className="flex-1 px-4 py-2.5 bg-white/5 rounded-xl border border-white/10 text-white placeholder-white/40 focus:outline-none focus:border-[#007AFF] transition-colors"
										/>
										<button
											type="button"
											onClick={() => {
												if (values.tempNetwork?.trim()) {
													const networks = values.blockchainNetworks || [];
													setFieldValue("blockchainNetworks", [...networks, values.tempNetwork.trim()]);
													setFieldValue("tempNetwork", "");
												}
											}}
											className="flex-shrink-0 h-[42px] w-[42px] flex items-center justify-center rounded-xl bg-[#007AFF]/10 text-[#007AFF] hover:bg-[#007AFF]/20 transition-colors"
										>
											<svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
												<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
											</svg>
										</button>
									</div>
									{values.blockchainNetworks?.length > 0 && (
										<div className="mt-3 flex flex-wrap gap-2">
											{values.blockchainNetworks.map((network, index) => (
												<div
													key={index}
													className="group flex items-center gap-1.5 px-3 py-1.5 bg-white/5 rounded-full border border-white/10 hover:border-white/20 transition-colors"
												>
													<span className="text-sm text-white">{network}</span>
													<button
														type="button"
														onClick={() => {
															const newNetworks = values.blockchainNetworks.filter((_, i) => i !== index);
															setFieldValue("blockchainNetworks", newNetworks);
														}}
														className="p-0.5 text-white/40 hover:text-red-400 transition-colors rounded-full"
													>
														<svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
															<path
																strokeLinecap="round"
																strokeLinejoin="round"
																strokeWidth={2}
																d="M6 18L18 6M6 6l12 12"
															/>
														</svg>
													</button>
												</div>
											))}
										</div>
									)}
								</div>

								<div>
									<label className="block text-sm font-medium text-white/80 mb-2">Smart Contract Features</label>
									<div className="relative flex items-center gap-2">
										<input
											type="text"
											placeholder="e.g., Staking, NFT Minting"
											value={values.tempFeature || ""}
											onChange={(e) => setFieldValue("tempFeature", e.target.value)}
											onKeyDown={(e) => {
												if (e.key === "Enter" && e.target.value.trim()) {
													e.preventDefault();
													const features = values.smartContractFeatures || [];
													setFieldValue("smartContractFeatures", [...features, e.target.value.trim()]);
													setFieldValue("tempFeature", "");
												}
											}}
											className="flex-1 px-4 py-2.5 bg-white/5 rounded-xl border border-white/10 text-white placeholder-white/40 focus:outline-none focus:border-[#007AFF] transition-colors"
										/>
										<button
											type="button"
											onClick={() => {
												if (values.tempFeature?.trim()) {
													const features = values.smartContractFeatures || [];
													setFieldValue("smartContractFeatures", [...features, values.tempFeature.trim()]);
													setFieldValue("tempFeature", "");
												}
											}}
											className="flex-shrink-0 h-[42px] w-[42px] flex items-center justify-center rounded-xl bg-[#007AFF]/10 text-[#007AFF] hover:bg-[#007AFF]/20 transition-colors"
										>
											<svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
												<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
											</svg>
										</button>
									</div>
									{values.smartContractFeatures?.length > 0 && (
										<div className="mt-3 flex flex-wrap gap-2">
											{values.smartContractFeatures.map((feature, index) => (
												<div
													key={index}
													className="group flex items-center gap-1.5 px-3 py-1.5 bg-white/5 rounded-full border border-white/10 hover:border-white/20 transition-colors"
												>
													<span className="text-sm text-white">{feature}</span>
													<button
														type="button"
														onClick={() => {
															const newFeatures = values.smartContractFeatures.filter((_, i) => i !== index);
															setFieldValue("smartContractFeatures", newFeatures);
														}}
														className="p-0.5 text-white/40 hover:text-red-400 transition-colors rounded-full"
													>
														<svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
															<path
																strokeLinecap="round"
																strokeLinejoin="round"
																strokeWidth={2}
																d="M6 18L18 6M6 6l12 12"
															/>
														</svg>
													</button>
												</div>
											))}
										</div>
									)}
								</div>

								<div>
									<label className="block text-sm font-medium text-white/80 mb-2">Technology Stack</label>
									<div className="relative flex items-center gap-2">
										<input
											type="text"
											placeholder="e.g., React, Node.js"
											value={values.tempTechnology || ""}
											onChange={(e) => setFieldValue("tempTechnology", e.target.value)}
											onKeyDown={(e) => {
												if (e.key === "Enter" && e.target.value.trim()) {
													e.preventDefault();
													const technologies = values.technologyStack || [];
													setFieldValue("technologyStack", [...technologies, e.target.value.trim()]);
													setFieldValue("tempTechnology", "");
												}
											}}
											className="flex-1 px-4 py-2.5 bg-white/5 rounded-xl border border-white/10 text-white placeholder-white/40 focus:outline-none focus:border-[#007AFF] transition-colors"
										/>
										<button
											type="button"
											onClick={() => {
												if (values.tempTechnology?.trim()) {
													const technologies = values.technologyStack || [];
													setFieldValue("technologyStack", [...technologies, values.tempTechnology.trim()]);
													setFieldValue("tempTechnology", "");
												}
											}}
											className="flex-shrink-0 h-[42px] w-[42px] flex items-center justify-center rounded-xl bg-[#007AFF]/10 text-[#007AFF] hover:bg-[#007AFF]/20 transition-colors"
										>
											<svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
												<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
											</svg>
										</button>
									</div>
									{values.technologyStack?.length > 0 && (
										<div className="mt-3 flex flex-wrap gap-2">
											{values.technologyStack.map((technology, index) => (
												<div
													key={index}
													className="group flex items-center gap-1.5 px-3 py-1.5 bg-white/5 rounded-full border border-white/10 hover:border-white/20 transition-colors"
												>
													<span className="text-sm text-white">{technology}</span>
													<button
														type="button"
														onClick={() => {
															const newTechnologies = values.technologyStack.filter((_, i) => i !== index);
															setFieldValue("technologyStack", newTechnologies);
														}}
														className="p-0.5 text-white/40 hover:text-red-400 transition-colors rounded-full"
													>
														<svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
															<path
																strokeLinecap="round"
																strokeLinejoin="round"
																strokeWidth={2}
																d="M6 18L18 6M6 6l12 12"
															/>
														</svg>
													</button>
												</div>
											))}
										</div>
									)}
								</div>
								<Input label="GitHub Repository" name="githubRepository" placeholder="https://github.com/..." />
							</div>
						</Section>
					</Form>
				)}
			</Formik>

			<Formik
				initialValues={{
					targetMarkets: initialData.marketInfo?.targetMarkets || [],
					uniqueSellingPoints: initialData.marketInfo?.uniqueSellingPoints || [],
					marketPositioning: initialData.marketInfo?.marketPositioning || "",
					tempMarket: "",
					tempSellingPoint: "",
				}}
				validationSchema={validationSchema.market}
				onSubmit={handleMarketSubmit}
			>
				{({ isSubmitting, values, setFieldValue, isValid, dirty }) => (
					<Form>
						<Section
							title="Market Information"
							optional
							isSubmitting={isSubmitting}
							disableSave={!isValid || updateMarketMutation.isPending || !dirty}
						>
							<div className="space-y-6">
								<div>
									<label className="block text-sm font-medium text-white/80 mb-2">Target Markets</label>
									<div className="relative flex items-center gap-2">
										<input
											type="text"
											placeholder="e.g., DeFi, GameFi"
											value={values.tempMarket || ""}
											onChange={(e) => setFieldValue("tempMarket", e.target.value)}
											onKeyDown={(e) => {
												if (e.key === "Enter" && e.target.value.trim()) {
													e.preventDefault();
													const markets = values.targetMarkets || [];
													setFieldValue("targetMarkets", [...markets, e.target.value.trim()]);
													setFieldValue("tempMarket", "");
												}
											}}
											className="flex-1 px-4 py-2.5 bg-white/5 rounded-xl border border-white/10 text-white placeholder-white/40 focus:outline-none focus:border-[#007AFF] transition-colors"
										/>
										<button
											type="button"
											onClick={() => {
												if (values.tempMarket?.trim()) {
													const markets = values.targetMarkets || [];
													setFieldValue("targetMarkets", [...markets, values.tempMarket.trim()]);
													setFieldValue("tempMarket", "");
												}
											}}
											className="flex-shrink-0 h-[42px] w-[42px] flex items-center justify-center rounded-xl bg-[#007AFF]/10 text-[#007AFF] hover:bg-[#007AFF]/20 transition-colors"
										>
											<svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
												<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
											</svg>
										</button>
									</div>
									{values.targetMarkets?.length > 0 && (
										<div className="mt-3 flex flex-wrap gap-2">
											{values.targetMarkets.map((market, index) => (
												<div
													key={index}
													className="group flex items-center gap-1.5 px-3 py-1.5 bg-white/5 rounded-full border border-white/10 hover:border-white/20 transition-colors"
												>
													<span className="text-sm text-white">{market}</span>
													<button
														type="button"
														onClick={() => {
															const newMarkets = values.targetMarkets.filter((_, i) => i !== index);
															setFieldValue("targetMarkets", newMarkets);
														}}
														className="p-0.5 text-white/40 hover:text-red-400 transition-colors rounded-full"
													>
														<svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
															<path
																strokeLinecap="round"
																strokeLinejoin="round"
																strokeWidth={2}
																d="M6 18L18 6M6 6l12 12"
															/>
														</svg>
													</button>
												</div>
											))}
										</div>
									)}
								</div>

								<div>
									<label className="block text-sm font-medium text-white/80 mb-2">Unique Selling Points</label>
									<div className="relative flex items-center gap-2">
										<input
											type="text"
											placeholder="Enter a unique feature"
											value={values.tempSellingPoint || ""}
											onChange={(e) => setFieldValue("tempSellingPoint", e.target.value)}
											onKeyDown={(e) => {
												if (e.key === "Enter" && e.target.value.trim()) {
													e.preventDefault();
													const points = values.uniqueSellingPoints || [];
													setFieldValue("uniqueSellingPoints", [...points, e.target.value.trim()]);
													setFieldValue("tempSellingPoint", "");
												}
											}}
											className="flex-1 px-4 py-2.5 bg-white/5 rounded-xl border border-white/10 text-white placeholder-white/40 focus:outline-none focus:border-[#007AFF] transition-colors"
										/>
										<button
											type="button"
											onClick={() => {
												if (values.tempSellingPoint?.trim()) {
													const points = values.uniqueSellingPoints || [];
													setFieldValue("uniqueSellingPoints", [...points, values.tempSellingPoint.trim()]);
													setFieldValue("tempSellingPoint", "");
												}
											}}
											className="flex-shrink-0 h-[42px] w-[42px] flex items-center justify-center rounded-xl bg-[#007AFF]/10 text-[#007AFF] hover:bg-[#007AFF]/20 transition-colors"
										>
											<svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
												<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
											</svg>
										</button>
									</div>
									{values.uniqueSellingPoints?.length > 0 && (
										<div className="mt-3 flex flex-wrap gap-2">
											{values.uniqueSellingPoints.map((point, index) => (
												<div
													key={index}
													className="group flex items-center gap-1.5 px-3 py-1.5 bg-white/5 rounded-full border border-white/10 hover:border-white/20 transition-colors"
												>
													<span className="text-sm text-white">{point}</span>
													<button
														type="button"
														onClick={() => {
															const newPoints = values.uniqueSellingPoints.filter((_, i) => i !== index);
															setFieldValue("uniqueSellingPoints", newPoints);
														}}
														className="p-0.5 text-white/40 hover:text-red-400 transition-colors rounded-full"
													>
														<svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
															<path
																strokeLinecap="round"
																strokeLinejoin="round"
																strokeWidth={2}
																d="M6 18L18 6M6 6l12 12"
															/>
														</svg>
													</button>
												</div>
											))}
										</div>
									)}
								</div>

								<TextArea
									label="Market Positioning"
									name="marketPositioning"
									placeholder="Describe your project's position in the market, including your competitive advantages, target audience, and how you differentiate from competitors..."
									rows={5}
								/>
							</div>
						</Section>
					</Form>
				)}
			</Formik>
		</div>
	);
};

export default ProjectInfoForm;
