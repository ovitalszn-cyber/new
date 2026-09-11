"use client"

import { useCallback, useEffect, useState, type ReactNode } from "react"

import type { DemoCs2PropsResponse } from "@/lib/demo/live-cs2-props"

function JsonLine({ children }: { children: ReactNode }) {
  return <>{children}{"\n"}</>
}

function renderSample(data: DemoCs2PropsResponse) {
  const prop = data.props[0]
  return (
    <code>
      <JsonLine>
        <span className="text-white">{"{"}</span>
      </JsonLine>
      <JsonLine>
        {"  "}
        <span className="token-key">&quot;source&quot;</span>:{" "}
        <span className="token-string">&quot;{data.source}&quot;</span>,
      </JsonLine>
      <JsonLine>
        {"  "}
        <span className="token-key">&quot;sport&quot;</span>:{" "}
        <span className="token-string">&quot;{data.sport}&quot;</span>,
      </JsonLine>
      <JsonLine>
        {"  "}
        <span className="token-key">&quot;props&quot;</span>:{" "}
        <span className="text-white">[</span>
      </JsonLine>
      <JsonLine>
        {"    "}
        <span className="text-white">{"{"}</span>
      </JsonLine>
      <JsonLine>
        {"      "}
        <span className="token-key">&quot;propId&quot;</span>:{" "}
        <span className="token-string">&quot;{prop.propId}&quot;</span>,
      </JsonLine>
      <JsonLine>
        {"      "}
        <span className="token-key">&quot;player_name&quot;</span>:{" "}
        <span className="token-string">&quot;{prop.player_name}&quot;</span>,
      </JsonLine>
      <JsonLine>
        {"      "}
        <span className="token-key">&quot;stat_type&quot;</span>:{" "}
        <span className="token-string">&quot;{prop.stat_type}&quot;</span>,
      </JsonLine>
      <JsonLine>
        {"      "}
        <span className="token-key">&quot;line&quot;</span>:{" "}
        <span className="token-number">{prop.line}</span>,
      </JsonLine>
      <JsonLine>
        {"      "}
        <span className="token-key">&quot;odds&quot;</span>:{" "}
        <span className="token-number">
          {prop.odds === null ? "null" : prop.odds}
        </span>
        ,
      </JsonLine>
      <JsonLine>
        {"      "}
        <span className="token-key">&quot;direction&quot;</span>:{" "}
        <span className="token-string">&quot;{prop.direction}&quot;</span>,
      </JsonLine>
      <JsonLine>
        {"      "}
        <span className="token-key">&quot;team&quot;</span>:{" "}
        <span className="token-string">&quot;{prop.team}&quot;</span>,
      </JsonLine>
      <JsonLine>
        {"      "}
        <span className="token-key">&quot;book_name&quot;</span>:{" "}
        <span className="token-string">&quot;{prop.book_name}&quot;</span>,
      </JsonLine>
      <JsonLine>
        {"      "}
        <span className="token-key">&quot;event_time&quot;</span>:{" "}
        <span className="token-string">&quot;{prop.event_time}&quot;</span>,
      </JsonLine>
      <JsonLine>
        {"      "}
        <span className="token-key">&quot;links&quot;</span>:{" "}
        <span className="text-white">{"{"}</span>
      </JsonLine>
      <JsonLine>
        {"        "}
        <span className="token-key">&quot;market&quot;</span>:{" "}
        <span className="token-string">&quot;{prop.links.market}&quot;</span>
      </JsonLine>
      <JsonLine>
        {"      "}
        <span className="text-white">{"}"}</span>
      </JsonLine>
      <JsonLine>
        {"    "}
        <span className="text-white">{"}"}</span>
      </JsonLine>
      <JsonLine>
        {"  "}
        <span className="text-white">]</span>
      </JsonLine>
      <span className="text-white">{"}"}</span>
    </code>
  )
}

export function LiveCs2PropsPane() {
  const [data, setData] = useState<DemoCs2PropsResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch("/api/demo/cs2-props", { cache: "no-store" })
      const body = (await response.json()) as DemoCs2PropsResponse & {
        detail?: string
      }
      if (!response.ok) {
        throw new Error(body.detail || `Demo failed (${response.status})`)
      }
      if (!body.props?.[0]) {
        throw new Error("No live prop returned")
      }
      setData(body)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load live props")
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void load()
  }, [load])

  return (
    <button
      type="button"
      onClick={() => void load()}
      className="block w-full text-left cursor-pointer"
      title="Click to refresh live CS2 player props"
      aria-label="Refresh live CS2 props sample"
    >
      <pre className="font-mono text-xs leading-normal min-h-[220px]">
        {loading && !data ? (
          <code className="text-zinc-500">{"// loading live CS2 props…"}</code>
        ) : error && !data ? (
          <code className="text-red-300">{`// ${error}`}</code>
        ) : data ? (
          renderSample(data)
        ) : null}
      </pre>
    </button>
  )
}
