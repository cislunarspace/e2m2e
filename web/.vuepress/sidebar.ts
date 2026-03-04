import { SidebarConfig4Multiple } from "vuepress/config";

// 全局侧边栏配置 - 在所有页面显示相同的导航结构
const globalSidebar = [
    {
        title: "地月空间是什么？",
        collapsable: true,
        children: [
            ["/地月空间是什么/", "概述"],
            ["/地月空间是什么/空间环境特征", "空间环境特征"],
            ["/地月空间是什么/参考文献", "参考文献"],
        ]
    },
    {
        title: "地月空间飞行器在什么轨道上运行？",
        collapsable: true,
        children: [
            ["/地月空间飞行器在什么轨道上运行/", "概述"],
        ]
    },
    {
        title: "地月空间科学研究前沿在哪里？",
        collapsable: true,
        children: [
            ["/地月空间科学研究前沿在哪里/", "引言"],
            ["/地月空间科学研究前沿在哪里/研究方向", "研究方向"],
            ["/地月空间科学研究前沿在哪里/研究机构和组织", "研究机构和组织"],
            ["/地月空间科学研究前沿在哪里/期刊会议", "期刊会议"],
            ["/地月空间科学研究前沿在哪里/重大项目", "重大项目"],
        ]
    },
    {
        title: "地月空间术语词典",
        collapsable: true,
        children: [
            ["/地月空间术语词典/", "概述"],
            ["/地月空间术语词典/圆形限制性三体问题", "圆形限制性三体问题"],
            ["/地月空间术语词典/X 射线脉冲星导航", "X射线脉冲星导航"],
        ]
    },
    {
        title: "资源与工具",
        collapsable: true,
        children: [
            ["/资源与工具/", "引言"],
            ["/资源与工具/数据集下载", "数据集下载"],
        ]
    },
    {
        title: "关于本站",
        collapsable: true,
        children: [
            ["/关于本站/", "引言"],
        ]
    }
];

// @ts-ignore
export default {
    // 所有页面都使用相同的全局侧边栏
    "/": globalSidebar,
    "/地月空间是什么/": globalSidebar,
    "/地月空间是什么/空间环境特征": globalSidebar,
    "/地月空间是什么/参考文献": globalSidebar,
    "/地月空间飞行器在什么轨道上运行/": globalSidebar,
    "/地月空间科学研究前沿在哪里/": globalSidebar,
    "/地月空间科学研究前沿在哪里/期刊会议": globalSidebar,
    "/地月空间科学研究前沿在哪里/研究方向": globalSidebar,
    "/地月空间科学研究前沿在哪里/研究机构和组织": globalSidebar,
    "/地月空间科学研究前沿在哪里/重大项目": globalSidebar,
    "/地月空间术语词典/": globalSidebar,
    "/地月空间术语词典/X 射线脉冲星导航": globalSidebar,
    "/资源与工具/": globalSidebar,
    "/资源与工具/数据集下载": globalSidebar,
    "/关于本站/": globalSidebar,
} as SidebarConfig4Multiple;
