'use client'

import { useCallback, useEffect, useState } from 'react'

import {
  api,
  type ApiKey,
  type LogEntry,
  type Usage,
  type UsageSummary,
} from '@/lib/api-client'

export interface ConsoleData {
  usage: Usage | null
  summary: UsageSummary | null
  logs: LogEntry[]
  keys: ApiKey[]
}

const EMPTY_DATA: ConsoleData = {
  usage: null,
  summary: null,
  logs: [],
  keys: [],
}

export function useConsoleData() {
  const [data, setData] = useState<ConsoleData>(EMPTY_DATA)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    setLoading(true)
    const results = await Promise.allSettled([
      api.getUsage(),
      api.getUsageSummary('30d'),
      api.getLogs(3),
      api.listApiKeys(),
    ])
    const [usage, summary, logs, keys] = results
    setData({
      usage: usage.status === 'fulfilled' ? usage.value : null,
      summary: summary.status === 'fulfilled' ? summary.value : null,
      logs: logs.status === 'fulfilled' ? logs.value.logs : [],
      keys: keys.status === 'fulfilled' ? keys.value.keys : [],
    })
    const failed = results.filter((result) => result.status === 'rejected').length
    setError(failed ? `${failed} account section${failed === 1 ? '' : 's'} unavailable.` : null)
    setLoading(false)
  }, [])

  useEffect(() => {
    const timer = setTimeout(() => void refresh(), 0)
    return () => clearTimeout(timer)
  }, [refresh])

  return { data, error, loading, refresh }
}
