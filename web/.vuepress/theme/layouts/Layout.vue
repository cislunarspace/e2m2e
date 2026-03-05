<template>
  <div
    class="theme-container"
    :class="pageClasses"
    @touchstart="onTouchStart"
    @touchend="onTouchEnd"
  >
    <Navbar
      v-if="shouldShowNavbar"
      @toggle-sidebar="toggleSidebar"
    />

    <div
      class="sidebar-mask"
      @click="toggleSidebar(false)"
    />

    <Sidebar
      :items="sidebarItems"
      @toggle-sidebar="toggleSidebar"
    >
      <template #top>
        <slot name="sidebar-top" />
      </template>
      <template #bottom>
        <slot name="sidebar-bottom" />
      </template>
    </Sidebar>

    <Home v-if="$page.frontmatter.home" />

    <Page
      v-else
      :sidebar-items="sidebarItems"
      :page-sidebar-items="pageSidebarItems"
    >
      <template #top>
        <slot name="page-top" />

      </template>
      <template #bottom>
        <slot name="page-bottom" />
        <Footer />
      </template>
    </Page>

    <PageSidebar
       v-if="shouldShowPageSidebar"
       :page-sidebar-items="pageSidebarItems"
       :sidebar-items="sidebarItems"
    >
      <slot
        name="page-sidebar-top"
        #top
      />
      <slot
        name="page-sidebar-bottom"
        #bottom
      />
    </PageSidebar>
  </div>
</template>

<script>
import Home from '@theme/components/Home.vue'
import Navbar from '@theme/components/Navbar.vue'
import Page from '@theme/components/Page.vue'
import Sidebar from '@theme/components/Sidebar.vue'
import PageSidebar from '@theme/components/ExtraSidebar.vue'
import Footer from "@theme/components/Footer.vue";
import { resolveSidebarItems, resolveHeaders } from '../util'


export default {
  components: { Home, Page, Sidebar, Navbar, PageSidebar, Footer },

  data () {
    return {
      isSidebarOpen: false,
      resizeTimer: null
    }
  },

  computed: {
    shouldShowNavbar () {
      const { themeConfig } = this.$site
      const { frontmatter } = this.$page
      if (
        frontmatter.navbar === false
        || themeConfig.navbar === false) {
        return false
      }
      return (
        this.$title
        || themeConfig.logo
        || themeConfig.repo
        || themeConfig.nav
        || this.$themeLocaleConfig.nav
      )
    },

    shouldShowSidebar () {
      const { frontmatter } = this.$page
      return (
        !frontmatter.home
        && frontmatter.sidebar !== false
        && this.sidebarItems.length
      )
    },

    shouldShowPageSidebar (){
        const { frontmatter } = this.$page

        return (
            false // 隐藏右侧边栏，只保留左侧导航
            && !frontmatter.home
            && frontmatter.sidebar !== false
            && this.pageSidebarItems.length
        )
    },

    sidebarItems () {
      return resolveSidebarItems(
        this.$page,
        this.$page.regularPath,
        this.$site,
        this.$localePath
      )
    },

    pageSidebarItems () {
        return resolveHeaders(this.$page)
    },

    pageClasses () {
      const userPageClass = this.$page.frontmatter.pageClass
      return [
        {
          'no-navbar': !this.shouldShowNavbar,
          'sidebar-open': this.isSidebarOpen,
          'no-sidebar': !this.shouldShowSidebar
        },
        userPageClass
      ]
    }
  },

  mounted () {
    this.updateDesktopSidebarWidth()
    window.addEventListener('resize', this.handleResize)

    this.$router.afterEach(() => {
      this.isSidebarOpen = false
      this.$nextTick(() => this.updateDesktopSidebarWidth())
    })
  },

  beforeDestroy () {
    if (this.resizeTimer) {
      clearTimeout(this.resizeTimer)
      this.resizeTimer = null
    }
    window.removeEventListener('resize', this.handleResize)
  },

  methods: {
    handleResize () {
      if (this.resizeTimer) {
        clearTimeout(this.resizeTimer)
      }
      this.resizeTimer = setTimeout(() => {
        this.updateDesktopSidebarWidth()
      }, 120)
    },

    updateDesktopSidebarWidth () {
      // Desktop only: keep left sidebar width based on longest title text.
      if (window.innerWidth <= 959) {
        document.documentElement.style.removeProperty('--desktop-sidebar-width')
        document.documentElement.style.removeProperty('--desktop-toc-width')
        return
      }

      this.$nextTick(() => {
        const sidebar = document.querySelector('.theme-container .sidebar')
        if (!sidebar) return

        const nodes = sidebar.querySelectorAll('.sidebar-link, .group-label, .sidebar-heading')
        let maxTextWidth = 0
        
        // 临时设置不换行来测量真实宽度
        nodes.forEach((el) => {
          const originalWhiteSpace = el.style.whiteSpace
          el.style.whiteSpace = 'nowrap'
          maxTextWidth = Math.max(maxTextWidth, el.scrollWidth)
          el.style.whiteSpace = originalWhiteSpace
        })

        if (!maxTextWidth) return

        // 只用文字宽度，不加额外空间，最小宽度 160px，最大 520px
        // 加上一些内边距和图标空间
        const width = Math.min(Math.max(maxTextWidth + 32, 160), 520)
        document.documentElement.style.setProperty('--desktop-sidebar-width', `${width}px`)

        // Right TOC sidebar
        const tocBox = document.querySelector('.toc-box')
        if (tocBox) {
          const links = tocBox.querySelectorAll('a')
          let maxTocWidth = 0
          links.forEach((el) => {
            const originalWhiteSpace = el.style.whiteSpace
            el.style.whiteSpace = 'nowrap'
            maxTocWidth = Math.max(maxTocWidth, el.scrollWidth)
            el.style.whiteSpace = originalWhiteSpace
          })
          if (maxTocWidth) {
            // 只用文字宽度，不加额外空间，最小宽度 180px，最大 400px
            // 加上一些内边距
            const tocWidth = Math.min(Math.max(maxTocWidth + 24, 180), 400)
            document.documentElement.style.setProperty('--desktop-toc-width', `${tocWidth}px`)
          }
        }
      })
    },

    toggleSidebar (to) {
      this.isSidebarOpen = typeof to === 'boolean' ? to : !this.isSidebarOpen
      this.$emit('toggle-sidebar', this.isSidebarOpen)
    },

    // side swipe
    onTouchStart (e) {
      this.touchStart = {
        x: e.changedTouches[0].clientX,
        y: e.changedTouches[0].clientY
      }
    },

    onTouchEnd (e) {
      const dx = e.changedTouches[0].clientX - this.touchStart.x
      const dy = e.changedTouches[0].clientY - this.touchStart.y
      if (Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > 40) {
        if (dx > 0 && this.touchStart.x <= 80) {
          this.toggleSidebar(true)
        } else {
          this.toggleSidebar(false)
        }
      }
    }
  }
}
</script>
