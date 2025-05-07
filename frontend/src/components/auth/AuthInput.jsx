import { forwardRef } from "react";

const AuthInput = forwardRef(({ label, error, type = "text", field, form, ...props }, ref) => {
	// Handle both direct props and Formik field props
	const inputProps = field || props;
	const errorMessage = form?.errors?.[field?.name] || error;

	return (
		<div className="mb-4">
			<label className="block text-[#eaeaea] text-sm font-medium mb-2">{label}</label>
			<input
				ref={ref}
				type={type}
				className={`w-full px-4 py-3 rounded-lg bg-[#1a1a1a] border ${
					errorMessage ? "border-red-500" : "border-[#2a2a2a]"
				} text-[#eaeaea] focus:outline-none focus:ring-2 focus:ring-[#007AFF] focus:border-transparent transition-all duration-200`}
				{...inputProps}
			/>
			{errorMessage && <p className="mt-1 text-sm text-red-500">{errorMessage}</p>}
		</div>
	);
});

AuthInput.displayName = "AuthInput";

export default AuthInput;
