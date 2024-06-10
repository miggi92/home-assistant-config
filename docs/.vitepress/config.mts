import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "Home assistant config",
  description: "A home assistant config of my home.",
  base: "/home-assistant-config",
  lang: "en-US",
  lastUpdated: true,
  head: [
      ['link', { rel: 'icon', href: '/favicon.ico' }],
      ['meta', { property: 'og:type', content: 'website' }],
      ['meta', { property: 'og:locale', content: 'en' }],
      ['meta', { property: 'og:site_name', content: 'Miggi92 Home assistant config' }],
      ['meta', { property: 'og:url', content: 'https://miggi92.github.io/home-assistant-config/' }],
  ],
  sitemap: {
    hostname: "https://miggi92.github.io/home-assistant-config/"
  },
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: 'Home', link: '/'},
      { text: 'Config', link: '/config' },
      { text: 'Examples', link: '/examples' },
      { text: 'Featured', link: '/featured'}
    ],
    outline: [2, 6],
    lastUpdated: {
      text: 'Updated at',
      formatOptions: {
        dateStyle: 'full',
        timeStyle: 'medium'
      }
    },
    sidebar: [{
        text: 'Config',
      }, 
      {
        text: 'Examples',
        // items: [
        //   { text: 'Markdown Examples', link: '/markdown-examples' },
        //   { text: 'Runtime API Examples', link: '/api-examples' }
        // ]
      }, {
        text: 'Featured',
      }
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/miggi92/home-assistant-config' }
    ]
  },
  locales: {
      root: {
        label: 'English',
        lang: 'en'
      },
    }
})