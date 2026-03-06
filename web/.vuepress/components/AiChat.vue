<template>
  <div class="ai-chat-container">
    <!-- Toolbar -->
    <div class="chat-toolbar">
      <div class="toolbar-title">{{ t('toolbarTitle') }}</div>
      <div class="toolbar-actions">
        <button class="toolbar-btn" @click="startNewChat" :title="t('newChat')">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 5v14M5 12h14"/>
          </svg>
          <span>{{ t('newChat') }}</span>
        </button>
        <button class="toolbar-btn" @click="showHistory = !showHistory" :title="t('history')">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>
          </svg>
          <span>{{ t('history') }}</span>
        </button>
      </div>
    </div>
    <!-- History panel -->
    <div v-if="showHistory" class="history-panel">
      <div class="history-header">
        <h3>{{ t('historyTitle') }}</h3>
        <button class="history-close-btn" @click="showHistory = false">&times;</button>
      </div>
      <div v-if="historyList.length === 0" class="history-empty">{{ t('noHistory') }}</div>
      <div v-else class="history-list">
        <div
          v-for="(item, idx) in historyList"
          :key="item.id"
          :class="['history-item', currentSessionId === item.id ? 'history-item-active' : '']"
          @click="loadSession(item.id)"
        >
          <div class="history-item-title">{{ item.title }}</div>
          <div class="history-item-meta">
            <span>{{ item.count }} {{ t('messages') }}</span>
            <span>{{ formatTime(item.time) }}</span>
          </div>
          <button class="history-delete-btn" @click.stop="deleteSession(item.id)" :title="t('delete')">&times;</button>
        </div>
      </div>
      <div v-if="historyList.length > 0" class="history-footer">
        <button class="history-clear-btn" @click="clearAllHistory">{{ t('clearAll') }}</button>
      </div>
    </div>
    <div class="chat-messages" ref="messagesContainer">
      <div v-if="messages.length === 0" class="chat-welcome">
        <h2>{{ t('welcomeTitle') }}</h2>
        <p>{{ t('welcomeDesc') }}</p>
        <div class="suggested-questions">
          <button
            v-for="(q, i) in suggestedQuestions"
            :key="i"
            class="suggested-btn"
            @click="sendSuggested(q)"
          >{{ q }}</button>
        </div>
      </div>
      <div
        v-for="(msg, index) in messages"
        :key="index"
        :class="['chat-message', msg.role === 'user' ? 'user-message' : 'assistant-message']"
      >
        <div class="message-avatar">
          <span v-if="msg.role === 'user'">🧑</span>
          <span v-else>🤖</span>
        </div>
        <div class="message-content" v-html="renderMarkdown(msg.content)"></div>
      </div>
      <div v-if="isLoading" class="chat-message assistant-message">
        <div class="message-avatar"><span>🤖</span></div>
        <div class="message-content typing-indicator">
          <span></span><span></span><span></span>
        </div>
      </div>
    </div>
    <div class="chat-input-area">
      <textarea
        v-model="userInput"
        @keydown.enter.exact="handleEnter"
        :placeholder="t('inputPlaceholder')"
        rows="1"
        ref="inputArea"
        :disabled="isLoading"
      ></textarea>
      <button class="send-btn" @click="sendMessage" :disabled="isLoading || !userInput.trim()">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
          <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script>
import katex from 'katex'
import 'katex/dist/katex.min.css'

function renderMd(text) {
  var lines = text.split('\n')
  var html = []
  var i = 0

  while (i < lines.length) {
    var line = lines[i]

    // Empty line — skip
    if (line.trim() === '') {
      i++
      continue
    }

    // Code block (fenced)
    if (/^```/.test(line.trim())) {
      var lang = line.trim().replace(/^```/, '').trim()
      var codeLines = []
      i++
      while (i < lines.length && !/^```\s*$/.test(lines[i].trim())) {
        codeLines.push(lines[i])
        i++
      }
      i++ // skip closing ```
      html.push('<pre><code class="language-' + escHtml(lang) + '">' + escHtml(codeLines.join('\n')) + '</code></pre>')
      continue
    }

    // Heading
    var headMatch = line.match(/^(#{1,6})\s+(.+)$/)
    if (headMatch) {
      var level = headMatch[1].length
      html.push('<h' + level + '>' + inlineMd(headMatch[2].trim()) + '</h' + level + '>')
      i++
      continue
    }

    // Horizontal rule
    if (/^\s*([-*_])\s*\1\s*\1[\s\-*_]*$/.test(line)) {
      html.push('<hr>')
      i++
      continue
    }

    // Table: collect consecutive lines starting with |
    if (/^\|.+\|/.test(line.trim())) {
      var tableLines = []
      while (i < lines.length && /^\|.+\|/.test(lines[i].trim())) {
        tableLines.push(lines[i].trim())
        i++
      }
      if (tableLines.length >= 2 && /^[\s|:|-]+$/.test(tableLines[1])) {
        var tableHtml = '<table>'
        var hCells = tableLines[0].split('|').filter(function(c) { return c.trim() !== '' })
        tableHtml += '<thead><tr>'
        for (var h = 0; h < hCells.length; h++) tableHtml += '<th>' + inlineMd(hCells[h].trim()) + '</th>'
        tableHtml += '</tr></thead><tbody>'
        for (var r = 2; r < tableLines.length; r++) {
          var cells = tableLines[r].split('|').filter(function(c) { return c.trim() !== '' })
          tableHtml += '<tr>'
          for (var c = 0; c < cells.length; c++) tableHtml += '<td>' + inlineMd(cells[c].trim()) + '</td>'
          tableHtml += '</tr>'
        }
        tableHtml += '</tbody></table>'
        html.push(tableHtml)
      } else {
        // Not a real table, treat as paragraphs
        for (var t = 0; t < tableLines.length; t++) {
          html.push('<p>' + inlineMd(tableLines[t]) + '</p>')
        }
      }
      continue
    }

    // Blockquote: collect consecutive > lines
    if (/^>\s?/.test(line)) {
      var bqLines = []
      while (i < lines.length && /^>\s?/.test(lines[i])) {
        bqLines.push(lines[i].replace(/^>\s?/, ''))
        i++
      }
      html.push('<blockquote>' + renderMd(bqLines.join('\n')) + '</blockquote>')
      continue
    }

    // Unordered list: collect consecutive - / * / + items (with possible continuation lines)
    if (/^\s*[-*+]\s/.test(line)) {
      var ulItems = []
      while (i < lines.length && /^\s*[-*+]\s/.test(lines[i])) {
        ulItems.push(lines[i].replace(/^\s*[-*+]\s/, '').trim())
        i++
      }
      html.push('<ul>')
      for (var u = 0; u < ulItems.length; u++) {
        html.push('<li>' + inlineMd(ulItems[u]) + '</li>')
      }
      html.push('</ul>')
      continue
    }

    // Ordered list: collect consecutive numbered items
    if (/^\s*\d+[.)]\s/.test(line)) {
      var olItems = []
      while (i < lines.length && /^\s*\d+[.)]\s/.test(lines[i])) {
        olItems.push(lines[i].replace(/^\s*\d+[.)]\s/, '').trim())
        i++
      }
      html.push('<ol>')
      for (var o = 0; o < olItems.length; o++) {
        html.push('<li>' + inlineMd(olItems[o]) + '</li>')
      }
      html.push('</ol>')
      continue
    }

    // Paragraph: collect consecutive non-empty, non-special lines
    var paraLines = []
    while (i < lines.length && lines[i].trim() !== '' &&
      !/^```/.test(lines[i].trim()) &&
      !/^#{1,6}\s/.test(lines[i]) &&
      !/^\|.+\|/.test(lines[i].trim()) &&
      !/^>\s?/.test(lines[i]) &&
      !/^\s*[-*+]\s/.test(lines[i]) &&
      !/^\s*\d+[.)]\s/.test(lines[i]) &&
      !/^\s*([-*_])\s*\1\s*\1[\s\-*_]*$/.test(lines[i])
    ) {
      paraLines.push(lines[i])
      i++
    }
    if (paraLines.length > 0) {
      html.push('<p>' + inlineMd(paraLines.join('<br>')) + '</p>')
    }
  }

  return html.join('\n')
}

function inlineMd(text) {
  // Inline code
  text = text.replace(/`([^`]+)`/g, function(_, code) {
    return '<code>' + escHtml(code) + '</code>'
  })
  // Bold
  text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  // Italic
  text = text.replace(/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/g, '<em>$1</em>')
  // Links
  text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
  return text
}

function escHtml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')
}

export default {
  name: 'AiChat',
  data() {
    return {
      userInput: '',
      messages: [],
      isLoading: false,
      config: null,
      showHistory: false,
      historyList: [],
      currentSessionId: null,
      abortController: null,
      suggestedQuestions: []
    }
  },
  computed: {
    isEn() {
      return (this.$localePath || '/') === '/en/'
    }
  },
  async mounted() {
    this.suggestedQuestions = this.isEn
      ? [
          'What is cislunar space?',
          'What is the CR3BP model?',
          'What are the characteristics of NRHO orbits?',
          'What are the uses of Lagrange points?'
        ]
      : [
          '什么是地月空间？',
          'CR3BP 模型是什么？',
          'NRHO 轨道有哪些特点？',
          '拉格朗日点有什么用途？'
        ]
    await this.loadConfig()
    this.loadHistoryList()
    // Start or resume the latest session
    if (this.historyList.length > 0) {
      this.loadSession(this.historyList[0].id)
    } else {
      this.createSession()
    }
  },
  watch: {
    messages: {
      deep: true,
      handler() {
        this.saveCurrentSession()
      }
    },
    isEn: {
      immediate: true,
      handler(newVal, oldVal) {
        if (newVal !== oldVal) {
          // Update suggested questions when language changes
          this.suggestedQuestions = newVal
            ? [
                'What is cislunar space?',
                'What is the CR3BP model?',
                'What are the characteristics of NRHO orbits?',
                'What are the uses of Lagrange points?'
              ]
            : [
                '什么是地月空间？',
                'CR3BP 模型是什么？',
                'NRHO 轨道有哪些特点？',
                '拉格朗日点有什么用途？'
              ]
          
          // Update system prompt when language changes
          if (this.config) {
            this.config.systemPrompt = this.getSystemPrompt()
          }
        }
      }
    }
  },
  methods: {
    // --- i18n helper ---
    t(key) {
      var strings = {
        toolbarTitle: { zh: 'AI 问答助手', en: 'AI Chat Assistant' },
        newChat: { zh: '新对话', en: 'New Chat' },
        history: { zh: '历史记录', en: 'History' },
        historyTitle: { zh: '历史对话', en: 'Chat History' },
        noHistory: { zh: '暂无历史记录', en: 'No history yet' },
        messages: { zh: '条消息', en: 'messages' },
        delete: { zh: '删除', en: 'Delete' },
        clearAll: { zh: '清空所有记录', en: 'Clear All' },
        welcomeTitle: { zh: '地月空间 AI 问答助手', en: 'Cislunar Space AI Assistant' },
        welcomeDesc: {
          zh: '你好！我是地月空间入门指南的 AI 助手，可以回答关于地月空间、轨道动力学、航天器导航等方面的问题。',
          en: 'Hello! I am the AI assistant for the Cislunar Space Beginner\'s Guide. I can answer questions about cislunar space, orbital dynamics, spacecraft navigation, and more.'
        },
        inputPlaceholder: { zh: '输入你的问题...', en: 'Type your question...' }
      }
      var item = strings[key]
      if (!item) return key
      return this.isEn ? item.en : item.zh
    },

    // --- Session / History ---
    createSession() {
      this.currentSessionId = 'chat_' + Date.now()
      this.messages = []
    },

    saveCurrentSession() {
      if (!this.currentSessionId || this.messages.length === 0) return
      var firstUserMsg = this.messages.find(function(m) { return m.role === 'user' })
      var title = firstUserMsg ? firstUserMsg.content.slice(0, 30) : (this.isEn ? 'New Chat' : '新对话')
      var session = {
        id: this.currentSessionId,
        title: title,
        messages: this.messages,
        time: Date.now(),
        count: this.messages.length
      }
      try {
        localStorage.setItem(this.currentSessionId, JSON.stringify(session))
        this.loadHistoryList()
      } catch (e) { /* localStorage full or unavailable */ }
    },

    loadHistoryList() {
      var list = []
      try {
        for (var i = 0; i < localStorage.length; i++) {
          var key = localStorage.key(i)
          if (key && key.indexOf('chat_') === 0) {
            var raw = localStorage.getItem(key)
            if (raw) {
              var parsed = JSON.parse(raw)
              list.push({ id: parsed.id, title: parsed.title, time: parsed.time, count: parsed.count })
            }
          }
        }
      } catch (e) { /* ignore */ }
      list.sort(function(a, b) { return b.time - a.time })
      this.historyList = list
    },

    loadSession(id) {
      // Abort any ongoing request
      if (this.abortController) {
        this.abortController.abort()
        this.abortController = null
      }
      this.isLoading = false
      try {
        var raw = localStorage.getItem(id)
        if (raw) {
          var session = JSON.parse(raw)
          this.currentSessionId = session.id
          this.messages = session.messages || []
          this.showHistory = false
          this.scrollToBottom()
        }
      } catch (e) { /* ignore */ }
    },

    deleteSession(id) {
      try { localStorage.removeItem(id) } catch (e) { /* ignore */ }
      if (this.currentSessionId === id) {
        this.createSession()
      }
      this.loadHistoryList()
    },

    clearAllHistory() {
      var keys = []
      try {
        for (var i = 0; i < localStorage.length; i++) {
          var key = localStorage.key(i)
          if (key && key.indexOf('chat_') === 0) keys.push(key)
        }
        for (var k = 0; k < keys.length; k++) localStorage.removeItem(keys[k])
      } catch (e) { /* ignore */ }
      this.createSession()
      this.loadHistoryList()
    },

    startNewChat() {
      // Abort any ongoing streaming request
      if (this.abortController) {
        this.abortController.abort()
        this.abortController = null
      }
      this.isLoading = false
      this.saveCurrentSession()
      this.createSession()
      this.showHistory = false
      this.scrollToBottom()
    },

    formatTime(ts) {
      if (!ts) return ''
      var d = new Date(ts)
      var mm = d.getMonth() + 1
      var dd = d.getDate()
      var hh = d.getHours()
      var mi = d.getMinutes()
      return mm + '/' + dd + ' ' + (hh < 10 ? '0' : '') + hh + ':' + (mi < 10 ? '0' : '') + mi
    },

    // --- Config ---
    async loadConfig() {
      try {
        const url = this.$withBase
          ? this.$withBase('/ai-chat-config.json')
          : '/ai-chat-config.json'
        const res = await fetch(url)
        if (!res.ok) {
          console.error('AI chat config fetch failed:', res.status, res.statusText)
          return
        }
        const text = await res.text()
        try {
          this.config = JSON.parse(text)
          // Override system prompt based on language
          this.config.systemPrompt = this.getSystemPrompt()
        } catch (parseErr) {
          console.error('AI chat config JSON parse error:', parseErr, 'Response:', text.slice(0, 200))
        }
      } catch (e) {
        console.error('Failed to load AI chat config:', e)
      }
    },

    getSystemPrompt() {
      if (this.isEn) {
        return `You are the AI assistant for the "Cislunar Space Beginner's Guide" website (https://cislunarspace.cn/). The main content of the website includes:

## Website Structure
- Homepage: https://cislunarspace.cn/
- English homepage: https://cislunarspace.cn/en/
- What is Cislunar Space: https://cislunarspace.cn/en/what-is-cislunarspace/
  - Cislunar Space Environment: https://cislunarspace.cn/en/what-is-cislunarspace/environment.html
- Cislunar Glossary: https://cislunarspace.cn/en/glossary/
  - CR3BP (Circular Restricted Three-Body Problem): https://cislunarspace.cn/en/glossary/cr3bp.html
  - X-ray Pulsar Navigation: https://cislunarspace.cn/en/glossary/xray-pulsar-navigation.html
- Cislunar Orbits: https://cislunarspace.cn/en/cislunar-orbits/
- Resources & Tools: https://cislunarspace.cn/en/resources-tools/
  - Datasets: https://cislunarspace.cn/en/resources-tools/datasets.html
- Research Frontiers: https://cislunarspace.cn/en/research-frontiers/
  - Research Directions: https://cislunarspace.cn/en/research-frontiers/directions.html
  - Research Institutions: https://cislunarspace.cn/en/research-frontiers/institutions.html
  - Journals & Conferences: https://cislunarspace.cn/en/research-frontiers/journals-conferences.html
  - Major Projects: https://cislunarspace.cn/en/research-frontiers/major-projects.html

## Your Responsibilities
Based on the website content and your own knowledge, answer user questions about cislunar space, including but not limited to:
- Definition, scope, and environmental characteristics of cislunar space
- Orbital dynamics fundamentals (CR3BP, Lagrange points, NRHO, Halo orbits, etc.)
- Spacecraft navigation and guidance (XNAV, pulsar navigation, etc.)
- Lunar exploration missions and the Artemis program
- Related research institutions, journals/conferences, and major engineering projects

## Answer Requirements
1. Use English to answer, with concise, accurate, and professional language
2. Include relevant website page links in your answers for users to easily navigate to detailed content
3. If a question goes beyond the website content, you can answer based on your knowledge, but indicate that this is not from the website
4. For mathematical formulas, use LaTeX format (wrap inline formulas with $, wrap block-level formulas with $$)
5. Make good use of Markdown formatting (headings, lists, tables, code blocks, etc.) to make answers well-structured
6. Maintain a friendly and patient tone`
      } else {
        return `你是“地月空间入门指南”网站（https://cislunarspace.cn/）的 AI 问答助手。该网站的主要内容包括：

## 网站结构
- 首页：https://cislunarspace.cn/
- 什么是地月空间：https://cislunarspace.cn/what-is-cislunarspace/
  - 地月空间环境：https://cislunarspace.cn/what-is-cislunarspace/environment.html
- 地月空间术语词典：https://cislunarspace.cn/glossary/
  - CR3BP（圆型限制性三体问题）：https://cislunarspace.cn/glossary/cr3bp.html
  - X射线脉冲星导航：https://cislunarspace.cn/glossary/xray-pulsar-navigation.html
- 地月轨道：https://cislunarspace.cn/cislunar-orbits/
- 资源与工具：https://cislunarspace.cn/resources-tools/
  - 数据集：https://cislunarspace.cn/resources-tools/datasets.html
- 研究前沿：https://cislunarspace.cn/research-frontiers/
  - 研究方向：https://cislunarspace.cn/research-frontiers/directions.html
  - 研究机构：https://cislunarspace.cn/research-frontiers/institutions.html
  - 期刊与会议：https://cislunarspace.cn/research-frontiers/journals-conferences.html
  - 重大工程项目：https://cislunarspace.cn/research-frontiers/major-projects.html

## 你的职责
基于网站内容和你自身知识，为用户解答关于地月空间（cislunar space）的相关问题，包括但不限于：
- 地月空间的定义、范围与环境特征
- 轨道动力学基础（CR3BP、拉格朗日点、NRHO、Halo 轨道等）
- 航天器导航与制导（XNAV、脉冲星导航等）
- 月球探测任务与阿耳忒弥斯计划
- 相关研究机构、期刊会议和重大工程项目

## 回答要求
1. 使用中文回答，语言简洁、准确、专业
2. 在回答中引用网站相关页面链接，方便用户跳转查看详细内容
3. 如果问题超出网站内容范围，可以基于你的知识回答，但要说明这不是网站上的内容
4. 对于数学公式，使用 LaTeX 格式（用 $ 包裹行内公式，用 $$ 包裹块级公式）
5. 善用 Markdown 格式（标题、列表、表格、代码块等）使回答结构清晰
6. 保持友好和耐心的语气`
      }
    },

    renderMarkdown(text) {
      if (!text) return ''
      try {
        // Protect LaTeX formulas from marked by replacing them with placeholders
        const placeholders = []
        let processed = text

        // Block formulas: $$$$ ... $$$$ (quad dollar)
        processed = processed.replace(/\$\$\$\$([\s\S]*?)\$\$\$\$/g, (_, tex) => {
          const id = placeholders.length
          try {
            placeholders.push(katex.renderToString(tex.trim(), { displayMode: true, throwOnError: false }))
          } catch (e) {
            placeholders.push(`<span class="katex-error">${tex}</span>`)
          }
          return `%%LATEX_${id}%%`
        })

        // Block formulas: $$ ... $$
        processed = processed.replace(/\$\$([\s\S]*?)\$\$/g, (_, tex) => {
          const id = placeholders.length
          try {
            placeholders.push(katex.renderToString(tex.trim(), { displayMode: true, throwOnError: false }))
          } catch (e) {
            placeholders.push(`<span class="katex-error">${tex}</span>`)
          }
          return `%%LATEX_${id}%%`
        })

        // Block formulas: \[ ... \]
        processed = processed.replace(/\\\[([\s\S]*?)\\\]/g, (_, tex) => {
          const id = placeholders.length
          try {
            placeholders.push(katex.renderToString(tex.trim(), { displayMode: true, throwOnError: false }))
          } catch (e) {
            placeholders.push(`<span class="katex-error">${tex}</span>`)
          }
          return `%%LATEX_${id}%%`
        })

        // Inline formulas: \( ... \)
        processed = processed.replace(/\\\(([\s\S]*?)\\\)/g, (_, tex) => {
          const id = placeholders.length
          try {
            placeholders.push(katex.renderToString(tex.trim(), { displayMode: false, throwOnError: false }))
          } catch (e) {
            placeholders.push(`<span class="katex-error">${tex}</span>`)
          }
          return `%%LATEX_${id}%%`
        })

        // Inline formulas: $ ... $ (single dollar, not preceded/followed by space+dollar)
        processed = processed.replace(/(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)/g, (_, tex) => {
          const id = placeholders.length
          try {
            placeholders.push(katex.renderToString(tex.trim(), { displayMode: false, throwOnError: false }))
          } catch (e) {
            placeholders.push(`<span class="katex-error">${tex}</span>`)
          }
          return `%%LATEX_${id}%%`
        })

        // Run markdown renderer on the processed text
        let html = renderMd(processed)

        // Restore LaTeX placeholders
        html = html.replace(/%%LATEX_(\d+)%%/g, (_, id) => placeholders[parseInt(id)])

        return html
      } catch (e) {
        return text.replace(/\n/g, '<br>')
      }
    },

    handleEnter(e) {
      if (!e.shiftKey) {
        e.preventDefault()
        this.sendMessage()
      }
    },

    sendSuggested(question) {
      this.userInput = question
      this.sendMessage()
    },

    async sendMessage() {
      const text = this.userInput.trim()
      if (!text || this.isLoading) return
      if (!this.config) {
        this.messages.push({
          role: 'assistant',
          content: this.isEn
            ? '⚠️ AI configuration failed to load. Please contact the administrator to check the `/ai-chat-config.json` file.'
            : '⚠️ AI 配置加载失败，请联系管理员检查 `/ai-chat-config.json` 配置文件。'
        })
        return
      }

      this.messages.push({ role: 'user', content: text })
      this.userInput = ''
      this.isLoading = true
      this.scrollToBottom()

      // Create abort controller for this request
      this.abortController = new AbortController()
      const signal = this.abortController.signal
      const sessionId = this.currentSessionId

      try {
        const apiMessages = []

        // System prompt from config
        if (this.config.systemPrompt) {
          apiMessages.push({ role: 'system', content: this.config.systemPrompt })
        }

        // Conversation history (last N turns to stay within context limits)
        const maxHistory = this.config.maxHistoryTurns || 10
        const recentMessages = this.messages.slice(-maxHistory * 2)
        for (const msg of recentMessages) {
          apiMessages.push({ role: msg.role, content: msg.content })
        }

        const requestBody = {
          model: this.config.model,
          messages: apiMessages,
          temperature: this.config.temperature ?? 0.7,
          stream: !!this.config.stream
        }

        const headers = {
          'Content-Type': 'application/json'
        }
        if (this.config.apiKey) {
          headers['Authorization'] = `Bearer ${this.config.apiKey}`
        }

        const response = await fetch(this.config.apiEndpoint, {
          method: 'POST',
          headers,
          body: JSON.stringify(requestBody),
          signal
        })

        if (!response.ok) {
          throw new Error(this.isEn ? `API request failed: ${response.status} ${response.statusText}` : `API 请求失败: ${response.status} ${response.statusText}`)
        }

        if (this.config.stream && response.body) {
          // Streaming response
          this.messages.push({ role: 'assistant', content: '' })
          const assistantIndex = this.messages.length - 1
          const reader = response.body.getReader()
          const decoder = new TextDecoder()
          let buffer = ''

          while (true) {
            const { done, value } = await reader.read()
            if (done) break
            // Stop writing if session has changed
            if (this.currentSessionId !== sessionId) {
              reader.cancel()
              break
            }
            buffer += decoder.decode(value, { stream: true })
            const lines = buffer.split('\n')
            buffer = lines.pop() || ''

            for (const line of lines) {
              const trimmed = line.trim()
              if (!trimmed || !trimmed.startsWith('data:')) continue
              const data = trimmed.slice(5).trim()
              if (data === '[DONE]') continue
              try {
                const parsed = JSON.parse(data)
                const delta = parsed.choices?.[0]?.delta?.content
                if (delta) {
                  this.$set(this.messages, assistantIndex, {
                    role: 'assistant',
                    content: this.messages[assistantIndex].content + delta
                  })
                  this.scrollToBottom()
                }
              } catch (e) {
                // skip unparseable chunks
              }
            }
          }
        } else {
          // Non-streaming response
          const data = await response.json()
          if (this.currentSessionId !== sessionId) return
          const content = data.choices?.[0]?.message?.content || (this.isEn ? 'Sorry, no valid response received.' : '抱歉，未获取到有效回复。')
          this.messages.push({ role: 'assistant', content })
        }
      } catch (error) {
        if (error.name === 'AbortError') return
        if (this.currentSessionId !== sessionId) return
        this.messages.push({
          role: 'assistant',
          content: this.isEn ? `⚠️ Request error: ${error.message}` : `⚠️ 请求出错: ${error.message}`
        })
      } finally {
        if (this.currentSessionId === sessionId) {
          this.isLoading = false
          this.abortController = null
        }
        this.scrollToBottom()
      }
    },

    scrollToBottom() {
      this.$nextTick(() => {
        const container = this.$refs.messagesContainer
        if (container) {
          container.scrollTop = container.scrollHeight
        }
      })
    }
  }
}
</script>

<style scoped>
.ai-chat-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 8rem);
  max-width: 900px;
  margin: 0 auto;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  background: #fff;
  position: relative;
}

/* Toolbar */
.chat-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.6rem 1rem;
  border-bottom: 1px solid #e2e8f0;
  background: #fff;
  flex-shrink: 0;
}

.toolbar-title {
  font-weight: 600;
  font-size: 1rem;
  color: #2d3748;
}

.toolbar-actions {
  display: flex;
  gap: 0.4rem;
}

.toolbar-btn {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.35rem 0.7rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #fff;
  color: #4a5568;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}

.toolbar-btn:hover {
  background: #f7fafc;
  border-color: #3eaf7c;
  color: #3eaf7c;
}

/* History panel */
.history-panel {
  position: absolute;
  top: 44px;
  right: 0;
  width: 320px;
  max-height: calc(100% - 44px);
  background: #fff;
  border-left: 1px solid #e2e8f0;
  box-shadow: -4px 0 12px rgba(0,0,0,0.08);
  z-index: 10;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.history-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e2e8f0;
}

.history-header h3 {
  margin: 0;
  font-size: 0.95rem;
  color: #2d3748;
  border-bottom: none;
}

.history-close-btn {
  border: none;
  background: none;
  font-size: 1.4rem;
  cursor: pointer;
  color: #a0aec0;
  line-height: 1;
  padding: 0 0.2rem;
}

.history-close-btn:hover {
  color: #e53e3e;
}

.history-empty {
  padding: 2rem 1rem;
  text-align: center;
  color: #a0aec0;
  font-size: 0.9rem;
}

.history-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem 0;
}

.history-item {
  padding: 0.6rem 1rem;
  cursor: pointer;
  transition: background 0.15s;
  position: relative;
  border-bottom: 1px solid #f0f0f0;
}

.history-item:hover {
  background: #f7fafc;
}

.history-item-active {
  background: #f0faf5;
  border-left: 3px solid #3eaf7c;
}

.history-item-title {
  font-size: 0.9rem;
  color: #2d3748;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding-right: 1.5rem;
}

.history-item-meta {
  display: flex;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: #a0aec0;
  margin-top: 0.2rem;
}

.history-delete-btn {
  position: absolute;
  right: 0.6rem;
  top: 50%;
  transform: translateY(-50%);
  border: none;
  background: none;
  font-size: 1.2rem;
  color: #cbd5e0;
  cursor: pointer;
  opacity: 0;
  transition: all 0.15s;
  padding: 0 0.3rem;
}

.history-item:hover .history-delete-btn {
  opacity: 1;
}

.history-delete-btn:hover {
  color: #e53e3e;
}

.history-footer {
  padding: 0.5rem 1rem;
  border-top: 1px solid #e2e8f0;
  text-align: center;
}

.history-clear-btn {
  border: none;
  background: none;
  color: #e53e3e;
  font-size: 0.85rem;
  cursor: pointer;
  padding: 0.3rem 0.6rem;
}

.history-clear-btn:hover {
  text-decoration: underline;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  scroll-behavior: smooth;
}

.chat-welcome {
  text-align: center;
  padding: 2rem 1rem;
  color: #4a5568;
}

.welcome-logo {
  width: 64px;
  height: 64px;
  margin-bottom: 1rem;
}

.chat-welcome h2 {
  margin-bottom: 0.5rem;
  color: #2d3748;
  border-bottom: none;
}

.chat-welcome p {
  color: #718096;
  margin-bottom: 1.5rem;
}

.suggested-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
}

.suggested-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #cbd5e0;
  border-radius: 20px;
  background: #f7fafc;
  color: #4a5568;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.suggested-btn:hover {
  background: #3eaf7c;
  color: #fff;
  border-color: #3eaf7c;
}

.chat-message {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.user-message {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  flex-shrink: 0;
  background: #f0f0f0;
}

.user-message .message-avatar {
  background: #3eaf7c;
}

.message-content {
  max-width: 75%;
  padding: 0.75rem 1rem;
  border-radius: 12px;
  line-height: 1.6;
  font-size: 0.95rem;
  word-break: break-word;
}

.user-message .message-content {
  background: #3eaf7c;
  color: #fff;
  border-bottom-right-radius: 4px;
}

.assistant-message .message-content {
  background: #f7fafc;
  color: #2d3748;
  border-bottom-left-radius: 4px;
  border: 1px solid #e2e8f0;
}

.message-content >>> h1,
.message-content >>> h2,
.message-content >>> h3,
.message-content >>> h4 {
  margin: 0.6rem 0 0.3rem;
  font-weight: 600;
  line-height: 1.4;
  border-bottom: none;
}

.message-content >>> h1 { font-size: 1.3em; }
.message-content >>> h2 { font-size: 1.15em; }
.message-content >>> h3 { font-size: 1.05em; }

.message-content >>> p {
  margin: 0.4rem 0;
}

.message-content >>> ul,
.message-content >>> ol {
  padding-left: 1.5rem;
  margin: 0.4rem 0;
}

.message-content >>> li {
  margin: 0.15rem 0;
}

.message-content >>> blockquote {
  margin: 0.5rem 0;
  padding: 0.3rem 0.8rem;
  border-left: 4px solid #3eaf7c;
  background: #f0faf5;
  color: #4a5568;
}

.message-content >>> pre {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 0.85rem 1rem;
  border-radius: 8px;
  overflow-x: auto;
  margin: 0.5rem 0;
  font-size: 0.85em;
  line-height: 1.5;
}

.message-content >>> pre code {
  background: none;
  color: inherit;
  padding: 0;
  border-radius: 0;
  font-size: inherit;
}

.message-content >>> code {
  background: #edf2f7;
  color: #e53e3e;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  font-size: 0.85em;
}

.message-content >>> table {
  border-collapse: collapse;
  margin: 0.5rem 0;
  width: 100%;
  font-size: 0.9em;
}

.message-content >>> th,
.message-content >>> td {
  border: 1px solid #e2e8f0;
  padding: 0.4rem 0.6rem;
  text-align: left;
}

.message-content >>> th {
  background: #f7fafc;
  font-weight: 600;
}

.message-content >>> a {
  color: #3eaf7c;
  text-decoration: underline;
}

.message-content >>> hr {
  border: none;
  border-top: 1px solid #e2e8f0;
  margin: 0.5rem 0;
}

.message-content >>> strong {
  font-weight: 600;
}

.user-message .message-content >>> code {
  background: rgba(255,255,255,0.2);
  color: #fff;
}

.user-message .message-content >>> a {
  color: #fff;
}

.message-content >>> .katex-display {
  margin: 0.5rem 0;
  overflow-x: auto;
  overflow-y: hidden;
}

.message-content >>> .katex {
  font-size: 1.05em;
}

.message-content >>> .katex-error {
  color: #e53e3e;
  font-family: monospace;
  font-size: 0.85em;
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 0.75rem 1rem;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #a0aec0;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
.typing-indicator span:nth-child(3) { animation-delay: 0s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.chat-input-area {
  display: flex;
  align-items: flex-end;
  gap: 0.5rem;
  padding: 1rem;
  border-top: 1px solid #e2e8f0;
  background: #f7fafc;
}

.chat-input-area textarea {
  flex: 1;
  resize: none;
  border: 1px solid #cbd5e0;
  border-radius: 10px;
  padding: 0.65rem 1rem;
  font-size: 0.95rem;
  font-family: inherit;
  line-height: 1.5;
  outline: none;
  transition: border-color 0.2s;
  max-height: 120px;
  overflow-y: auto;
}

.chat-input-area textarea:focus {
  border-color: #3eaf7c;
  box-shadow: 0 0 0 2px rgba(62, 175, 124, 0.15);
}

.send-btn {
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 50%;
  background: #3eaf7c;
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) {
  background: #2d9d6e;
}

.send-btn:disabled {
  background: #cbd5e0;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .ai-chat-container {
    height: calc(100vh - 6rem);
    border-radius: 0;
    border: none;
  }
  .message-content {
    max-width: 85%;
  }
  .toolbar-btn span {
    display: none;
  }
  .history-panel {
    width: 100%;
    border-left: none;
  }
}
</style>
