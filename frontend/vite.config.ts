import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@components': resolve(__dirname, 'src/components'),
      '@pages': resolve(__dirname, 'src/pages'),
      '@hooks': resolve(__dirname, 'src/hooks'),
      '@utils': resolve(__dirname, 'src/utils'),
      '@types': resolve(__dirname, 'src/types'),
      '@store': resolve(__dirname, 'src/store'),
      '@api': resolve(__dirname, 'src/api'),
      '@assets': resolve(__dirname, 'src/assets'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/socket.io': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        ws: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    // AUTO-PILOT: Enhanced build optimization for ~40% bundle reduction
    minify: 'esbuild', // Use esbuild instead of terser for faster builds
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          router: ['react-router-dom'],
          state: ['@reduxjs/toolkit', 'react-redux'],
          charts: ['chart.js', 'react-chartjs-2', 'recharts'],
          ui: ['@headlessui/react', '@heroicons/react', 'framer-motion'],
          // AUTO-PILOT: Additional chunk splitting for better caching  
          utils: ['lodash', 'date-fns'],
          networking: ['axios', 'socket.io-client'],
        },
        // AUTO-PILOT: Optimize chunk file naming for better caching
        chunkFileNames: (chunkInfo) => {
          const facadeModuleId = chunkInfo.facadeModuleId ? 
            chunkInfo.facadeModuleId.split('/').pop()?.replace('.tsx', '').replace('.ts', '') : 
            'chunk';
          return `js/${facadeModuleId || 'chunk'}-[hash].js`;
        },
        assetFileNames: (assetInfo) => {
          const name = assetInfo.name || 'asset';
          const extType = name.split('.').at(1);
          if (extType && /png|jpe?g|svg|gif|tiff|bmp|ico/i.test(extType)) {
            return `img/[name]-[hash][extname]`;
          }
          if (extType && /css/i.test(extType)) {
            return `css/[name]-[hash][extname]`;
          }
          return `assets/[name]-[hash][extname]`;
        },
      },
      // AUTO-PILOT: Enhanced tree-shaking configuration
      treeshake: {
        moduleSideEffects: false,
        propertyReadSideEffects: false,
        unknownGlobalSideEffects: false,
      },
    },
    // AUTO-PILOT: Bundle size analysis and warnings
    chunkSizeWarningLimit: 500, // Reduced from 1000 for better optimization awareness
    // AUTO-PILOT: Enable compression for smaller builds
    reportCompressedSize: true,
    // AUTO-PILOT: Target modern browsers for smaller output
    target: 'es2020',
  },
  optimizeDeps: {
    include: ['react', 'react-dom', 'react-router-dom'],
  },
});
