import { motion } from "framer-motion";

const AuthLayout = ({ children, title, subtitle }) => {
	return (
		<div className="min-h-screen bg-[#0e0e10] flex items-center justify-center p-4">
			<div className="w-full max-w-md">
				<motion.div
					initial={{ opacity: 0, y: 20 }}
					animate={{ opacity: 1, y: 0 }}
					transition={{ duration: 0.5 }}
					className="bg-[#121212] rounded-2xl p-8 shadow-2xl border border-[#1a1a1a]"
				>
					<div className="text-center mb-8">
						<h1 className="text-3xl font-bold text-[#eaeaea] mb-2">{title}</h1>
						<p className="text-gray-400">{subtitle}</p>
					</div>
					{children}
				</motion.div>
			</div>
		</div>
	);
};

export default AuthLayout;
