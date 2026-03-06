import { SidebarConfig } from "vuepress/config";

// Main sidebar configuration (English)
const mainSidebar = [
    {
        title: "What Is Cislunar Space",
        collapsable: true,
        children: [
            ["/en/what-is-cislunarspace/", "Introduction"],
            ["/en/what-is-cislunarspace/environment", "Cislunar Space Environment"],
        ]
    },
    {
        title: "Cislunar Spacecraft Orbits",
        collapsable: true,
        children: [
            ["/en/cislunar-orbits/", "Introduction"],
        ]
    },
    {
        title: "Research Frontiers",
        collapsable: true,
        children: [
            ["/en/research-frontiers/", "Introduction"],
            ["/en/research-frontiers/directions", "Research Directions"],
            ["/en/research-frontiers/institutions", "Research Institutions"],
            ["/en/research-frontiers/journals-conferences", "Journals & Conferences"],
            ["/en/research-frontiers/major-projects", "Major Projects"],
        ]
    },
];

// Glossary sidebar (English)
const glossarySidebar = [
    {
        title: "Cislunar Space Glossary",
        collapsable: false,
        children: [
            ["/en/glossary/", "Overview"],
            ["/en/glossary/cr3bp", "Circular Restricted Three-Body Problem"],
            ["/en/glossary/xray-pulsar-navigation", "X-ray Pulsar Navigation"],
        ]
    }
];

// Resources & Tools sidebar (English)
const resourcesToolsSidebar = [
    {
        title: "Resources & Tools",
        collapsable: false,
        children: [
            ["/en/resources-tools/", "Overview"],
            ["/en/resources-tools/datasets", "Datasets"],
        ]
    }
];

// VuePress 1.x multi-sidebar config
const sidebarConfigEn: SidebarConfig = {
    "/en/glossary/": glossarySidebar,
    "/en/resources-tools/": resourcesToolsSidebar,
    "/en/what-is-cislunarspace/": mainSidebar,
    "/en/cislunar-orbits/": mainSidebar,
    "/en/research-frontiers/": mainSidebar,
    "/en/": mainSidebar,
};

export default sidebarConfigEn;
