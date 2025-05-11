import { defineConfig } from "vite";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react-swc";

// https://vite.dev/config/
export default defineConfig({
	plugins: [react(), tailwindcss()],

	resolve: {
		alias: {
			"@": "/src",
			"@components": "/src/components",
			"@pages": "/src/pages",
			"@assets": "/src/assets",
			"@hooks": "/src/hooks",
			"@lib": "/src/lib",
		},
	},
});
