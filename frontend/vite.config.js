import { fileURLToPath, URL } from 'node:url';

import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import vueDevTools from 'vite-plugin-vue-devtools';

const isDocker = process.env.DOCKER_ENV === 'true';

// https://vite.dev/config/
export default defineConfig(({ mode }) => ({
	plugins: [vue()],
	// plugins: [vue(), vueDevTools()],
	resolve: {
		alias: {
			'@': fileURLToPath(new URL('./src', import.meta.url)),
		},
	},
	base: mode === 'production' ? '/page/' : '/dev/',
	server: {
		port: 5173,
		host: true, // Ensures the server is accessible from the network
		strictPort: true, // Prevents the port from changing if it’s in use
		proxy:
			mode === 'production'
				? {} // No proxy in production
				: {
						'/api': {
							target: isDocker ? 'http://backend:8080' : 'http://localhost:8010',
							changeOrigin: true,
						},
					},
	},
	assetsInclude: ['**/*.csv'], // Füge CSV-Dateien als Assets hinzu
}));
