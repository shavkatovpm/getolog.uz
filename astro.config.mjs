// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  site: 'https://getolog.uz',
  integrations: [sitemap()],
  i18n: {
    defaultLocale: 'uz',
    locales: ['uz', 'ru'],
    routing: {
      prefixDefaultLocale: false,
    },
  },
});
