import { useState, useEffect } from "react";
import { Link } from "wouter";
import { motion } from "framer-motion";
import { Formik, Form } from "formik";
import AuthLayout from "../components/auth/AuthLayout";
import logoWhite from "../assets/logo-white.png";
import { useLocation } from "wouter";
import { setStorage, isStorageAvailable } from "../lib/browserutils";
import { useMutation } from "@tanstack/react-query";
import { createFetcher } from "../lib/fetcher";
import config from "../lib/config";
import useSnack from "../hooks/useSnack";

const Login = () => {
	const [isWalletConnected, setIsWalletConnected] = useState(false);
	const [walletAddress, setWalletAddress] = useState("");
	const [isSigning, setIsSigning] = useState(false);
	const [error, setError] = useState("");
	const [, navigate] = useLocation();
	const snack = useSnack();

	const loginMutation = useMutation({
		mutationKey: ["login"],
		mutationFn: createFetcher({
			url: config.endpoints.getAccessToken,
			method: "POST",
		}),
	});

	useEffect(() => {
		if (loginMutation.isSuccess) {
			snack.success("Welcome to your workspace!");

			if (isStorageAvailable()) {
				setStorage("workspaceAccessToken", loginMutation.data);
				navigate("/campaigns", { replace: true });
			} else {
				navigate(`/campaigns?accessToken=${loginMutation.data.accessToken}`, { replace: true });
			}
		}

		if (loginMutation.isError) {
			snack.error(loginMutation.error.message || "Failed to login");
			loginMutation.reset();
		}
	}, [loginMutation.isSuccess, loginMutation.isError, loginMutation.error]);

	const handleSubmit = async (_, { setSubmitting }) => {
		if (!isWalletConnected) {
			return;
		}

		try {
			setIsSigning(true);
			setError("");

			// Prepare the message to sign
			const message = `Welcome back to MoonShill!\n\nPlease sign this message to access your workspace.\n\nThis signature will be used to verify your ownership of this wallet address.`;

			// Request signature from wallet
			const signature = await window.ethereum.request({
				method: "personal_sign",
				params: [message, walletAddress],
			});

			const body = {
				message,
				signature,
				ownerAddress: walletAddress,
			};

			loginMutation.mutate(body);
		} catch (error) {
			console.error("Error during login:", error);
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
		<AuthLayout title="Welcome Back" subtitle="Connect your wallet to access your workspace">
			<div className="flex justify-center mb-6 sm:mb-8">
				<img src={logoWhite} alt="MoonShill" className="h-8 sm:h-12" />
			</div>
			<Formik initialValues={{}} onSubmit={handleSubmit}>
				{({ isSubmitting }) => (
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
									Connect your wallet to access your MoonShill workspace
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
													loginMutation.reset();
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
										"Access Workspace"
									)}
								</motion.button>
							</motion.div>
						)}

						<p className="text-center text-gray-400 mt-6 text-sm sm:text-base">
							Don't have a workspace?{" "}
							<Link href="/signup" className="text-[#007AFF] hover:text-[#0056b3]">
								Create One
							</Link>
						</p>
					</Form>
				)}
			</Formik>
		</AuthLayout>
	);
};

export default Login;
