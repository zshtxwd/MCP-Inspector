<script setup lang="ts">
import type { Component } from 'vue'
import { computed, reactive, ref } from 'vue'
import {
  Database,
  MessageSquareText,
  PanelTopOpen,
  Plus,
  Radio,
  Server,
  SquareTerminal,
  Wrench,
} from '@lucide/vue'

type ServerId = 'local' | 'staging'
type TabId = 'tools' | 'resources' | 'prompts'

interface McpServer {
  id: ServerId
  name: string
  endpoint: string
  transport: string
  connected: boolean
  latency: number | null
}

interface ResourceItem {
  id: string
  name: string
  description: string
}

interface ResourceTab {
  id: TabId
  label: string
  icon: Component
  count: number
}

const servers: McpServer[] = [
  {
    id: 'local',
    name: '本地开发服务器',
    endpoint: 'http://localhost:8000/mcp',
    transport: 'Streamable HTTP',
    connected: true,
    latency: 22,
  },
  {
    id: 'staging',
    name: '远程测试服务器',
    endpoint: 'https://staging.example.com/mcp',
    transport: 'Streamable HTTP',
    connected: false,
    latency: null,
  },
]

const resourceItems = reactive<Record<TabId, ResourceItem[]>>({
  tools: [
    { id: 'search-files', name: 'search_files', description: '按名称或内容搜索工作区文件' },
    { id: 'read-file', name: 'read_file', description: '读取指定文件的完整内容' },
    { id: 'write-file', name: 'write_file', description: '创建文件或更新已有文件' },
    { id: 'list-directory', name: 'list_directory', description: '列出目录下的文件和文件夹' },
    { id: 'run-command', name: 'run_command', description: '在工作区内执行终端命令' },
    { id: 'git-status', name: 'get_git_status', description: '查看当前仓库的变更状态' },
    { id: 'fetch-url', name: 'fetch_url', description: '获取指定网页的响应内容' },
    { id: 'query-database', name: 'query_database', description: '执行只读数据库查询' },
  ],
  resources: [
    { id: 'readme', name: 'workspace://README.md', description: '项目说明与本地开发指南' },
    { id: 'config', name: 'config://mcp.json', description: '当前 MCP 服务器配置' },
    { id: 'logs', name: 'logs://latest', description: '最近一次服务运行日志' },
  ],
  prompts: [
    { id: 'code-review', name: 'code_review', description: '检查代码质量与潜在问题' },
    { id: 'explain-code', name: 'explain_code', description: '解释所选代码的实现逻辑' },
    { id: 'fix-bug', name: 'fix_bug', description: '分析错误并给出修复方案' },
    { id: 'write-tests', name: 'write_tests', description: '为现有功能补充测试用例' },
    { id: 'summarize', name: 'summarize_changes', description: '整理本次代码变更摘要' },
  ],
})

const tabs = computed<ResourceTab[]>(() => [
  { id: 'tools', label: '工具', icon: Wrench, count: resourceItems.tools.length },
  { id: 'resources', label: '资源', icon: Database, count: resourceItems.resources.length },
  { id: 'prompts', label: '提示词', icon: MessageSquareText, count: resourceItems.prompts.length },
])

const selectedServerId = ref<ServerId>('local')
const activeTabId = ref<TabId>('tools')

const selectedServer = computed(
  () => servers.find((server) => server.id === selectedServerId.value) ?? servers[0],
)
const connectedServerCount = computed(() => servers.filter((server) => server.connected).length)
const activeTab = computed(
  () => tabs.value.find((tab) => tab.id === activeTabId.value) ?? tabs.value[0],
)
const activeItems = computed(() => resourceItems[activeTabId.value])

function formatCount(count: number) {
  return count > 99 ? '99+' : String(count)
}

function formatServerStatus(server: McpServer) {
  if (!server.connected) return '离线'
  return server.latency === null ? '--' : `${server.latency} ms`
}

function selectTab(tabId: TabId) {
  activeTabId.value = tabId
}

function handleTabKeydown(event: KeyboardEvent, currentIndex: number) {
  const tabItems = tabs.value
  let nextIndex = currentIndex

  if (event.key === 'ArrowLeft') {
    nextIndex = (currentIndex - 1 + tabItems.length) % tabItems.length
  } else if (event.key === 'ArrowRight') {
    nextIndex = (currentIndex + 1) % tabItems.length
  } else if (event.key === 'Home') {
    nextIndex = 0
  } else if (event.key === 'End') {
    nextIndex = tabItems.length - 1
  } else {
    return
  }

  event.preventDefault()
  const nextTab = tabItems[nextIndex]
  selectTab(nextTab.id)
  document.getElementById(`tab-${nextTab.id}`)?.focus()
}
</script>

<template>
  <main class="inspector-page">
    <header class="app-header">
      <div class="brand">
        <span class="brand-mark" aria-hidden="true">
          <SquareTerminal :size="22" :stroke-width="1.8" />
        </span>
        <div>
          <h1>MCP Inspector</h1>
          <p>协议调试工作台</p>
        </div>
      </div>

      <div class="header-meta">
        <span class="environment-badge">本地环境</span>
        <span class="global-status">
          <span class="status-dot is-connected" aria-hidden="true" />
          {{ connectedServerCount }}/{{ servers.length }} 个服务在线
        </span>
      </div>
    </header>

    <div class="inspector-layout">
      <aside class="sidebar" aria-label="MCP 服务器与能力">
        <section class="panel server-panel" aria-labelledby="server-panel-title">
          <header class="panel-header">
            <div class="panel-title">
              <Server :size="18" :stroke-width="1.8" aria-hidden="true" />
              <h2 id="server-panel-title">服务器</h2>
              <span class="panel-count">{{ servers.length }}</span>
            </div>
            <button
              class="icon-button add-server-button"
              type="button"
              aria-label="添加 MCP 服务器"
              title="添加 MCP 服务器"
            >
              <Plus :size="19" :stroke-width="2" aria-hidden="true" />
            </button>
          </header>

          <el-scrollbar
            class="server-scrollbar"
            always
            :min-size="36"
            :tabindex="0"
            tag="ul"
            view-class="server-list"
            role="list"
            aria-label="MCP 服务器列表"
          >
            <li v-for="serverItem in servers" :key="serverItem.id">
              <button
                class="server-item"
                :class="{ 'is-selected': selectedServerId === serverItem.id }"
                type="button"
                :aria-pressed="selectedServerId === serverItem.id"
                @click="selectedServerId = serverItem.id"
              >
                <span class="server-primary-row">
                  <span
                    class="status-dot"
                    :class="serverItem.connected ? 'is-connected' : 'is-offline'"
                    aria-hidden="true"
                  />
                  <span class="server-name">{{ serverItem.name }}</span>
                  <span class="server-state">
                    {{ formatServerStatus(serverItem) }}
                  </span>
                </span>
                <span class="server-endpoint">{{ serverItem.endpoint }}</span>
                <span class="server-secondary-row">
                  <span>{{ serverItem.transport }}</span>
                </span>
              </button>
            </li>
          </el-scrollbar>

          <footer class="panel-footer">
            <Radio :size="15" :stroke-width="1.8" aria-hidden="true" />
            <span>{{ selectedServer.connected ? '连接正常' : '等待服务器恢复' }}</span>
          </footer>
        </section>

        <section class="panel resource-panel" aria-label="服务器能力">
          <div class="tab-bar" role="tablist" aria-label="能力类型">
            <button
              v-for="(tab, index) in tabs"
              :id="`tab-${tab.id}`"
              :key="tab.id"
              class="tab-button"
              :class="{ 'is-active': activeTabId === tab.id }"
              type="button"
              role="tab"
              :aria-label="`${tab.label}，${tab.count} 项`"
              :aria-selected="activeTabId === tab.id"
              aria-controls="resource-tab-panel"
              :tabindex="activeTabId === tab.id ? 0 : -1"
              @click="selectTab(tab.id)"
              @keydown="handleTabKeydown($event, index)"
            >
              <component :is="tab.icon" :size="16" :stroke-width="1.8" aria-hidden="true" />
              <span class="tab-label">{{ tab.label }}</span>
              <span class="tab-count" aria-hidden="true">{{ formatCount(tab.count) }}</span>
            </button>
          </div>

          <div
            id="resource-tab-panel"
            class="resource-list"
            role="tabpanel"
            :aria-labelledby="`tab-${activeTab.id}`"
          >
            <el-scrollbar
              class="resource-scrollbar"
              always
              :min-size="36"
              :tabindex="0"
              tag="ul"
              view-class="capability-list"
              role="list"
              :aria-label="`${activeTab.label}列表`"
            >
              <li v-for="item in activeItems" :key="item.id" class="capability-item">
                <span class="capability-icon" aria-hidden="true">
                  <component :is="activeTab.icon" :size="15" :stroke-width="1.8" />
                </span>
                <span class="capability-copy">
                  <strong class="capability-name">{{ item.name }}</strong>
                  <span class="capability-description">{{ item.description }}</span>
                </span>
              </li>
            </el-scrollbar>
          </div>
        </section>
      </aside>

      <section class="workspace" aria-labelledby="workspace-title">
        <header class="workspace-header">
          <div>
            <p class="workspace-context">
              <span
                class="status-dot"
                :class="selectedServer.connected ? 'is-connected' : 'is-offline'"
                aria-hidden="true"
              />
              {{ selectedServer.name }}
            </p>
            <h2 id="workspace-title">检查器</h2>
          </div>
          <span class="transport-badge">{{ selectedServer.transport }}</span>
        </header>

        <div class="workspace-canvas">
          <span class="empty-state-icon" aria-hidden="true">
            <PanelTopOpen :size="28" :stroke-width="1.6" />
          </span>
          <h3>尚未选择{{ activeTab.label }}</h3>
          <p>{{ selectedServer.name }} · {{ activeItems.length }} 项可用</p>
        </div>

        <footer class="workspace-footer">
          <span class="connection-label">
            <span
              class="status-dot"
              :class="selectedServer.connected ? 'is-connected' : 'is-offline'"
              aria-hidden="true"
            />
            {{ formatServerStatus(selectedServer) }}
          </span>
          <code>{{ selectedServer.endpoint }}</code>
        </footer>
      </section>
    </div>
  </main>
</template>

<style scoped>
.inspector-page {
  --color-canvas: #eef1ef;
  --color-surface: #ffffff;
  --color-surface-subtle: #f7f9f8;
  --color-ink: #18201f;
  --color-muted: #65716d;
  --color-faint: #8a9691;
  --color-border: #d7dedb;
  --color-brand: #1f9d68;
  --color-brand-soft: #e8f5ef;
  --color-offline: #8a9691;
  --color-header: #17201f;
  display: flex;
  width: 100%;
  min-height: 100dvh;
  flex-direction: column;
  gap: 12px;
  padding: 12px;
  color: var(--color-ink);
  background: var(--color-canvas);
}

.app-header {
  display: flex;
  min-height: 64px;
  flex: 0 0 auto;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 10px 16px;
  color: #f7faf8;
  background: var(--color-header);
  border: 1px solid #293430;
  border-radius: 6px;
}

.brand,
.header-meta,
.panel-title,
.global-status,
.workspace-context,
.connection-label {
  display: flex;
  align-items: center;
}

.brand {
  min-width: 0;
  gap: 12px;
}

.brand-mark {
  display: grid;
  width: 38px;
  height: 38px;
  flex: 0 0 38px;
  place-items: center;
  color: #ffffff;
  background: var(--color-brand);
  border-radius: 5px;
}

.brand h1,
.brand p,
.panel-title h2,
.workspace-header h2,
.workspace-context,
.workspace-canvas h3,
.workspace-canvas p {
  margin: 0;
}

.brand h1 {
  font-size: 16px;
  font-weight: 650;
  line-height: 1.35;
}

.brand p {
  color: #aeb9b5;
  font-size: 12px;
  line-height: 1.4;
}

.header-meta {
  flex: 0 0 auto;
  gap: 16px;
  font-size: 13px;
}

.environment-badge,
.transport-badge {
  display: inline-flex;
  min-height: 28px;
  align-items: center;
  padding: 4px 9px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.environment-badge {
  color: #c8d2ce;
  background: #25302d;
  border: 1px solid #36433e;
}

.global-status {
  gap: 8px;
  color: #dbe2df;
  white-space: nowrap;
}

.inspector-layout {
  display: grid;
  min-height: 0;
  flex: 1;
  grid-template-columns: clamp(310px, 25vw, 360px) minmax(0, 1fr);
  gap: 12px;
}

.sidebar {
  display: grid;
  min-height: 0;
  grid-template-rows: minmax(250px, 0.72fr) minmax(400px, 1.28fr);
  gap: 12px;
}

.panel,
.workspace {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  box-shadow: 0 1px 2px rgba(24, 32, 31, 0.05);
}

.panel {
  display: flex;
  min-height: 0;
  flex-direction: column;
  overflow: hidden;
}

.panel-header {
  display: flex;
  min-height: 56px;
  flex: 0 0 56px;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 8px 10px 8px 16px;
  border-bottom: 1px solid var(--color-border);
}

.panel-title {
  min-width: 0;
  gap: 8px;
}

.panel-title > svg {
  color: var(--color-muted);
}

.panel-title h2 {
  font-size: 15px;
  font-weight: 650;
  line-height: 1.4;
}

.panel-count,
.tab-count {
  display: inline-grid;
  width: 28px;
  min-width: 28px;
  height: 20px;
  place-items: center;
  padding: 0;
  overflow: hidden;
  color: var(--color-muted);
  background: #edf0ee;
  border-radius: 4px;
  font-size: 11px;
  font-variant-numeric: tabular-nums;
  font-weight: 650;
  line-height: 1;
  text-overflow: clip;
  white-space: nowrap;
}

.icon-button {
  display: grid;
  width: 40px;
  height: 40px;
  flex: 0 0 40px;
  place-items: center;
  padding: 0;
  color: #ffffff;
  background: var(--color-brand);
  border: 0;
  border-radius: 5px;
  cursor: pointer;
}

.icon-button,
.server-item,
.tab-button {
  transition:
    color 120ms ease,
    background-color 120ms ease,
    border-color 120ms ease;
}

.icon-button:hover {
  background: #188356;
}

.icon-button:active {
  background: #126d47;
}

.icon-button:focus-visible,
.server-item:focus-visible,
.tab-button:focus-visible {
  position: relative;
  z-index: 1;
  outline: 2px solid var(--color-brand);
  outline-offset: -2px;
}

:deep(.server-list),
:deep(.capability-list) {
  margin: 0;
  padding: 0;
  list-style: none;
}

.server-scrollbar {
  min-height: 0;
  flex: 1;
}

:deep(.server-list) {
  padding: 8px 14px 8px 8px;
}

:deep(.server-list) li + li {
  margin-top: 4px;
}

.server-item {
  display: flex;
  width: 100%;
  min-height: 88px;
  flex-direction: column;
  justify-content: center;
  gap: 7px;
  padding: 10px 11px;
  color: var(--color-ink);
  text-align: left;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 5px;
  cursor: pointer;
}

.server-item:hover {
  background: var(--color-surface-subtle);
  border-color: var(--color-border);
}

.server-item.is-selected {
  background: var(--color-brand-soft);
  border-color: #b9ddcc;
}

.server-primary-row,
.server-secondary-row {
  display: flex;
  width: 100%;
  min-width: 0;
  align-items: center;
}

.server-primary-row {
  gap: 8px;
}

.server-secondary-row {
  justify-content: space-between;
  gap: 12px;
  color: var(--color-faint);
  font-size: 11px;
}

.status-dot {
  width: 8px;
  height: 8px;
  flex: 0 0 8px;
  background: var(--color-offline);
  border-radius: 50%;
}

.status-dot.is-connected {
  background: var(--color-brand);
  box-shadow: 0 0 0 3px rgba(31, 157, 104, 0.14);
}

.status-dot.is-offline {
  background: var(--color-offline);
}

.server-name {
  min-width: 0;
  flex: 1;
  overflow: hidden;
  font-size: 14px;
  font-weight: 650;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.server-state {
  flex: 0 0 auto;
  color: var(--color-muted);
  font-size: 11px;
}

.server-endpoint {
  width: 100%;
  overflow: hidden;
  color: var(--color-muted);
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 11px;
  line-height: 1.4;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.panel-footer {
  display: flex;
  min-height: 36px;
  flex: 0 0 36px;
  align-items: center;
  gap: 7px;
  padding: 0 14px;
  color: var(--color-muted);
  background: var(--color-surface-subtle);
  border-top: 1px solid var(--color-border);
  font-size: 11px;
}

.panel-footer > svg {
  color: var(--color-brand);
}

.tab-bar {
  display: grid;
  min-height: 56px;
  flex: 0 0 56px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  border-bottom: 1px solid var(--color-border);
}

.tab-button {
  position: relative;
  display: flex;
  min-width: 0;
  align-items: center;
  justify-content: center;
  gap: 5px;
  padding: 0 6px;
  color: var(--color-muted);
  background: var(--color-surface);
  border: 0;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.tab-button + .tab-button {
  border-left: 1px solid var(--color-border);
}

.tab-button::after {
  position: absolute;
  right: 10px;
  bottom: 0;
  left: 10px;
  height: 2px;
  background: transparent;
  content: "";
}

.tab-button:hover:not(.is-active) {
  color: var(--color-ink);
  background: var(--color-surface-subtle);
}

.tab-button.is-active {
  color: var(--color-ink);
  background: #fbfcfb;
}

.tab-button.is-active::after {
  background: var(--color-brand);
}

.tab-button.is-active .tab-count {
  color: #176d49;
  background: var(--color-brand-soft);
}

.tab-label {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
}

.resource-list {
  min-height: 0;
  flex: 1 1 0;
  overflow: hidden;
  contain: layout paint;
}

.resource-scrollbar {
  height: 100%;
}

:deep(.capability-list) {
  min-height: 100%;
  padding-right: 10px;
  overflow-anchor: none;
}

.capability-item {
  display: grid;
  height: 64px;
  min-height: 64px;
  align-items: center;
  grid-template-columns: 32px minmax(0, 1fr);
  gap: 10px;
  padding: 9px 12px;
  border-bottom: 1px solid #e6eae8;
}

.capability-item:last-child {
  border-bottom: 0;
}

.capability-item:hover {
  background: var(--color-surface-subtle);
}

.capability-icon {
  display: grid;
  width: 32px;
  height: 32px;
  place-items: center;
  color: #34775c;
  background: var(--color-brand-soft);
  border-radius: 4px;
}

.capability-copy {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 3px;
}

.capability-name {
  overflow: hidden;
  color: var(--color-ink);
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 12px;
  font-weight: 600;
  line-height: 1.4;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.capability-description {
  overflow: hidden;
  color: var(--color-muted);
  font-size: 12px;
  line-height: 1.45;
  text-overflow: ellipsis;
  white-space: nowrap;
}

:deep(.el-scrollbar__wrap:focus-visible) {
  outline: 2px solid var(--color-brand);
  outline-offset: -2px;
}

:deep(.el-scrollbar__bar.is-vertical) {
  top: 6px;
  right: 3px;
  bottom: 6px;
  width: 7px;
}

:deep(.el-scrollbar__bar.is-horizontal) {
  display: none;
}

:deep(.el-scrollbar__thumb) {
  background: #8fa099;
  border-radius: 4px;
  opacity: 0.65;
}

:deep(.el-scrollbar__thumb:hover) {
  background: #557267;
  opacity: 0.9;
}

.workspace {
  display: flex;
  min-width: 0;
  min-height: 0;
  flex-direction: column;
  overflow: hidden;
}

.workspace-header {
  display: flex;
  min-height: 72px;
  flex: 0 0 72px;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 10px 20px;
  border-bottom: 1px solid var(--color-border);
}

.workspace-context {
  gap: 8px;
  color: var(--color-muted);
  font-size: 12px;
  line-height: 1.4;
}

.workspace-header h2 {
  margin-top: 2px;
  font-size: 18px;
  font-weight: 650;
  line-height: 1.4;
}

.transport-badge {
  color: #825f18;
  background: #fbf3df;
  border: 1px solid #ead7a7;
}

.workspace-canvas {
  display: flex;
  min-height: 360px;
  flex: 1;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px;
  text-align: center;
  background: #fafbfa;
}

.empty-state-icon {
  display: grid;
  width: 58px;
  height: 58px;
  place-items: center;
  margin-bottom: 18px;
  color: #4f625b;
  background: #edf1ef;
  border: 1px solid #d7dedb;
  border-radius: 6px;
}

.workspace-canvas h3 {
  font-size: 16px;
  font-weight: 650;
  line-height: 1.5;
}

.workspace-canvas p {
  margin-top: 6px;
  color: var(--color-muted);
  font-size: 13px;
  line-height: 1.5;
}

.workspace-footer {
  display: flex;
  min-height: 40px;
  flex: 0 0 40px;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 0 16px;
  color: var(--color-muted);
  background: var(--color-surface-subtle);
  border-top: 1px solid var(--color-border);
  font-size: 11px;
}

.connection-label {
  flex: 0 0 auto;
  gap: 8px;
}

.workspace-footer code {
  min-width: 0;
  overflow: hidden;
  color: #52615c;
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 11px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

button {
  touch-action: manipulation;
}

@media (max-width: 780px) {
  .inspector-page {
    min-height: 100dvh;
  }

  .inspector-layout {
    display: flex;
    flex-direction: column;
  }

  .sidebar {
    grid-template-columns: minmax(280px, 0.9fr) minmax(360px, 1.1fr);
    grid-template-rows: 480px;
  }

  .workspace {
    min-height: 480px;
  }
}

@media (max-width: 700px) {
  .app-header {
    align-items: flex-start;
  }

  .environment-badge {
    display: none;
  }

  .sidebar {
    display: flex;
    flex-direction: column;
  }

  .server-panel {
    min-height: 300px;
  }

  .resource-panel {
    height: 520px;
    min-height: 520px;
  }
}

@media (max-width: 440px) {
  .inspector-page {
    gap: 8px;
    padding: 8px;
  }

  .app-header,
  .inspector-layout,
  .sidebar {
    gap: 8px;
  }

  .app-header {
    min-height: 60px;
    padding: 9px 11px;
  }

  .brand {
    gap: 9px;
  }

  .brand-mark {
    width: 36px;
    height: 36px;
    flex-basis: 36px;
  }

  .brand p {
    display: none;
  }

  .header-meta {
    font-size: 11px;
  }

  .global-status {
    gap: 6px;
  }

  .tab-button {
    gap: 4px;
    padding-inline: 4px;
    font-size: 11px;
  }

  .tab-button > svg {
    display: none;
  }

  .workspace-header {
    padding-inline: 14px;
  }

  .workspace-footer {
    align-items: flex-start;
    flex-direction: column;
    justify-content: center;
    gap: 2px;
    padding-block: 6px;
  }
}

@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    scroll-behavior: auto !important;
    transition-duration: 0.01ms !important;
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
  }
}
</style>
