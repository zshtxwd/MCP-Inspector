<script setup lang="ts">
import type { Component } from 'vue'
import { computed, reactive, ref } from 'vue'
import {
  Database,
  MessageSquareText,
  PanelTopOpen,
  Play,
  Plus,
  Radio,
  RotateCcw,
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
  params?: ToolParam[]
}

type ToolParamType = 'string' | 'number' | 'boolean' | 'select' | 'textarea'

interface ToolParam {
  name: string
  label: string
  description: string
  type: ToolParamType
  required?: boolean
  placeholder?: string
  defaultValue?: string | number | boolean
  options?: string[]
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
    {
      id: 'search-files',
      name: 'search_files',
      description: '按文件名或文件内容搜索工作区，并返回匹配的文件路径与上下文。',
      params: [
        {
          name: 'query',
          label: '搜索内容',
          description: '要查找的文件名或文本内容',
          type: 'string',
          required: true,
          placeholder: '例如：InspectorPage',
        },
        {
          name: 'path',
          label: '搜索目录',
          description: '相对于工作区根目录的路径',
          type: 'string',
          placeholder: '例如：frontend/src',
        },
        {
          name: 'max_results',
          label: '结果数量',
          description: '最多返回的匹配项数量',
          type: 'number',
          defaultValue: 20,
        },
      ],
    },
    {
      id: 'read-file',
      name: 'read_file',
      description: '读取指定文件的完整内容。',
      params: [
        { name: 'path', label: '文件路径', description: '要读取的文件路径', type: 'string', required: true, placeholder: '例如：README.md' },
        { name: 'encoding', label: '字符编码', description: '读取文件时使用的编码', type: 'select', defaultValue: 'utf-8', options: ['utf-8', 'utf-16', 'ascii'] },
      ],
    },
    {
      id: 'write-file',
      name: 'write_file',
      description: '创建文件或更新已有文件。',
      params: [
        { name: 'path', label: '文件路径', description: '目标文件路径', type: 'string', required: true, placeholder: '例如：src/example.ts' },
        { name: 'content', label: '文件内容', description: '要写入文件的文本', type: 'textarea', required: true, placeholder: '输入文件内容' },
        { name: 'overwrite', label: '允许覆盖', description: '文件存在时覆盖原内容', type: 'boolean', defaultValue: false },
      ],
    },
    {
      id: 'list-directory',
      name: 'list_directory',
      description: '列出指定目录下的文件和文件夹。',
      params: [
        { name: 'path', label: '目录路径', description: '要浏览的目录', type: 'string', required: true, placeholder: '例如：frontend/src' },
        { name: 'recursive', label: '递归读取', description: '包含所有子目录内容', type: 'boolean', defaultValue: false },
      ],
    },
    {
      id: 'run-command',
      name: 'run_command',
      description: '在工作区内执行终端命令。',
      params: [
        { name: 'command', label: '命令', description: '要执行的终端命令', type: 'string', required: true, placeholder: '例如：npm run build' },
        { name: 'cwd', label: '工作目录', description: '命令执行目录', type: 'string', placeholder: '例如：frontend' },
        { name: 'timeout', label: '超时时间', description: '命令超时秒数', type: 'number', defaultValue: 30 },
      ],
    },
    { id: 'git-status', name: 'get_git_status', description: '查看当前仓库的变更状态。', params: [] },
    {
      id: 'fetch-url',
      name: 'fetch_url',
      description: '获取指定网页的响应内容。',
      params: [
        { name: 'url', label: 'URL', description: '要请求的完整网页地址', type: 'string', required: true, placeholder: 'https://example.com' },
        { name: 'method', label: '请求方法', description: 'HTTP 请求方法', type: 'select', defaultValue: 'GET', options: ['GET', 'POST'] },
      ],
    },
    {
      id: 'query-database',
      name: 'query_database',
      description: '执行只读数据库查询。',
      params: [
        { name: 'query', label: '查询语句', description: '要执行的只读 SQL', type: 'textarea', required: true, placeholder: 'SELECT * FROM users LIMIT 10' },
      ],
    },
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
const selectedToolId = ref('search-files')
const formValues = ref<Record<string, string | number | boolean>>({})

const selectedServer = computed(
  () => servers.find((server) => server.id === selectedServerId.value) ?? servers[0],
)
const connectedServerCount = computed(() => servers.filter((server) => server.connected).length)
const activeTab = computed(
  () => tabs.value.find((tab) => tab.id === activeTabId.value) ?? tabs.value[0],
)
const activeItems = computed(() => resourceItems[activeTabId.value])
const selectedTool = computed(() =>
  resourceItems.tools.find((tool) => tool.id === selectedToolId.value),
)

function createParamValues(tool: ResourceItem) {
  return Object.fromEntries(
    (tool.params ?? []).map((param) => [param.name, param.defaultValue ?? '']),
  )
}

formValues.value = createParamValues(selectedTool.value ?? resourceItems.tools[0])

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

function selectTool(tool: ResourceItem) {
  if (activeTabId.value !== 'tools') return
  selectedToolId.value = tool.id
  formValues.value = createParamValues(tool)
}

function resetParams() {
  if (!selectedTool.value) return
  formValues.value = createParamValues(selectedTool.value)
}

function updateParamValue(param: ToolParam, event: Event) {
  const target = event.target as HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
  formValues.value[param.name] = param.type === 'number' ? Number(target.value) : target.value
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
                <button
                  class="capability-button"
                  :class="{ 'is-selected': activeTabId === 'tools' && selectedToolId === item.id }"
                  type="button"
                  :aria-pressed="activeTabId === 'tools' ? selectedToolId === item.id : undefined"
                  @click="selectTool(item)"
                >
                  <span class="capability-icon" aria-hidden="true">
                    <component :is="activeTab.icon" :size="15" :stroke-width="1.8" />
                  </span>
                  <span class="capability-copy">
                    <strong class="capability-name">{{ item.name }}</strong>
                    <span class="capability-description">{{ item.description }}</span>
                  </span>
                </button>
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
          <section class="workspace-section basic-info" aria-labelledby="basic-info-title">
            <header class="workspace-section-header">
              <div>
                <span class="section-eyebrow">TOOL</span>
                <h3 id="basic-info-title">工具调试</h3>
              </div>
              <span v-if="selectedTool" class="param-count">
                {{ selectedTool.params?.length ?? 0 }} 个参数
              </span>
            </header>
            <div v-if="selectedTool" class="tool-debugger">
              <div class="tool-summary">
                <span class="field-label">Name</span>
                <code class="tool-name">{{ selectedTool.name }}</code>
                <span class="field-label">Description</span>
                <p>{{ selectedTool.description }}</p>
              </div>

              <form class="params-form" @submit.prevent>
                <div class="params-form-heading">
                  <div>
                    <h4>Params</h4>
                    <p>填写本次工具调用所需的参数</p>
                  </div>
                </div>

                <div v-if="selectedTool.params?.length" class="param-fields">
                  <label v-for="param in selectedTool.params" :key="param.name" class="param-field">
                    <span class="param-label">
                      {{ param.label }}
                      <span v-if="param.required" class="required-mark" aria-label="必填">*</span>
                      <code>{{ param.name }}</code>
                    </span>
                    <span class="param-description">{{ param.description }}</span>

                    <select
                      v-if="param.type === 'select'"
                      :value="String(formValues[param.name] ?? '')"
                      class="form-control"
                      :required="param.required"
                      @change="updateParamValue(param, $event)"
                    >
                      <option v-for="option in param.options" :key="option" :value="option">
                        {{ option }}
                      </option>
                    </select>
                    <textarea
                      v-else-if="param.type === 'textarea'"
                      :value="String(formValues[param.name] ?? '')"
                      class="form-control form-textarea"
                      :placeholder="param.placeholder"
                      :required="param.required"
                      rows="3"
                      @input="updateParamValue(param, $event)"
                    />
                    <span v-else-if="param.type === 'boolean'" class="boolean-control">
                      <input v-model="formValues[param.name]" type="checkbox" />
                      <span>{{ formValues[param.name] ? '启用' : '关闭' }}</span>
                    </span>
                    <input
                      v-else
                      :value="formValues[param.name] as string | number"
                      class="form-control"
                      :type="param.type"
                      :placeholder="param.placeholder"
                      :required="param.required"
                      @input="updateParamValue(param, $event)"
                    />
                  </label>
                </div>
                <p v-else class="no-params">该工具无需参数，可直接调用。</p>

                <div class="params-actions">
                  <button
                    class="secondary-button"
                    type="button"
                    title="重置参数"
                    @click="resetParams"
                  >
                    <RotateCcw :size="15" :stroke-width="1.8" aria-hidden="true" />
                    重置
                  </button>
                  <button
                    class="primary-button"
                    type="submit"
                    disabled
                    title="接口接入后可调用"
                  >
                    <Play :size="15" :stroke-width="2" aria-hidden="true" />
                    调试
                  </button>
                </div>
              </form>
            </div>
          </section>

          <div class="workspace-detail-grid">
            <section class="workspace-section timeline-section" aria-labelledby="timeline-title">
              <header class="workspace-section-header">
                <h3 id="timeline-title">时间轴</h3>
              </header>
              <div class="section-empty-state">
                <span class="empty-state-icon" aria-hidden="true">
                  <PanelTopOpen :size="28" :stroke-width="1.6" />
                </span>
                <h4>暂无调用记录</h4>
                <p>工具调用时间轴将在此处展示</p>
              </div>
            </section>

            <section class="workspace-section result-section" aria-labelledby="result-title">
              <header class="workspace-section-header">
                <h3 id="result-title">调用结果</h3>
              </header>
              <div class="section-empty-state section-empty-state-compact">
                <h4>尚未调用工具</h4>
                <p>执行调试后，响应状态和返回内容将在此处显示</p>
              </div>
            </section>
          </div>
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
.workspace-canvas h4,
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
.tab-button,
.capability-button,
.primary-button,
.secondary-button {
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
.tab-button:focus-visible,
.capability-button:focus-visible,
.primary-button:focus-visible,
.secondary-button:focus-visible,
.form-control:focus-visible,
.boolean-control:focus-within {
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
  height: 64px;
  min-height: 64px;
  border-bottom: 1px solid #e6eae8;
}

.capability-item:last-child {
  border-bottom: 0;
}

.capability-button {
  display: grid;
  width: 100%;
  height: 100%;
  min-width: 0;
  align-items: center;
  grid-template-columns: 32px minmax(0, 1fr);
  gap: 10px;
  padding: 9px 12px;
  color: inherit;
  text-align: left;
  background: transparent;
  border: 0;
  cursor: pointer;
}

.capability-button:hover {
  background: var(--color-surface-subtle);
}

.capability-button.is-selected {
  background: var(--color-brand-soft);
  box-shadow: inset 3px 0 0 var(--color-brand);
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
  display: grid;
  min-height: 360px;
  flex: 1;
  grid-template-rows: minmax(300px, auto) minmax(0, 1fr);
  gap: 12px;
  padding: 12px;
  background: #f4f6f5;
}

.workspace-section {
  display: flex;
  min-width: 0;
  min-height: 0;
  flex-direction: column;
  overflow: hidden;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 5px;
}

.workspace-section-header {
  display: flex;
  min-height: 44px;
  flex: 0 0 44px;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 0 16px;
  border-bottom: 1px solid var(--color-border);
}

.workspace-section-header h3 {
  font-size: 14px;
  font-weight: 650;
  line-height: 1.4;
}

.section-eyebrow {
  display: block;
  margin-bottom: 1px;
  color: var(--color-brand);
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 9px;
  font-weight: 700;
  line-height: 1.1;
}

.param-count {
  flex: 0 0 auto;
  color: var(--color-muted);
  font-size: 11px;
}

.tool-debugger {
  display: grid;
  flex: 1;
  grid-template-columns: minmax(200px, 0.65fr) minmax(360px, 1.35fr);
  min-height: 0;
}

.tool-summary {
  min-width: 0;
  padding: 20px;
  background: var(--color-surface-subtle);
  border-right: 1px solid var(--color-border);
}

.field-label {
  display: block;
  margin-bottom: 7px;
  color: var(--color-faint);
  font-size: 10px;
  font-weight: 700;
  line-height: 1.3;
  text-transform: uppercase;
}

.tool-name {
  display: block;
  margin-bottom: 22px;
  overflow: hidden;
  color: #176d49;
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 15px;
  font-weight: 650;
  line-height: 1.4;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tool-summary p {
  color: var(--color-muted);
  font-size: 13px;
  line-height: 1.65;
}

.params-form {
  display: flex;
  min-width: 0;
  flex-direction: column;
  padding: 18px 20px;
}

.params-form-heading h4 {
  font-size: 14px;
  font-weight: 650;
  line-height: 1.4;
}

.params-form-heading p {
  margin-top: 3px;
  color: var(--color-muted);
  font-size: 11px;
  line-height: 1.4;
}

.param-fields {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px 16px;
  margin-top: 16px;
}

.param-field {
  display: flex;
  min-width: 0;
  flex-direction: column;
}

.param-label {
  color: var(--color-ink);
  font-size: 12px;
  font-weight: 650;
  line-height: 1.4;
}

.param-label code {
  margin-left: 6px;
  color: var(--color-faint);
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 10px;
  font-weight: 500;
}

.required-mark {
  margin-left: 2px;
  color: #c43f3f;
}

.param-description {
  min-height: 17px;
  margin: 2px 0 6px;
  color: var(--color-faint);
  font-size: 10px;
  line-height: 1.4;
}

.form-control {
  width: 100%;
  min-height: 36px;
  padding: 7px 10px;
  color: var(--color-ink);
  background: #ffffff;
  border: 1px solid #cbd4d0;
  border-radius: 4px;
  font: inherit;
  font-size: 12px;
}

.form-control::placeholder {
  color: #9aa49f;
}

.form-textarea {
  min-height: 72px;
  resize: vertical;
}

.boolean-control {
  display: flex;
  min-height: 36px;
  align-items: center;
  gap: 8px;
  padding: 0 10px;
  background: #ffffff;
  border: 1px solid #cbd4d0;
  border-radius: 4px;
  color: var(--color-muted);
  font-size: 12px;
}

.boolean-control input {
  width: 16px;
  height: 16px;
  accent-color: var(--color-brand);
}

.no-params {
  flex: 1;
  margin-top: 18px !important;
  color: var(--color-muted);
  font-size: 12px;
}

.params-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: auto;
  padding-top: 18px;
}

.primary-button,
.secondary-button {
  display: inline-flex;
  min-height: 36px;
  align-items: center;
  justify-content: center;
  gap: 7px;
  padding: 7px 13px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 650;
}

.primary-button {
  color: #ffffff;
  background: var(--color-brand);
  border: 1px solid var(--color-brand);
}

.primary-button:disabled {
  color: #8c9692;
  background: #e8ecea;
  border-color: #d7dedb;
  cursor: not-allowed;
}

.secondary-button {
  color: var(--color-ink);
  background: #ffffff;
  border: 1px solid #cbd4d0;
}

.secondary-button:hover {
  background: var(--color-surface-subtle);
}

.workspace-detail-grid {
  display: grid;
  min-width: 0;
  min-height: 0;
  grid-template-columns: minmax(0, 2.4fr) minmax(240px, 1fr);
  gap: 12px;
}

.section-empty-state {
  display: flex;
  min-height: 240px;
  flex: 1;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px;
  text-align: center;
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

.section-empty-state h4 {
  font-size: 16px;
  font-weight: 650;
  line-height: 1.5;
}

.section-empty-state p {
  margin-top: 6px;
  color: var(--color-muted);
  font-size: 13px;
  line-height: 1.5;
}

.section-empty-state-compact p {
  max-width: 180px;
  margin-top: 0;
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

  .workspace-detail-grid {
    grid-template-columns: minmax(0, 1fr);
    grid-template-rows: minmax(300px, 1.4fr) minmax(220px, 1fr);
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

  .tool-debugger {
    grid-template-columns: minmax(0, 1fr);
  }

  .tool-summary {
    border-right: 0;
    border-bottom: 1px solid var(--color-border);
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

  .workspace-canvas {
    grid-template-rows: auto minmax(0, 1fr);
    gap: 8px;
    padding: 8px;
  }

  .param-fields {
    grid-template-columns: minmax(0, 1fr);
  }

  .tool-summary,
  .params-form {
    padding: 16px;
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
