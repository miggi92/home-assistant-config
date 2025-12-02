export default defineNuxtConfig({
  modules: [
    '@nuxtjs/i18n',
    '@nuxt/eslint',
    '@nuxt/content',
    '@nuxt/ui',
    '@nuxt/image',
    'nuxt-studio'
  ],
  css: ['~/assets/css/main.css'],
  app: {
    baseURL: '/home-assistant-config/',
    buildAssetsDir: '/_nuxt/',
  },
  i18n: {
    defaultLocale: 'en',
    locales: [{
      code: 'en',
      name: 'English',
    }, {
      code: 'de',
      name: 'Deutsch',
    }],
  },
})