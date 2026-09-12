import type { Metadata } from "next"
import Link from "next/link"

import { DocsShell } from "@/components/docs/DocsShell"
import {
  MCP_GROUP_LABEL,
  MCP_SPORTS,
  MCP_TIER_LABEL,
  MCP_TOOLS,
  type McpTool,
} from "@/lib/mcp/catalog"
import { MCP_SNIPPET } from "@/lib/seo/copy"

export const metadata: Metadata = {
  title: "MCP | KashRock Docs",
  description:
    "KashRock MCP for Cursor and Claude: uvx kashrock-mcp, Google login, full tier-scoped tool catalog.",
}

const GROUPS: McpTool["group"][] = ["session", "board", "players", "schedule"]

export default function DocsMcpPage() {
  return (
    <DocsShell active="mcp">
      <h1 className="text-4xl font-semibold text-white mb-4 tracking-tight">MCP</h1>
      <p className="text-lg text-zinc-400 leading-relaxed mb-8">
        Prefer MCP over hunting HTTP paths. Paste the snippet in Cursor or Claude Desktop, say
        “log in to KashRock,” then ask in plain English. Marketing guide:{" "}
        <Link href="/mcp" className="text-white underline">
          /mcp
        </Link>
        .
      </p>

      <section className="mb-16">
        <h2 className="text-2xl font-semibold text-white mb-4">Setup</h2>
        <p className="text-zinc-400 mb-4 text-sm">
          Needs{" "}
          <a href="https://docs.astral.sh/uv/" className="text-white underline">
            uv
          </a>
          . Package: <code className="text-white">kashrock-mcp</code> on PyPI.
        </p>
        <pre className="p-5 font-mono text-xs leading-normal overflow-x-auto text-zinc-300 bg-[#0C0D0F] border border-white/10 rounded-lg mb-4">
          {MCP_SNIPPET}
        </pre>
        <p className="text-sm text-zinc-500">
          Optional env <code className="text-zinc-400">KASHROCK_API_KEY</code> skips browser login.
          Never paste a key into chat.
        </p>
      </section>

      <section className="mb-16">
        <h2 className="text-2xl font-semibold text-white mb-4">Sports</h2>
        <div className="flex flex-wrap gap-2">
          {MCP_SPORTS.map((s) => (
            <code
              key={s}
              className="px-2 py-1 bg-white/5 border border-white/10 rounded text-xs text-emerald-400"
            >
              {s}
            </code>
          ))}
        </div>
      </section>

      <section className="mb-16">
        <h2 className="text-2xl font-semibold text-white mb-2">Plans</h2>
        <ul className="text-sm text-zinc-400 space-y-2 list-disc pl-5 mb-8">
          <li>
            <span className="text-white">Sandbox</span> — session tools + CS2 props / coverage
          </li>
          <li>
            <span className="text-white">Hobby</span> — all sports, moneylines, lines, research,
            streams, H2H
          </li>
          <li>
            <span className="text-white">Builder+</span> — matches, live in-game KDA (
            <code className="text-zinc-300">get_live_boxscore</code>), gamelogs, finished
            boxscores, results, history tape
          </li>
        </ul>
        <p className="text-sm text-zinc-500">
          Call <code className="text-zinc-400">list_capabilities</code> or{" "}
          <code className="text-zinc-400">whoami</code> after login. Stacks are not exposed via MCP.
        </p>
      </section>

      <section className="mb-16">
        <h2 className="text-2xl font-semibold text-white mb-6">Tools</h2>
        {GROUPS.map((group) => (
          <div key={group} className="mb-10">
            <h3 className="text-lg font-semibold text-white mb-3">{MCP_GROUP_LABEL[group]}</h3>
            <div className="overflow-x-auto border border-white/5 rounded-lg bg-[#0C0D0F]">
              <table className="w-full text-left text-sm">
                <thead className="bg-white/5 text-zinc-500">
                  <tr>
                    <th className="px-4 py-3">Tool</th>
                    <th className="px-4 py-3">When</th>
                    <th className="px-4 py-3">Min plan</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5 text-zinc-400">
                  {MCP_TOOLS.filter((t) => t.group === group).map((t) => (
                    <tr key={t.id}>
                      <td className="px-4 py-3 font-mono text-emerald-400 whitespace-nowrap">
                        {t.id}
                      </td>
                      <td className="px-4 py-3">{t.when}</td>
                      <td className="px-4 py-3 whitespace-nowrap">{MCP_TIER_LABEL[t.tier]}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ))}
      </section>
    </DocsShell>
  )
}
