import { fileURLToPath } from 'node:url'
import { mergeConfig, defineConfig, configDefaults } from 'vitest/config'
import viteConfig from './vite.config'

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      environment: 'jsdom',
      exclude: [...configDefaults.exclude, 'e2e/**'],
      root: fileURLToPath(new URL('./', import.meta.url)),
      reporters: [
        'default',
        ['junit', { outputFile: 'testresults/test-results.xml' }],
        ['html', { outputFile: 'testresults/test-result.html' }],
      ],
    },
  }),
)
