import { SidebarConfig4Multiple } from "vuepress/config";

import cislunarWhatSideBar from "./sidebars/cislunarWhatSideBar";
// @ts-ignore
export default {
    "/地月空间是什么/": cislunarWhatSideBar,
    "/地月空间飞行器在什么轨道上运行/": [
        "",
        "CAPSTONE任务",
        "GRAIL-SMART-1任务",
        "阿耳忒弥斯计划",
        "LONEStar实验",
    ],
    "/地月空间科学研究前沿在哪里/": [
        "",
    ],
    "/地月空间术语词典/": [
        "",
        "X 射线脉冲星导航",
    ],
    "/资源与工具/": [
        "",
        "数据集下载",
    ],
    "/关于本站/": [
        "",
    ],
    // 主页左侧边栏：显示主要导航
    "/": [
        {
            title: "快速导航",
            children: [
                "/地月空间是什么/",
                "/地月空间飞行器在什么轨道上运行/",
                "/地月空间科学研究前沿在哪里/",
                "/地月空间术语词典/",
                "/资源与工具/",
                "/关于本站/",
            ]
        }
    ],
} as SidebarConfig4Multiple;
