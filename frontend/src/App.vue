<script setup lang="ts">
import { onMounted } from 'vue'

import { useBackendStore } from '@/stores/backend'

const backend = useBackendStore()

onMounted(() => backend.checkHealth())
</script>

<template>
  <el-container class="app-shell">
    <el-header class="app-header">
      <div>
        <h1>MCP Inspector</h1>
        <p>服务开发与调试工作台</p>
      </div>
      <el-tag :type="backend.connected ? 'success' : 'danger'" effect="plain">
        {{ backend.connected ? '后端已连接' : '后端未连接' }}
      </el-tag>
    </el-header>

    <el-main class="app-main">
      <section class="status-panel" aria-labelledby="service-status-title">
        <div class="panel-heading">
          <div>
            <h2 id="service-status-title">服务状态</h2>
            <p>FastAPI 与 MCP Streamable HTTP 服务</p>
          </div>
          <el-button :loading="backend.loading" @click="backend.checkHealth">
            重新检测
          </el-button>
        </div>

        <el-alert
          v-if="backend.error"
          :title="backend.error"
          type="error"
          :closable="false"
          show-icon
        />

        <el-descriptions v-else-if="backend.health" :column="1" border>
          <el-descriptions-item label="服务名称">
            {{ backend.health.name }}
          </el-descriptions-item>
          <el-descriptions-item label="版本">
            {{ backend.health.version }}
          </el-descriptions-item>
          <el-descriptions-item label="MCP 端点">
            <code>/mcp</code>
          </el-descriptions-item>
        </el-descriptions>

        <el-skeleton v-else :rows="3" animated />
      </section>
    </el-main>
  </el-container>
</template>
