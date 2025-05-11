import { motion } from "framer-motion";
import { useEffect } from "react";

const Notification = ({ notification, onRemove }) => {
	const { type, message, duration } = notification;

	useEffect(() => {
		if (duration) {
			const timer = setTimeout(() => {
				onRemove(notification.id);
			}, duration);
			return () => clearTimeout(timer);
		}
	}, [duration, notification.id, onRemove]);

	const getIcon = () => {
		switch (type) {
			case "success":
				return (
					<svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
					</svg>
				);
			case "error":
				return (
					<svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
					</svg>
				);
			case "warning":
				return (
					<svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path
							strokeLinecap="round"
							strokeLinejoin="round"
							strokeWidth={2}
							d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
						/>
					</svg>
				);
			case "info":
				return (
					<svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path
							strokeLinecap="round"
							strokeLinejoin="round"
							strokeWidth={2}
							d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
						/>
					</svg>
				);
			default:
				return null;
		}
	};

	const getStyles = () => {
		switch (type) {
			case "success":
				return "bg-green-500/10 border-green-500/20 text-green-500";
			case "error":
				return "bg-red-500/10 border-red-500/20 text-red-500";
			case "warning":
				return "bg-yellow-500/10 border-yellow-500/20 text-yellow-500";
			case "info":
				return "bg-blue-500/10 border-blue-500/20 text-blue-500";
			default:
				return "bg-gray-500/10 border-gray-500/20 text-gray-500";
		}
	};

	// Check if the message contains a long string (like a hash)
	const hasLongString = message.split(/\s+/).some((word) => word.length > 20);

	return (
		<motion.div
			initial={{ opacity: 0, y: 50, scale: 0.3 }}
			animate={{ opacity: 1, y: 0, scale: 1 }}
			exit={{ opacity: 0, scale: 0.5, transition: { duration: 0.2 } }}
			className={`flex items-start w-full p-4 rounded-xl border shadow-lg ${getStyles()} backdrop-blur-sm`}
		>
			<div className="flex-shrink-0 mr-3 mt-0.5">{getIcon()}</div>
			<div className="flex-1 mr-2 min-w-0">
				<div className={`text-sm ${hasLongString ? "break-all" : "break-words"}`}>{message}</div>
			</div>
			<button
				onClick={() => onRemove(notification.id)}
				className="flex-shrink-0 ml-2 text-current hover:opacity-70 transition-opacity mt-0.5"
			>
				<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
				</svg>
			</button>
		</motion.div>
	);
};

export default Notification;
