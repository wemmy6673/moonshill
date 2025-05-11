import { AnimatePresence } from "framer-motion";

const ConfirmDialog = ({ isOpen, onClose, onConfirm, title, message }) => {
	if (!isOpen) return null;

	return (
		<AnimatePresence>
			<div
				className="fixed inset-0 bg-black/80 backdrop-blur-sm z-[100] flex min-h-screen items-center justify-center p-8 sm:p-12"
				onClick={onClose}
			>
				<div
					className="relative top-0 bg-[#0a0a0a] border border-white/10 rounded-2xl w-full max-w-md overflow-hidden shadow-2xl"
					onClick={(e) => e.stopPropagation()}
				>
					<div className="p-6">
						<h3 className="text-xl font-semibold text-white mb-2">{title}</h3>
						<p className="text-white/60">{message}</p>
					</div>
					<div className="flex items-center justify-end gap-3 px-6 py-4 bg-white/5 border-t border-white/10">
						<button
							onClick={onClose}
							className="px-4 py-2 text-sm font-medium text-white/60 hover:text-white transition-colors"
						>
							Cancel
						</button>
						<button
							onClick={onConfirm}
							className="rounded-xl bg-red-500 px-4 py-2 text-sm font-semibold text-white hover:bg-red-600 transition-colors"
						>
							Confirm
						</button>
					</div>
				</div>
			</div>
		</AnimatePresence>
	);
};

export default ConfirmDialog;
