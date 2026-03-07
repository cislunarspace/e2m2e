<template>
  <div class="ai-chat-container">
    <div class="chat-toolbar">
      <div class="toolbar-title">{{ t('toolbarTitle') }}</div>
      <button class="toolbar-btn" @click="startNewChat" :disabled="isLoading">
        {{ t('newChat') }}
      </button>
    </div>

    <div class="chat-messages" ref="messagesContainer">
      <div v-if="messages.length === 0" class="chat-welcome">
        <h2>{{ t('welcomeTitle') }}</h2>
        <p>{{ t('welcomeDesc') }}</p>
        <div class="suggested-questions">
          <button
            v-for="(question, index) in suggestedQuestions"
            :key="index"
            class="suggested-btn"
            @click="sendSuggested(question)"
            :disabled="isLoading"
          >
            {{ question }}
          </button>
        </div>
      </div>

      <div
        v-for="(message, index) in messages"
        :key="index"
        :class="['chat-message', message.role === 'user' ? 'user-message' : 'assistant-message']"
      >
        <div class="message-avatar">{{ message.role === 'user' ? 'U' : 'AI' }}</div>
        <div
          v-if="message.role === 'assistant'"
          class="message-content"
          v-html="renderMessageHtml(message, index)"
        ></div>
        <div v-else class="message-content">
          {{ getMessageText(message, index) }}
        </div>
      </div>
    </div>

    <div class="chat-input-area">
      <textarea
        v-model="userInput"
        @keydown.enter.exact.prevent="sendMessage"
        :placeholder="t('inputPlaceholder')"
        :disabled="isLoading || !config"
        rows="3"
      ></textarea>
      <button
        class="send-btn"
        @click="sendMessage"
        :disabled="isLoading || !userInput.trim() || !config"
      >
        {{ t('send') }}
      </button>
    </div>
  </div>
</template>

<script>
import katex from 'katex'
import 'katex/dist/katex.min.css'

import sidebarConfig from '../sidebar.ts'
import sidebarConfigEn from '../sidebar-en.ts'

function normalizeApiEndpoint(rawEndpoint) {
  if (typeof rawEndpoint !== 'string') return '/api/ai/v1/chat/completions'

  const endpoint = rawEndpoint.trim()
  if (!endpoint) return '/api/ai/v1/chat/completions'

  if (/^https?:\/\//i.test(endpoint)) {
    try {
      const url = new URL(endpoint, window.location.origin)
      if (url.origin === window.location.origin) {
        return url.pathname + url.search + url.hash
      }
    } catch (e) {
      return '/api/ai/v1/chat/completions'
    }

    return '/api/ai/v1/chat/completions'
  }

  return endpoint.startsWith('/') ? endpoint : `/${endpoint}`
}

function sanitizeClientConfig(config) {
  const nextConfig = Object.assign({}, config || {})
  delete nextConfig.apiKey
  nextConfig.apiEndpoint = normalizeApiEndpoint(nextConfig.apiEndpoint)
  return nextConfig
}

function normalizeDocPath(path) {
  if (typeof path !== 'string' || !path.trim()) return ''

  const trimmed = path.trim()
  if (/^https?:\/\//i.test(trimmed)) return trimmed
  if (trimmed === '/') return trimmed
  if (/[.#?]$/.test(trimmed)) return trimmed
  return trimmed.endsWith('/') ? trimmed : `${trimmed}/`
}

function collectSidebarChildren(children, entries) {
  if (!Array.isArray(children)) return

  for (const child of children) {
    if (Array.isArray(child) && child.length >= 2) {
      const path = normalizeDocPath(child[0])
      const title = child[1]
      if (path && title) {
        entries.push({ title, path })
      }
      continue
    }

    if (child && typeof child === 'object') {
      const path = normalizeDocPath(child.path)
      if (path && child.title) {
        entries.push({ title: child.title, path })
      }

      collectSidebarChildren(child.children, entries)
    }
  }
}

function buildSidebarEntries(sidebarConfigObject) {
  const rawEntries = []
  const groups = Object.values(sidebarConfigObject || {})

  for (const group of groups) {
    if (Array.isArray(group)) {
      collectSidebarChildren(group, rawEntries)
    }
  }

  const uniqueEntries = []
  const seen = new Set()

  for (const entry of rawEntries) {
    const key = `${entry.title}@@${entry.path}`
    if (seen.has(key)) continue
    seen.add(key)
    uniqueEntries.push(entry)
  }

  return uniqueEntries
}

function escapeHtml(text) {
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

function renderKatex(text) {
  const placeholders = []
  let nextText = String(text || '')

  function pushPlaceholder(source, displayMode) {
    const id = placeholders.length

    try {
      placeholders.push(katex.renderToString(source.trim(), { displayMode, throwOnError: false }))
    } catch (error) {
      placeholders.push(escapeHtml(source))
    }

    return `%%KATEX_${id}%%`
  }

  nextText = nextText.replace(/\$\$([\s\S]+?)\$\$/g, function(_, source) {
    return pushPlaceholder(source, true)
  })

  nextText = nextText.replace(/\\\[([\s\S]+?)\\\]/g, function(_, source) {
    return pushPlaceholder(source, true)
  })

  nextText = nextText.replace(/\\\(([\s\S]+?)\\\)/g, function(_, source) {
    return pushPlaceholder(source, false)
  })

  nextText = nextText.replace(/(^|[^\\$])\$([^$\n]+)\$/g, function(_, prefix, source) {
    return prefix + pushPlaceholder(source, false)
  })

  return {
    text: nextText,
    placeholders
  }
}

function renderInlineMarkdown(text, placeholders) {
  let html = escapeHtml(text)

  html = html.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+|\/[A-Za-z0-9\-_/]+\/?(?:#[A-Za-z0-9\-_]+)?)\)/g, function(_, label, href) {
    return `<a href="${href}" class="chat-link">${label}</a>`
  })

  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
  html = html.replace(/(^|[^*])\*([^*\n]+)\*(?!\*)/g, '$1<em>$2</em>')
  html = html.replace(/(^|[^_])_([^_\n]+)_(?!_)/g, '$1<em>$2</em>')

  html = html.replace(/(^|\s)(https?:\/\/[^\s<]+)/g, function(_, prefix, href) {
    return `${prefix}<a href="${href}" class="chat-link">${href}</a>`
  })

  html = html.replace(/(^|\s)(\/[A-Za-z0-9\-_/]+\/?(?:#[A-Za-z0-9\-_]+)?)/g, function(_, prefix, href) {
    return `${prefix}<a href="${href}" class="chat-link">${href}</a>`
  })

  html = html.replace(/%%KATEX_(\d+)%%/g, function(_, id) {
    return placeholders[Number(id)] || ''
  })

  return html
}

function renderLinkedHtml(text) {
  const katexResult = renderKatex(text)
  const lines = katexResult.text.split('\n')
  const html = []

  for (const line of lines) {
    const trimmed = line.trim()

    if (!trimmed) continue

    const headingMatch = trimmed.match(/^(#{1,6})\s+(.+)$/)
    if (headingMatch) {
      const level = headingMatch[1].length
      html.push(`<h${level}>${renderInlineMarkdown(headingMatch[2], katexResult.placeholders)}</h${level}>`)
      continue
    }

    html.push(`<p>${renderInlineMarkdown(line, katexResult.placeholders)}</p>`)
  }

  return html.join('')
}

const zhSidebarEntries = buildSidebarEntries(sidebarConfig)
const enSidebarEntries = buildSidebarEntries(sidebarConfigEn)

export default {
  name: 'AiChat',
  data() {
    return {
      userInput: '',
      messages: [],
      isLoading: false,
      config: null,
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
    this.updateSuggestedQuestions()
    await this.loadConfig()
  },
  watch: {
    isEn() {
      this.updateSuggestedQuestions()
      if (this.config) {
        this.config.systemPrompt = this.getSystemPrompt()
      }
    }
  },
  beforeDestroy() {
    this.abortRequest()
  },
  methods: {
    getMessageText(message, index) {
      if (
        message &&
        message.role === 'assistant' &&
        !message.content &&
        this.isLoading &&
        index === this.messages.length - 1
      ) {
        return this.t('thinking')
      }

      return message.content
    },

    renderMessageHtml(message, index) {
      return renderLinkedHtml(this.getMessageText(message, index))
    },

    t(key) {
      const strings = {
        toolbarTitle: { zh: 'AI 问答助手', en: 'AI Chat Assistant' },
        newChat: { zh: '新对话', en: 'New Chat' },
        welcomeTitle: { zh: '地月空间 AI 问答助手', en: 'Cislunar Space AI Assistant' },
        welcomeDesc: {
          zh: '问答助手会根据你的问题，结合本站内容和相关知识进行回答。你可以尝试以下问题：',
          en: 'This is a simplified stable chat page with only the core streaming Q&A flow.'
        },
        inputPlaceholder: { zh: '输入你的问题...', en: 'Type your question...' },
        send: { zh: '发送', en: 'Send' },
        thinking: { zh: '正在思考...', en: 'Thinking...' },
        configError: {
          zh: 'AI 配置加载失败，请检查 /ai-chat-config.json。',
          en: 'AI configuration failed to load. Please check /ai-chat-config.json.'
        },
        emptyReply: {
          zh: '抱歉，未获取到有效回复。',
          en: 'Sorry, no valid response was received.'
        },
        networkError: {
          zh: '请求失败，请检查网络或服务器代理配置。',
          en: 'Request failed. Please check the network or server proxy configuration.'
        }
      }

      const item = strings[key]
      if (!item) return key
      return this.isEn ? item.en : item.zh
    },

    updateSuggestedQuestions() {
      this.suggestedQuestions = this.isEn
        ? [
            'What is cislunar space?',
            'What is the CR3BP model?',
            'What are the characteristics of NRHO orbits?',
            'What are Lagrange points used for?'
          ]
        : [
            '什么是地月空间？',
            'CR3BP 模型是什么？',
            '有谁在研究地月空间？',
            '地月空间研究前沿是什么？'
          ]
    },

    async loadConfig() {
      try {
        const url = this.$withBase ? this.$withBase('/ai-chat-config.json') : '/ai-chat-config.json'
        const response = await fetch(url, { cache: 'no-store' })
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`)
        }

        this.config = sanitizeClientConfig(await response.json())
        this.config.systemPrompt = this.getSystemPrompt()
      } catch (error) {
        this.config = null
        this.messages = [{ role: 'assistant', content: `${this.t('configError')} ${error.message}` }]
      }
    },

    getSystemPrompt() {
      if (this.isEn) {
        const siteIndex = enSidebarEntries
          .map((entry) => `- ${entry.title}: ${entry.path}`)
          .join('\n')

        return `You are the AI assistant for the Cislunar Space Beginner's Guide website. Answer in English, be concise and professional. When relevant, cite real website pages using clickable Markdown links such as [CR3BP](/en/glossary/cr3bp/). Only use pages from the site index below. If information is not from the site, say so clearly.\n\nSite index:\n${siteIndex}`
      }

      const siteIndex = zhSidebarEntries
        .map((entry) => `- ${entry.title}: ${entry.path}`)
        .join('\n')

      return `你是地月空间入门指南网站的 AI 问答助手。请使用中文回答，保持简洁、准确、专业。引用本站内容时，请优先输出可点击的 Markdown 超链接，例如 [地月空间环境](/what-is-cislunarspace/environment/)。只能使用下面站点索引中真实存在的页面；如果内容不是来自本站，请明确说明。\n\n站点索引：\n${siteIndex}`
    },

    startNewChat() {
      this.abortRequest()
      this.messages = []
      this.userInput = ''
    },

    sendSuggested(question) {
      if (this.isLoading) return
      this.userInput = question
      this.sendMessage()
    },

    abortRequest() {
      if (this.abortController) {
        this.abortController.abort()
        this.abortController = null
      }
      this.isLoading = false
    },

    async sendMessage() {
      const text = this.userInput.trim()
      if (!text || this.isLoading || !this.config) return

      this.messages.push({ role: 'user', content: text })
      this.userInput = ''
      this.isLoading = true
      this.scrollToBottom()

      const assistantMessage = { role: 'assistant', content: '' }
      this.messages.push(assistantMessage)

      this.abortController = new AbortController()

      try {
        const maxHistory = Number(this.config.maxHistoryTurns || 10)
        const historyMessages = this.messages
          .slice(0, -1)
          .slice(-maxHistory * 2)
          .map((message) => ({ role: message.role, content: message.content }))

        const payload = {
          model: this.config.model,
          messages: [
            { role: 'system', content: this.config.systemPrompt },
            ...historyMessages
          ],
          temperature: this.config.temperature == null ? 0.7 : this.config.temperature,
          stream: true
        }

        const response = await fetch(this.config.apiEndpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(payload),
          signal: this.abortController.signal
        })

        if (!response.ok) {
          throw new Error(`HTTP ${response.status} ${response.statusText}`)
        }

        if (response.body && response.body.getReader) {
          await this.readStream(response.body.getReader(), assistantMessage)
        } else {
          const data = await response.json()
          assistantMessage.content = data.choices?.[0]?.message?.content || this.t('emptyReply')
        }

        if (!assistantMessage.content.trim()) {
          assistantMessage.content = this.t('emptyReply')
        }
      } catch (error) {
        if (error.name === 'AbortError') {
          this.messages.pop()
          return
        }

        assistantMessage.content = `${this.t('networkError')} ${error.message}`
      } finally {
        this.isLoading = false
        this.abortController = null
        this.scrollToBottom()
      }
    },

    async readStream(reader, assistantMessage) {
      const decoder = new TextDecoder('utf-8')
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

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
              assistantMessage.content += delta
              this.$forceUpdate()
              this.scrollToBottom('auto')
            }
          } catch (error) {
          }
        }
      }

      if (buffer.trim().startsWith('data:')) {
        const data = buffer.trim().slice(5).trim()
        if (data && data !== '[DONE]') {
          try {
            const parsed = JSON.parse(data)
            const delta = parsed.choices?.[0]?.delta?.content
            if (delta) {
              assistantMessage.content += delta
            }
          } catch (error) {
          }
        }
      }

      try {
        reader.cancel()
      } catch (error) {
      }
    },

    scrollToBottom(behavior) {
      this.$nextTick(() => {
        const container = this.$refs.messagesContainer
        if (!container) return

        container.scrollTo({
          top: container.scrollHeight,
          behavior: behavior || 'smooth'
        })
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
  max-width: 880px;
  margin: 0 auto;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  background: #ffffff;
}

.chat-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e2e8f0;
  background: #f8fafc;
}

.toolbar-title {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
}

.toolbar-btn,
.suggested-btn,
.send-btn {
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  background: #ffffff;
  color: #1f2937;
  cursor: pointer;
  transition: background 0.15s ease, border-color 0.15s ease;
}

.toolbar-btn,
.send-btn {
  padding: 0.55rem 0.9rem;
}

.suggested-btn {
  padding: 0.55rem 0.8rem;
  text-align: left;
}

.toolbar-btn:hover,
.suggested-btn:hover,
.send-btn:hover {
  background: #f1f5f9;
  border-color: #94a3b8;
}

.toolbar-btn:disabled,
.suggested-btn:disabled,
.send-btn:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  background: #ffffff;
}

.chat-welcome {
  padding: 2rem 0;
}

.chat-welcome h2 {
  margin: 0 0 0.75rem;
  border-bottom: none;
}

.chat-welcome p {
  margin: 0 0 1rem;
  color: #475569;
}

.suggested-questions {
  display: grid;
  gap: 0.75rem;
}

.chat-message {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
  align-items: flex-start;
}

.message-avatar {
  flex: 0 0 auto;
  width: 2.2rem;
  height: 2.2rem;
  border-radius: 999px;
  background: #dbeafe;
  color: #1e3a8a;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 700;
}

.user-message .message-avatar {
  background: #dcfce7;
  color: #166534;
}

.message-content {
  flex: 1;
  padding: 0.85rem 1rem;
  border-radius: 12px;
  background: #f8fafc;
  color: #111827;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.assistant-message .message-content {
  white-space: normal;
}

.assistant-message .message-content ::v-deep p {
  margin: 0 0 0.75rem;
}

.assistant-message .message-content ::v-deep p:last-child {
  margin-bottom: 0;
}

.assistant-message .message-content ::v-deep h1,
.assistant-message .message-content ::v-deep h2,
.assistant-message .message-content ::v-deep h3,
.assistant-message .message-content ::v-deep h4,
.assistant-message .message-content ::v-deep h5,
.assistant-message .message-content ::v-deep h6 {
  margin: 0 0 0.75rem;
  color: #0f172a;
  border-bottom: none;
  line-height: 1.35;
}

.assistant-message .message-content ::v-deep h1 { font-size: 1.4rem; }
.assistant-message .message-content ::v-deep h2 { font-size: 1.25rem; }
.assistant-message .message-content ::v-deep h3 { font-size: 1.1rem; }

.assistant-message .message-content ::v-deep strong {
  font-weight: 700;
}

.assistant-message .message-content ::v-deep em {
  font-style: italic;
}

.assistant-message .message-content ::v-deep .katex-display {
  margin: 0.85rem 0;
  overflow-x: auto;
  overflow-y: hidden;
}

.user-message .message-content {
  background: #ecfccb;
}

.message-content ::v-deep a {
  color: #2563eb;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.message-content ::v-deep a:hover {
  color: #1d4ed8;
}

.typing-indicator {
  color: #64748b;
}

.chat-input-area {
  display: flex;
  gap: 0.75rem;
  padding: 1rem;
  border-top: 1px solid #e2e8f0;
  background: #f8fafc;
}

.chat-input-area textarea {
  flex: 1;
  resize: none;
  min-height: 4rem;
  padding: 0.75rem 0.9rem;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  font: inherit;
  line-height: 1.5;
}

.chat-input-area textarea:focus {
  outline: none;
  border-color: #60a5fa;
}

.send-btn {
  align-self: flex-end;
}

@media (max-width: 768px) {
  .ai-chat-container {
    height: calc(100vh - 6rem);
    border-radius: 0;
    border-left: none;
    border-right: none;
  }

  .chat-input-area {
    flex-direction: column;
  }

  .send-btn {
    width: 100%;
  }
}
</style>
