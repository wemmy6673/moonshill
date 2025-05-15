import { useState, useEffect } from "react";
import { Link } from "wouter";
import { motion } from "framer-motion";
import { Formik, Form, Field } from "formik";
import * as Yup from "yup";
import AuthLayout from "../components/auth/AuthLayout";
import AuthInput from "../components/auth/AuthInput";
import logoWhite from "../assets/logo-white.png";
import { useMutation } from "@tanstack/react-query";
import { createFetcher } from "../libs/fetcher";
import config from "../libs/config";
import useSnack from "../hooks/useSnack";
import { setStorage, isStorageAvailable } from "../libs/browserutils";
import { useLocation } from "wouter";

const SignupSchema = Yup.object().shape({
	workspaceName: Yup.string()
		.min(3, "Workspace name must be at least 3 characters")
		.max(50, "Workspace name must be less than 50 characters")
		.matches(/^[a-zA-Z0-9-_ ]+$/, "Workspace name can only contain letters, numbers, spaces, hyphens, and underscores")
		.required("Workspace name is required"),
	email: Yup.string()
		.email("Invalid email address")
		.nullable()
		.transform((value) => (value === "" ? null : value)),
	terms: Yup.boolean()
		.oneOf([true], "You must accept the terms and conditions")
		.required("You must accept the terms and conditions"),
});

const Signup = () => {
	const [isWalletConnected, setIsWalletConnected] = useState(false);
	const [walletAddress, setWalletAddress] = useState("");
	const [isSigning, setIsSigning] = useState(false);
	const [error, setError] = useState("");
	const snack = useSnack();
	const [, navigate] = useLocation();

	const createWorkspaceMutation = useMutation({
		mutationKey: ["create-workspace"],
		mutationFn: createFetcher({
			url: config.endpoints.createWorkspace,
			method: "POST",
		}),
	});

	useEffect(() => {
		if (createWorkspaceMutation.isSuccess) {
			snack.success("Workspace created");
			if (isStorageAvailable()) {
				setStorage("workspaceAccessToken", createWorkspaceMutation.data);
				navigate("/campaigns", { replace: true });
			} else {
				navigate(`/campaigns?accessToken=${createWorkspaceMutation.data.accessToken}`, { replace: true });
			}
		}

		if (createWorkspaceMutation.isError) {
			snack.error(createWorkspaceMutation.error.message || "Failed to create workspace");
			createWorkspaceMutation.reset();
		}
	}, [createWorkspaceMutation.isSuccess, createWorkspaceMutation.isError, createWorkspaceMutation.error]);

	const handleSubmit = async (values, { setSubmitting }) => {
		if (!isWalletConnected) {
			return;
		}

		try {
			setIsSigning(true);
			setError("");

			// Prepare the message to sign
			const message = `Welcome to MoonShill!\n\nPlease sign this message to create your workspace "${values.workspaceName}".\n\nThis signature will be used to verify your ownership of this wallet address.`;

			// Request signature from wallet
			const signature = await window.ethereum.request({
				method: "personal_sign",
				params: [message, walletAddress],
			});
			const body = {
				message,
				signature,
				ownerAddress: walletAddress,
				name: values.workspaceName,
			};

			if (values.email) {
				body.notificationEmail = values.email;
			}

			createWorkspaceMutation.mutate(body);
		} catch (error) {
			console.error("Error during signup:", error);
			setError(error.message || "Failed to sign message. Please try again.");
		} finally {
			setIsSigning(false);
			setSubmitting(false);
		}
	};

	const connectWallet = async () => {
		try {
			setError("");
			if (typeof window.ethereum !== "undefined") {
				const accounts = await window.ethereum.request({ method: "eth_requestAccounts" });
				setWalletAddress(accounts[0]);
				setIsWalletConnected(true);
			} else {
				setError("Please install MetaMask to continue");
			}
		} catch (error) {
			console.error("Error connecting wallet:", error);
			setError(error.message || "Failed to connect wallet. Please try again.");
		}
	};

	const formatWalletAddress = (address) => {
		if (!address) return "";
		return `${address.slice(0, 6)}...${address.slice(-4)}`;
	};

	return (
		<AuthLayout title="Create Account" subtitle="Connect your wallet to get started">
			<div className="flex justify-center mb-6 sm:mb-8">
				<img src={logoWhite} alt="MoonShill" className="h-8 sm:h-12" />
			</div>
			<Formik
				initialValues={{
					workspaceName: "",
					email: "",
					terms: false,
				}}
				validationSchema={SignupSchema}
				onSubmit={handleSubmit}
			>
				{({ errors, touched, isSubmitting }) => (
					<Form className="space-y-4 px-4 sm:px-0">
						{error && (
							<motion.div
								initial={{ opacity: 0, y: -10 }}
								animate={{ opacity: 1, y: 0 }}
								className="bg-red-500/10 border border-red-500/20 text-red-500 px-3 sm:px-4 py-2 sm:py-3 rounded-lg text-xs sm:text-sm"
							>
								{error}
							</motion.div>
						)}
						{!isWalletConnected ? (
							<motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
								<p className="text-gray-400 text-center mb-4 text-sm sm:text-base">
									Connect your wallet to create your MoonShill workspace
								</p>
								<motion.button
									whileHover={{ scale: 1.02 }}
									whileTap={{ scale: 0.98 }}
									type="button"
									onClick={connectWallet}
									className="w-full bg-[#007AFF] text-white py-2.5 sm:py-3 rounded-lg text-sm sm:text-base font-medium hover:bg-[#0056b3] transition-colors duration-200 flex items-center justify-center"
								>
									<svg
										className="w-4 h-4 sm:w-5 sm:h-5 mr-2"
										viewBox="0 0 24 24"
										fill="none"
										xmlns="http://www.w3.org/2000/svg"
									>
										<path
											d="M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z"
											stroke="currentColor"
											strokeWidth="2"
										/>
										<path d="M12 7V17M7 12H17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
									</svg>
									Connect Wallet
								</motion.button>
							</motion.div>
						) : (
							<motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
								<div className="bg-[#1a1a1a] p-3 sm:p-4 rounded-lg border border-[#2a2a2a]">
									<div className="flex items-center justify-between">
										<span className="text-gray-400 text-sm sm:text-base">Connected Wallet</span>
										<div className="flex items-center gap-2">
											<span className="text-[#007AFF] font-mono text-xs sm:text-sm">
												{formatWalletAddress(walletAddress)}
											</span>
											<button
												onClick={() => {
													setWalletAddress("");
													setIsWalletConnected(false);
													setError("");
													createWorkspaceMutation.reset();
													snack.info(
														"Tip: If you want to connect a different wallet, you can do so from your wallet extension"
													);
												}}
												className="text-white/60 hover:text-white transition-colors"
											>
												<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
													<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
												</svg>
											</button>
										</div>
									</div>
								</div>

								<Field
									name="workspaceName"
									label="Workspace Name"
									placeholder="Enter your workspace name"
									component={AuthInput}
								/>

								<Field
									name="email"
									label="Email (Optional)"
									type="email"
									placeholder="Enter your email for notifications"
									component={AuthInput}
								/>

								<div className="space-y-1">
									<div className="flex items-center">
										<Field
											type="checkbox"
											name="terms"
											className="form-checkbox h-3.5 w-3.5 sm:h-4 sm:w-4 text-[#007AFF]"
										/>
										<span className="ml-2 text-xs sm:text-sm text-gray-400">
											I agree to the{" "}
											<Link href="/terms" className="text-[#007AFF] hover:text-[#0056b3]">
												Terms of Service
											</Link>{" "}
											and{" "}
											<Link href="/privacy" className="text-[#007AFF] hover:text-[#0056b3]">
												Privacy Policy
											</Link>
										</span>
									</div>
									{errors.terms && touched.terms && (
										<div className="text-red-500 text-xs sm:text-sm mt-1">{errors.terms}</div>
									)}
								</div>

								<motion.button
									whileHover={{ scale: 1.02 }}
									whileTap={{ scale: 0.98 }}
									type="submit"
									disabled={isSubmitting || isSigning}
									className="w-full bg-[#007AFF] text-white py-2.5 sm:py-3 rounded-lg text-sm sm:text-base font-medium hover:bg-[#0056b3] transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
								>
									{isSigning ? (
										<>
											<svg
												className="animate-spin -ml-1 mr-2 sm:mr-3 h-4 w-4 sm:h-5 sm:w-5 text-white"
												xmlns="http://www.w3.org/2000/svg"
												fill="none"
												viewBox="0 0 24 24"
											>
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
											Signing Message...
										</>
									) : (
										"Create Workspace"
									)}
								</motion.button>
							</motion.div>
						)}

						<p className="text-center text-gray-400 mt-6 text-sm sm:text-base">
							Already have a workspace?{" "}
							<Link href="/login" className="text-[#007AFF] hover:text-[#0056b3]">
								Connect Wallet
							</Link>
						</p>
					</Form>
				)}
			</Formik>
		</AuthLayout>
	);
};

export default Signup;
