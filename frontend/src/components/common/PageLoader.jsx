import { motion } from "framer-motion";

const PageLoader = ({ color = "#007AFF", isPageWide = true, size = "default" }) => {
	const sizeClasses = {
		small: "h-4 w-4",
		default: "h-10 w-10",
		large: "h-16 w-16",
	};

	const spinnerSize = sizeClasses[size] || sizeClasses.default;
	const textSize =
		{
			small: "text-xs",
			default: "text-base",
			large: "text-lg",
		}[size] || "text-base";

	const loader = (
		<motion.div
			className="flex flex-col items-center gap-4"
			initial={{ opacity: 0 }}
			animate={{ opacity: 1 }}
			exit={{ opacity: 0 }}
		>
			<svg className={`animate-spin ${spinnerSize}`} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
				<circle className="opacity-25" cx="12" cy="12" r="10" stroke={color} strokeWidth="4"></circle>
				<path
					className="opacity-75"
					fill={color}
					d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
				></path>
			</svg>
			<div className={`text-white/60 font-medium ${textSize}`}>Loading...</div>
		</motion.div>
	);

	if (isPageWide) {
		return <div className="fixed inset-0 bg-[#0a0a0a] z-50 flex items-center justify-center">{loader}</div>;
	}

	return <div className="flex items-center justify-center p-4">{loader}</div>;
};

export default PageLoader;
