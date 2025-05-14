import { useState } from "react";
import { AnimatePresence } from "framer-motion";
import { Field, Form, Formik, useField, useFormikContext } from "formik";
import * as Yup from "yup";

const validationSchema = Yup.object().shape({
	// Basic Info
	projectName: Yup.string().required("Project name is required"),
	projectInfo: Yup.string().required("Project description is required"),
	projectWebsite: Yup.string().url("Must be a valid URL"),
	projectTwitter: Yup.string(),
	projectTelegram: Yup.string(),
	projectDiscord: Yup.string(),

	// Tokenomics (all optional)
	projectTokenAddress: Yup.string(),
	projectTokenSymbol: Yup.string(),
	projectTokenDecimals: Yup.number().min(0).max(18),
	projectTokenSupply: Yup.number().positive(),
	projectTokenInitialPrice: Yup.number().positive(),
	projectMarketCap: Yup.number().positive(),

	// Technical Info
	blockchainNetworks: Yup.array().of(Yup.string()),
	smartContractFeatures: Yup.array().of(Yup.string()),
	githubRepository: Yup.string().url("Must be a valid URL"),

	// Market Info
	targetMarkets: Yup.array().of(Yup.string()),
	uniqueSellingPoints: Yup.array().of(Yup.string()),
	marketPositioning: Yup.string(),
});

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
	</div>
);

const Section = ({ title, children, optional = false }) => {
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
						<div className="space-y-4 pt-4">{children}</div>
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

const ProjectInfoForm = ({ initialData, onSubmit }) => {
	return (
		<Formik initialValues={initialData || {}} validationSchema={validationSchema} onSubmit={onSubmit}>
			{({ isSubmitting }) => (
				<Form className="space-y-6">
					<div className="grid grid-cols-1 gap-6">
						<Section title="Basic Information">
							<Input label="Project Name" name="projectName" placeholder="Enter project name" required />
							<Input label="Project Description" name="projectInfo" placeholder="Describe your project" required />
							<Input label="Website" name="projectWebsite" placeholder="https://..." />
							<Input label="Twitter" name="projectTwitter" placeholder="@username" />
							<Input label="Telegram" name="projectTelegram" placeholder="t.me/..." />
							<Input label="Discord" name="projectDiscord" placeholder="discord.gg/..." />
						</Section>

						<Section title="Tokenomics" optional>
							<Input label="Token Address" name="projectTokenAddress" placeholder="0x..." />
							<Input label="Token Symbol" name="projectTokenSymbol" placeholder="e.g., ETH" />
							<Input label="Token Decimals" name="projectTokenDecimals" type="number" placeholder="18" />
							<Input label="Total Supply" name="projectTokenSupply" type="number" placeholder="1000000" />
							<Input label="Initial Price (USD)" name="projectTokenInitialPrice" type="number" placeholder="0.001" />
							<Input label="Market Cap (USD)" name="projectMarketCap" type="number" placeholder="1000000" />
						</Section>

						<Section title="Technical Information" optional>
							<ArrayInput label="Blockchain Networks" name="blockchainNetworks" placeholder="e.g., Ethereum, BSC" />
							<ArrayInput
								label="Smart Contract Features"
								name="smartContractFeatures"
								placeholder="e.g., Staking, NFT Minting"
							/>
							<Input label="GitHub Repository" name="githubRepository" placeholder="https://github.com/..." />
						</Section>

						<Section title="Market Information" optional>
							<ArrayInput label="Target Markets" name="targetMarkets" placeholder="e.g., DeFi, GameFi" />
							<ArrayInput
								label="Unique Selling Points"
								name="uniqueSellingPoints"
								placeholder="Enter a unique feature"
							/>
							<Input label="Market Positioning" name="marketPositioning" placeholder="Describe your market position" />
						</Section>
					</div>

					<div className="sticky bottom-0 bg-[#1a1a1a]/80 backdrop-blur-xl p-4 -mx-4 -mb-8 sm:static sm:bg-transparent sm:backdrop-blur-none sm:p-0 sm:m-0">
						<div className="flex flex-col sm:flex-row justify-end gap-3 max-w-7xl mx-auto">
							<button
								type="button"
								className="w-full sm:w-auto px-6 py-2.5 border border-white/10 rounded-xl text-white/60 hover:text-white hover:border-white/20 transition-colors order-2 sm:order-1"
							>
								Cancel
							</button>
							<button
								type="submit"
								disabled={isSubmitting}
								className="w-full sm:w-auto px-6 py-2.5 bg-[#007AFF] text-white rounded-xl hover:bg-[#0056b3] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 order-1 sm:order-2 font-medium"
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
									"Save Changes"
								)}
							</button>
						</div>
					</div>
				</Form>
			)}
		</Formik>
	);
};

export default ProjectInfoForm;
