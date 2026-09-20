import axios from 'axios'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { http } from '@/api/http'

interface HealthResponse {
  name: string
  status: string
  version: string
}

export const useBackendStore = defineStore('backend', () => {
  const health = ref<HealthResponse | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const connected = computed(() => health.value?.status === 'ok')

  async function checkHealth() {
    loading.value = true
    error.value = null

    try {
      const response = await http.get<HealthResponse>('/health')
      health.value = response.data
    } catch (reason) {
      health.value = null
      error.value = axios.isAxiosError(reason)
        ? reason.message
        : '无法连接后端服务'
    } finally {
      loading.value = false
    }
  }

  return { health, loading, error, connected, checkHealth }
})
