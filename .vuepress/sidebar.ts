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
            ["/地月空间飞行器在什么轨道上运行/CAPSTONE任务", "CAPSTONE任务"],
            ["/地月空间飞行器在什么轨道上运行/GRAIL-SMART-1任务", "GRAIL-SMART-1任务"],
            ["/地月空间飞行器在什么轨道上运行/阿耳忒弥斯计划", "阿耳忒弥斯计划"],
            ["/地月空间飞行器在什么轨道上运行/LONEStar实验", "LONEStar实验"],
        ]
    },
    {
        title: "地月空间科学研究前沿在哪里？",
        collapsable: true,
        children: [
            ["/地月空间科学研究前沿在哪里/", "概述"],
        ]
    },
    {
        title: "地月空间术语词典",
        collapsable: true,
        children: [
            ["/地月空间术语词典/", "概述"],
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
    "/地月空间飞行器在什么轨道上运行/CAPSTONE任务": globalSidebar,
    "/地月空间飞行器在什么轨道上运行/GRAIL-SMART-1任务": globalSidebar,
    "/地月空间飞行器在什么轨道上运行/阿耳忒弥斯计划": globalSidebar,
    "/地月空间飞行器在什么轨道上运行/LONEStar实验": globalSidebar,
    "/地月空间科学研究前沿在哪里/": globalSidebar,
    "/地月空间术语词典/": globalSidebar,
    "/地月空间术语词典/X 射线脉冲星导航": globalSidebar,
    "/资源与工具/": globalSidebar,
    "/资源与工具/数据集下载": globalSidebar,
    "/关于本站/": globalSidebar,
} as SidebarConfig4Multiple;
