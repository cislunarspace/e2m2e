import { defineConfig } from "vuepress/config";
import navbar from "./navbar";
import sidebar from "./sidebar";
import footer from "./footer";
import extraSideBar from "./extraSideBar";

const author = "天疆说";
const domain = "https://cislunarspace.cn";
const tags = ["地月空间", "航天", "轨道动力学"];

export default defineConfig({
  title: "地月空间入门指南",
  description: "系统掌握地月空间科学、技术与工程实践",
  head: [
    // 站点图标
    ["link", { rel: "icon", href: "/favicon.ico" }],
    // SEO
    [
      "meta",
      {
        name: "keywords",
        content:
          "地月空间，航天，轨道动力学，拉格朗日点，NRHO, 阿耳忒弥斯，月球探测，航天器轨道，CR3BP，GNC",
      },
    ],
    // 百度统计
    [
      "script",
      {},
      `
        var _hmt = _hmt || [];
        (function() {
          var hm = document.createElement("script");
          hm.src = "https://hm.baidu.com/hm.js?2675818a983a3131404cee835018f016";
          var s = document.getElementsByTagName("script")[0]; 
          s.parentNode.insertBefore(hm, s);
        })();
      `,
    ],
    // Google Analytics 4
    [
      "script",
      { async: true, src: "https://www.googletagmanager.com/gtag/js?id=G-0PLJ56MK80" }
    ],
    [
      "script",
      {},
      `
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', 'G-0PLJ56MK80');
      `
    ],
  ],
  // 监听文件变化，热更新
  extraWatchFiles: [".vuepress/*.ts", ".vuepress/sidebars/*.ts"],
  // 开发服务器代理（解决 AI API 跨域问题）
  devServer: {
    proxy: {
      '/api/ai': {
        target: 'https://api.deepseek.com',
        changeOrigin: true,
        pathRewrite: { '^/api/ai': '' },
      },
    },
  },
  markdown: {
    // 开启代码块的行号
    lineNumbers: true,
    // 支持 4 级以上的标题渲染
    extractHeaders: ["h2", "h3", "h4", "h5", "h6"],
  },
  // @ts-ignore
  plugins: [
    ["@vuepress/back-to-top"],
    // latex 数学公式支持
    [
    "vuepress-plugin-mathjax",
    {
      target: "svg", // 输出格式：'svg' 或 'chtml'
      macros: {
        // 自定义宏，可选
        "\\Z": "\\mathbb{Z}",
      },
    },
    ],
    // Google 分析
    [
      "@vuepress/google-analytics",
      {
        ga: "G-0PLJ56MK80", // Google Analytics 4 测量 ID
      },
    ],
    ["@vuepress/medium-zoom"],
    // https://github.com/lorisleiva/vuepress-plugin-seo
    [
      "seo",
      {
        siteTitle: (_, $site) => $site.title,
        title: ($page) => {
          const pageTitle = $page.frontmatter.wechatShare?.title ||
            $page.frontmatter.shareTitle ||
            $page.title;
          return `地月空间入门指南 | ${pageTitle}`;
        },
        description: ($page) =>
          $page.frontmatter.wechatShare?.desc ||
          $page.frontmatter.shareDesc ||
          $page.frontmatter.description || $page.description,
        author: (_, $site) => $site.themeConfig.author || author,
        tags: ($page) => $page.frontmatter.tags || tags,
        type: ($page) => "article",
        url: (_, $site, path) =>
          ($site.themeConfig.domain || domain || "") + path,
        image: ($page, $site) => {
          const siteDomain = ($site.themeConfig.domain || domain || "").replace(/\/$/, "");
          const rawImage =
            $page.frontmatter.wechatShare?.image ||
            $page.frontmatter.shareImage ||
            $page.frontmatter.image ||
            "/logo.png";

          if (/^https?:\/\//.test(rawImage)) {
            return rawImage;
          }

          const normalizedPath = rawImage.startsWith("/") ? rawImage : `/${rawImage}`;
          return `${siteDomain}${normalizedPath}`;
        },
        publishedAt: ($page) =>
          $page.frontmatter.date && new Date($page.frontmatter.date),
        modifiedAt: ($page) => $page.lastUpdated && new Date($page.lastUpdated),
      },
    ],
    // https://github.com/ekoeryanto/vuepress-plugin-sitemap
    [
      "sitemap",
      {
        hostname: domain,
      },
    ],
    // https://github.com/IOriens/vuepress-plugin-baidu-autopush
    ["vuepress-plugin-baidu-autopush"],
    // https://github.com/zq99299/vuepress-plugin/tree/master/vuepress-plugin-tags
    ["vuepress-plugin-tags"],
    // https://github.com/znicholasbrown/vuepress-plugin-code-copy
    [
      "vuepress-plugin-code-copy",
      {
        successText: "代码已复制",
      },
    ],
    // https://github.com/webmasterish/vuepress-plugin-feed
    [
      "feed",
      {
        canonical_base: domain,
        count: 10000,
        // 需要自动推送的文档目录
        posts_directories: [],
      },
    ],
    // https://github.com/tolking/vuepress-plugin-img-lazy
    ["img-lazy"],
  ],
  // 主题配置
  themeConfig: {
    logo: "/icon.ico",
    domain,
    nav: navbar,
    sidebar,
    lastUpdated: "最近更新",

    // 微信分享卡片配置（需配合后端签名接口）
    wechatShare: {
      enabled: true,
      signatureEndpoint: "https://www.cislunarspace.cn/api/wechat-signature",
      defaultTitle: "地月空间入门指南",
      defaultDesc: "系统掌握地月空间科学、技术与工程实践",
      defaultImage: "/logo.png",
    },

    // Gitee 仓库位置
    repo: "https://gitee.com/cislunarspace/cislunarspace",
    docsBranch: "master",

    // 编辑链接
    editLinks: true,
    editLinkText: "完善页面",

    // @ts-ignore
    // 底部版权信息
    footer,
    // 额外右侧边栏
    extraSideBar,
  },
});