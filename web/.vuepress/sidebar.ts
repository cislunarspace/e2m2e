import { SidebarConfig } from "vuepress/config";

// 主侧边栏配置
const mainSidebar = [
    {
        title: "地月空间是什么",
        collapsable: true,
        children: [
            ["/what-is-cislunarspace/", "概述"],
            ["/what-is-cislunarspace/environment", "空间环境特征"],
            ["/what-is-cislunarspace/references", "参考文献"],
        ]
    },
    {
        title: "地月空间飞行器运行轨道",
        collapsable: true,
        children: [
            ["/cislunar-orbits/", "概述"],
        ]
    },
    {
        title: "地月空间科学研究前沿",
        collapsable: true,
        children: [
            ["/research-frontiers/", "引言"],
            ["/research-frontiers/directions", "研究方向"],
            ["/research-frontiers/institutions", "研究机构和组织"],
            ["/research-frontiers/journals-conferences", "期刊会议"],
            ["/research-frontiers/major-projects", "重大项目"],
        ]
    },
];

// 词典独立侧边栏
const glossarySidebar = [
    {
        title: "地月空间术语词典",
        collapsable: false,
        children: [
            ["/glossary/", "概述"],
            ["/glossary/cr3bp", "圆形限制性三体问题"],
            ["/glossary/xray-pulsar-navigation", "X射线脉冲星导航"],
        ]
    }
];

// 资源与工具独立侧边栏
const resourcesToolsSidebar = [
    {
        title: "资源与工具",
        collapsable: false,
        children: [
            ["/resources-tools/", "概述"],
            ["/resources-tools/datasets", "数据集"],
        ]
    }
];

// VuePress 1.x 多侧边栏配置
// 注意：回退配置 '/' 应该放在最后
const sidebarConfig: SidebarConfig = {
    // 词典页面使用独立的词典侧边栏
    "/glossary/": glossarySidebar,
    
    // 资源与工具页面使用独立的资源与工具侧边栏
    "/resources-tools/": resourcesToolsSidebar,
    
    // 主要页面使用主侧边栏
    "/what-is-cislunarspace/": mainSidebar,
    "/cislunar-orbits/": mainSidebar,
    "/research-frontiers/": mainSidebar,
    
    // 默认侧边栏（用于首页和其他页面）- 放在最后
    "/": mainSidebar,
};

export default sidebarConfig;
