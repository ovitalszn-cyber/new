"use client";

import { useState, useEffect } from "react";

interface UserUsage {
    user_id: string; // Added user_id
    email: string;
    google_id: string;
    total_requests: number;
    total_credits: number;
}

interface EndpointStat {
    endpoint: string;
    method: string;
    count: number;
    total_credits: number;
}

export default function AdminUsagePage() {
    const [users, setUsers] = useState<UserUsage[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    // State for expandable rows
    const [expandedUserId, setExpandedUserId] = useState<string | null>(null);
    const [endpointStats, setEndpointStats] = useState<{ [key: string]: EndpointStat[] }>({});
    const [loadingStats, setLoadingStats] = useState<{ [key: string]: boolean }>({});

    useEffect(() => {
        fetchUsage();
    }, []);

    const fetchUsage = async () => {
        try {
            const res = await fetch("http://localhost:8000/v6/admin/usage/users", {
                headers: { "X-Admin-Secret": "dev_admin_secret" }
            });
            if (!res.ok) throw new Error("Failed to fetch data");
            const data = await res.json();
            setUsers(data);
        } catch (err) {
            setError("Error loading admin data");
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const toggleExpand = async (userId: string) => {
        if (expandedUserId === userId) {
            setExpandedUserId(null); // Collapse
            return;
        }

        setExpandedUserId(userId);

        // Fetch stats if not already loaded
        if (!endpointStats[userId]) {
            setLoadingStats(prev => ({ ...prev, [userId]: true }));
            try {
                const res = await fetch(`http://localhost:8000/v6/admin/usage/users/${userId}/endpoints`, {
                    headers: { "X-Admin-Secret": "dev_admin_secret" }
                });
                if (res.ok) {
                    const stats = await res.json();
                    setEndpointStats(prev => ({ ...prev, [userId]: stats }));
                }
            } catch (err) {
                console.error("Failed to load user stats", err);
            } finally {
                setLoadingStats(prev => ({ ...prev, [userId]: false }));
            }
        }
    };

    return (
        <div className="p-8 max-w-7xl mx-auto">
            <h1 className="text-3xl font-bold mb-8 text-indigo-400">Admin Dashboard: User Usage</h1>

            {loading && <div className="text-gray-400">Loading usage data...</div>}
            {error && <div className="text-red-400 mb-4">{error}</div>}

            {!loading && !error && (
                <div className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden shadow-xl">
                    <table className="w-full text-left border-collapse">
                        <thead className="bg-gray-800 text-gray-400 uppercase text-xs font-semibold">
                            <tr>
                                <th className="px-6 py-4">User Email</th>
                                <th className="px-6 py-4">Total Requests</th>
                                <th className="px-6 py-4">Total Credits</th>
                                <th className="px-6 py-4">Est. Cost</th>
                                <th className="px-6 py-4"></th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-800">
                            {users.map((user) => (
                                <>
                                    <tr
                                        key={user.user_id}
                                        onClick={() => toggleExpand(user.user_id)}
                                        className="hover:bg-gray-800/50 transition-colors cursor-pointer group"
                                    >
                                        <td className="px-6 py-4 font-medium text-white flex items-center gap-2">
                                            <span className={`transform transition-transform ${expandedUserId === user.user_id ? 'rotate-90' : ''}`}>
                                                ▶
                                            </span>
                                            {user.email || "Unknown"}
                                            {user.email === "test@kashrock.com" && (
                                                <span className="px-2 py-0.5 rounded text-[10px] bg-indigo-500/20 text-indigo-300">
                                                    TEST
                                                </span>
                                            )}
                                        </td>
                                        <td className="px-6 py-4 text-gray-300">
                                            {user.total_requests.toLocaleString()}
                                        </td>
                                        <td className="px-6 py-4 text-emerald-400 font-mono">
                                            {user.total_credits.toLocaleString()}
                                        </td>
                                        <td className="px-6 py-4 text-gray-400">
                                            ${(user.total_credits * 0.0001).toFixed(4)}
                                        </td>
                                        <td className="px-6 py-4 text-right text-sm text-gray-500 group-hover:text-indigo-400">
                                            {expandedUserId === user.user_id ? 'Less Details' : 'More Details'}
                                        </td>
                                    </tr>

                                    {expandedUserId === user.user_id && (
                                        <tr className="bg-gray-800/30">
                                            <td colSpan={5} className="px-6 py-4">
                                                <div className="pl-6 border-l-2 border-indigo-500/50 ml-2">
                                                    <h4 className="text-xs font-bold text-gray-400 uppercase mb-3">Top Endpoints</h4>

                                                    {loadingStats[user.user_id] ? (
                                                        <div className="text-sm text-gray-500 py-2">Loading endpoints...</div>
                                                    ) : (
                                                        <table className="w-full text-sm">
                                                            <thead className="text-gray-500 border-b border-gray-700/50">
                                                                <tr>
                                                                    <th className="pb-2 text-left font-normal">Endpoint</th>
                                                                    <th className="pb-2 text-left font-normal">Method</th>
                                                                    <th className="pb-2 text-right font-normal">Calls</th>
                                                                    <th className="pb-2 text-right font-normal">Credits</th>
                                                                </tr>
                                                            </thead>
                                                            <tbody className="divide-y divide-gray-700/30">
                                                                {(endpointStats[user.user_id] || []).map((stat, i) => (
                                                                    <tr key={i} className="group/row">
                                                                        <td className="py-2 text-gray-300 font-mono text-xs">{stat.endpoint}</td>
                                                                        <td className="py-2 text-gray-500 text-xs">
                                                                            <span className={`px-1.5 py-0.5 rounded ${stat.method === 'GET' ? 'bg-blue-900/30 text-blue-400' : 'bg-gray-700 text-gray-300'
                                                                                }`}>
                                                                                {stat.method}
                                                                            </span>
                                                                        </td>
                                                                        <td className="py-2 text-right text-gray-300">{stat.count}</td>
                                                                        <td className="py-2 text-right text-emerald-500/80">{stat.total_credits}</td>
                                                                    </tr>
                                                                ))}
                                                                {(!endpointStats[user.user_id] || endpointStats[user.user_id].length === 0) && (
                                                                    <tr>
                                                                        <td colSpan={4} className="py-4 text-center text-gray-500 italic">
                                                                            No detailed usage found.
                                                                        </td>
                                                                    </tr>
                                                                )}
                                                            </tbody>
                                                        </table>
                                                    )}
                                                </div>
                                            </td>
                                        </tr>
                                    )}
                                </>
                            ))}

                            {users.length === 0 && (
                                <tr>
                                    <td colSpan={5} className="px-6 py-8 text-center text-gray-500">
                                        No usage data found.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            )}

            <div className="mt-8 text-sm text-gray-500">
                <p>🔒 Secure Admin Access Only. Data source: Local SQLite Database.</p>
            </div>
        </div>
    );
}
