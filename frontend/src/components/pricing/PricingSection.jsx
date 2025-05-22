import { motion } from "framer-motion";
import { Link } from "wouter";
import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { createFetcher } from "../../libs/fetcher";
import config from "../../libs/config";
import PageLoader from "../common/PageLoader";

const PricingSection = () => {
	const { data: pricingData, isLoading } = useQuery({
		queryKey: ["pricing"],
		queryFn: createFetcher({
			method: "GET",
			url: config.endpoints.getPricing,
		}),

		initialData: keepPreviousData,

		refetchInterval: 30000,
	});

	if (isLoading) {
		return (
			<div className="min-h-[400px] flex items-center justify-center">
				<PageLoader isPageWide={false} size="default" />
			</div>
		);
	}

	const tiers = pricingData?.tiers || {};

	// Helper function to determine if there's a price discount
	const hasDiscount = (basePrice, price) => {
		return parseFloat(basePrice) > parseFloat(price);
	};

	// Helper function to calculate discount amount
	const calculateDiscount = (basePrice, price) => {
		const discount = parseFloat(basePrice) - parseFloat(price);
		return Math.abs(discount) < 0.01 ? "0.00" : discount.toFixed(2);
	};

	// Helper function to format price
	const formatPrice = (price) => {
		const numericPrice = parseFloat(price);
		return Math.abs(numericPrice) < 0.01 ? "0.00" : numericPrice.toFixed(2);
	};

	return (
		<section id="pricing" className="relative py-20">
			<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
				<motion.div
					initial={{ opacity: 0, y: 20 }}
					animate={{ opacity: 1, y: 0 }}
					transition={{ duration: 0.5 }}
					className="text-center mb-16"
				>
					<h2 className="text-3xl sm:text-4xl font-bold mb-4">Simple, Transparent Pricing</h2>
					<p className="text-gray-400 max-w-3xl mx-auto">
						Choose the perfect plan for your project's growth. All plans include our core features, with options to
						scale as you go.
					</p>
				</motion.div>

				<div className="grid grid-cols-1 md:grid-cols-3 gap-y-12 md:gap-y-8 gap-x-8 max-w-6xl mx-auto">
					{Object.entries(tiers).map(([key, plan]) => (
						<motion.div
							key={key}
							initial={{ opacity: 0, y: 20 }}
							whileInView={{ opacity: 1, y: 0 }}
							viewport={{ once: true }}
							className={`relative bg-[#1A1A1A] rounded-2xl p-6 sm:p-8 flex flex-col ${
								plan.isPopular ? "border-[3px] border-[#007AFF] scale-105 md:scale-110" : "border border-white/15"
							}`}
						>
							{plan.isPopular && (
								<div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
									<span className="bg-[#007AFF] text-white px-4 py-1.5 rounded-full text-sm font-semibold shadow-lg">
										Most Popular
									</span>
								</div>
							)}
							<div className="text-center mb-8">
								<h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
								<p className="text-gray-400 mb-4 text-sm min-h-[3em]">{plan.description}</p>
								<div className="flex flex-col items-center justify-center">
									{hasDiscount(plan.basePrice, plan.price) &&
									parseFloat(calculateDiscount(plan.basePrice, plan.price)) > 0 ? (
										<>
											<div className="flex items-baseline">
												<span className="text-2xl font-bold text-gray-500 line-through mr-2">${plan.basePrice}</span>
												<span className="text-4xl font-bold text-green-400">${formatPrice(plan.price)}</span>
											</div>
											<span className="text-sm text-green-400 font-semibold mt-1 px-2 py-0.5 bg-green-500/10 rounded-md">
												Save ${calculateDiscount(plan.basePrice, plan.price)}! (One-Time Offer)
											</span>
											<span className="text-gray-400 ml-2 mt-1">/ {plan.billingPeriod}</span>
										</>
									) : (
										<div className="flex items-baseline justify-center">
											<span className="text-4xl font-bold">${formatPrice(plan.price)}</span>
											<span className="text-gray-400 ml-2">/ {plan.billingPeriod}</span>
										</div>
									)}
								</div>
							</div>
							<ul className="space-y-2.5 mb-6 flex-grow">
								{plan.features.map((feature, index) => (
									<li key={index} className="flex items-start">
										<svg
											className={`h-5 w-5 mt-0.5 mr-2 flex-shrink-0 ${
												feature.isHighlighted ? "text-[#007AFF]" : "text-white/60"
											}`}
											fill="none"
											viewBox="0 0 24 24"
											stroke="currentColor"
										>
											<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
										</svg>
										<div>
											<span
												className={`block text-sm ${
													feature.isHighlighted ? "text-white font-medium" : "text-white/80"
												}`}
											>
												{feature.name}
											</span>
											{feature.description && (
												<span className="text-sm text-white/60 block mt-0.5">{feature.description}</span>
											)}
										</div>
									</li>
								))}
							</ul>
							<Link href={`/signup?tag=${plan.priceTag}`} className="mt-auto">
								<motion.button
									whileHover={{ scale: 1.05 }}
									whileTap={{ scale: 0.95 }}
									className={`w-full py-3 rounded-lg font-semibold transition-colors text-sm ${
										plan.isPopular
											? "bg-[#007AFF] text-white hover:bg-[#0056b3] shadow-md hover:shadow-lg"
											: "bg-white/10 text-white hover:bg-white/20"
									}`}
								>
									Get Started
								</motion.button>
							</Link>
						</motion.div>
					))}
				</div>

				<div className="mt-20 text-center">
					<p className="text-gray-400 text-lg">
						Need a custom solution or have specific requirements?{" "}
						<Link href="/contact" className="text-[#007AFF] hover:text-[#0056b3] font-medium">
							Contact us
						</Link>{" "}
						for enterprise packages.
					</p>
				</div>
			</div>
		</section>
	);
};

export default PricingSection;
