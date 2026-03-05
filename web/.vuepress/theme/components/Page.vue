<template>
  <main class="page">
    <slot name="top" />
      <div class="content">
          <div style="width:100%">
              <Content class="theme-default-content custom-content"  />
              <PageEdit style="margin: 0"/>
              <!--      <div class="option-box-toc-fixed">-->
              <!--         -->
              <!--      </div>-->


              <PageNav v-bind="{ sidebarItems }" />
          </div>

          <div class="toc-container-sidebar" ref="tocc">
              <div class="pos-box">
                  <div class="icon-arrow"></div>
                  <div class="scroll-box" style="max-height:86vh">
                      <div style="font-weight:bold;">{{pageSidebarItems[0].title}}</div>
                      <hr/>
                      <div class="toc-box">
                          <PageSidebarToc :depth="0" :items="pageSidebarItems" :sidebarDepth="6"/>
                      </div>
                  </div>
              </div>
          </div>
      </div>

    <slot name="bottom" />
  </main>
</template>

<script>
import PageEdit from '@theme/components/PageEdit.vue'
import PageNav from '@theme/components/PageNav.vue'
import PageSidebarToc from '@theme/components/PageSidebarToc.vue'
export default {
  components: { PageEdit, PageNav, PageSidebarToc },
  props: ['sidebarItems', 'pageSidebarItems'],
}
</script>

<style lang="stylus">
@require '../styles/wrapper.styl'

:root
  --desktop-sidebar-width 20rem

@media (min-width: 960px)
  .theme-container .sidebar
    width var(--desktop-sidebar-width) !important
    
  .theme-container .sidebar .sidebar-link,
  .theme-container .sidebar .group-label,
  .theme-container .sidebar .sidebar-heading
    white-space: nowrap !important
    overflow: hidden
    text-overflow: ellipsis

  .theme-container .page
    padding-left calc(var(--desktop-sidebar-width) + 1.5rem) !important

  .theme-container.no-sidebar .page
    padding-left 0 !important


@media (max-width: 1435px)
  .toc-container-sidebar
    display none !important

@media (max-width: $MQMobile)
  .toc-container-sidebar
    display none
.content-page
  position relative
.custom-content
  max-width none !important
  width 100%
  margin 0 !important
  padding-right 16px !important
.content
  display flex
  align-items flex-start
  justify-content flex-start
  gap 1.5rem
  margin 0 auto
  width 100%
  padding 0 0.75rem
  li, a , p, span
    word-wrap break-word

.content > div:first-child
  flex 1 1 auto
  min-width 0

.theme-default-content
  margin 0 !important

.page
  display block
  position relative
  padding-right 1.25rem
  //height 100vw
  //width 100vw
  //overflow scroll
.toc-container-sidebar
  order 2
  flex 0 0 auto
  width var(--desktop-toc-width, 240px)
  display: block;
  position: relative;
  color $textColor
  top: 80px;
  background transparent
  margin-right: 0;
  margin-left: 0;
  .on
    display: block;
  .pos-box
    position: fixed;
    padding: 16px;
    top 80px;
    height 100vh
    overflow-x hidden
    overflow-y hidden

    .icon-arrow
      position: relative;
      margin-left: -20px;
    .scroll-box
      overflow-x: hidden;
      overflow-y: auto;
      max-height: calc(100vh - 120px);
      padding-right: 8px;
      scrollbar-width: thin;
      scrollbar-color: rgba(0,0,0,0.2) transparent;
      &::-webkit-scrollbar {
        width: 6px;
      }
      &::-webkit-scrollbar-track {
        background: transparent;
      }
      &::-webkit-scrollbar-thumb {
        background-color: rgba(0,0,0,0.2);
        border-radius: 3px;
      }
      & > div:first-child
        overflow-x visible
        white-space: nowrap;
        text-overflow ellipsis
      hr
        margin: 0.5rem 0 1rem 0;
        border: none;
        border-top: 1px solid rgba(0,0,0,0.1);
      .toc-box
        max-height: none;
        overflow-y: visible;
        overflow-x: visible;
        width: 100%;
        min-width: 190px;
        padding-right: 16px;
        -webkit-box-sizing: border-box;
        box-sizing: border-box;
        padding-bottom: 20px;
        a
          white-space: normal;
          word-break: break-word;
          display: inline-block;
          max-width: 100%;
      & > ol
        margin-top: -8px;
        li
          margin-top: 8px;
          line-height: 17px;
          text-align: left;
          overflow: auto;
          text-overflow: ellipsis;
          font-size: 12px;
          white-space: nowrap;
        .sub-box
          margin-top: 0;
        & > ol > li
          padding-left: 15px;

@media (max-width: $MQMobile)
  .page
    padding-right 0
    padding-left 0 !important
  .content
    gap 0
    padding 0 0.85rem
  .custom-content
    max-width 100% !important
    padding-left 0 !important
    padding-right 0 !important

</style>
