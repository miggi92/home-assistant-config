import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "Home assistant config",
  description: "A home assistant config of my home.",
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: 'Home', link: '/'},
      { text: 'Config', link: '/config' },
      { text: 'Examples', link: '/examples' },
      { text: 'Featured', link: '/featured'}
    ],

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
  }
})
