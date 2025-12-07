'use client';

import { useState } from 'react';
import DashboardLayout from '@/components/DashboardLayout';

interface SupportTicket {
  id: string;
  subject: string;
  message: string;
  status: 'OPEN' | 'IN_PROGRESS' | 'RESOLVED' | 'CLOSED';
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
  category: string;
  createdAt: string;
  updatedAt: string;
  replies: number;
}

export default function SupportPage() {
  const [tickets, setTickets] = useState<SupportTicket[]>([
    {
      id: '1',
      subject: 'API rate limit questions',
      message: 'I need help understanding the rate limits for the Pro tier. Can you clarify?',
      status: 'RESOLVED',
      priority: 'MEDIUM',
      category: 'API Usage',
      createdAt: '2025-01-10',
      updatedAt: '2025-01-11',
      replies: 2,
    },
    {
      id: '2',
      subject: 'Historical data export issue',
      message: 'The export engine seems to be timing out when I try to export 50k rows of historical data.',
      status: 'IN_PROGRESS',
      priority: 'HIGH',
      category: 'Technical Issue',
      createdAt: '2025-01-12',
      updatedAt: '2025-01-13',
      replies: 3,
    },
  ]);

  const [showNewTicketModal, setShowNewTicketModal] = useState(false);
  const [newTicket, setNewTicket] = useState({
    subject: '',
    message: '',
    category: 'General',
    priority: 'MEDIUM',
  });

  const categories = [
    'General',
    'API Usage',
    'Billing',
    'Technical Issue',
    'Feature Request',
    'Bug Report',
  ];

  const priorities = [
    { value: 'LOW', label: 'Low', color: 'bg-[#10B981]/10 text-[#10B981]' },
    { value: 'MEDIUM', label: 'Medium', color: 'bg-[#F59E0B]/10 text-[#F59E0B]' },
    { value: 'HIGH', label: 'High', color: 'bg-[#EF4444]/10 text-[#EF4444]' },
    { value: 'URGENT', label: 'Urgent', color: 'bg-[#DC2626]/10 text-[#DC2626]' },
  ];

  const getStatusBadge = (status: string) => {
    const statusStyles = {
      OPEN: 'bg-[#7C3AED]/10 text-[#7C3AED]',
      IN_PROGRESS: 'bg-[#F59E0B]/10 text-[#F59E0B]',
      RESOLVED: 'bg-[#10B981]/10 text-[#10B981]',
      CLOSED: 'bg-[#635F69]/10 text-[#635F69]',
    };
    return statusStyles[status as keyof typeof statusStyles] || statusStyles.OPEN;
  };

  const createTicket = () => {
    const ticket: SupportTicket = {
      id: String(tickets.length + 1),
      subject: newTicket.subject,
      message: newTicket.message,
      status: 'OPEN',
      priority: newTicket.priority as any,
      category: newTicket.category,
      createdAt: new Date().toISOString().split('T')[0],
      updatedAt: new Date().toISOString().split('T')[0],
      replies: 0,
    };
    setTickets([ticket, ...tickets]);
    setNewTicket({ subject: '', message: '', category: 'General', priority: 'MEDIUM' });
    setShowNewTicketModal(false);
  };

  return (
    <DashboardLayout>
      {/* Page Header */}
      <div className="mb-8">
        <h1 
          className="text-3xl sm:text-4xl font-black text-[#332F3A] mb-2"
          style={{ fontFamily: 'Nunito, sans-serif' }}
        >
          Support Center
        </h1>
        <p className="text-[#635F69]">
          Get help with your account, API usage, and technical questions.
        </p>
      </div>

      {/* Quick Actions */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="clay-card shadow-clay-card p-6 text-center hover:-translate-y-2 transition-all cursor-pointer">
          <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-[#7C3AED]/10 flex items-center justify-center">
            <svg className="w-6 h-6 text-[#7C3AED]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          </div>
          <h3 className="font-bold text-[#332F3A] mb-1" style={{ fontFamily: 'Nunito, sans-serif' }}>
            Live Chat
          </h3>
          <p className="text-sm text-[#635F69]">Chat with our support team</p>
        </div>

        <div className="clay-card shadow-clay-card p-6 text-center hover:-translate-y-2 transition-all cursor-pointer">
          <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-[#10B981]/10 flex items-center justify-center">
            <svg className="w-6 h-6 text-[#10B981]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>
          <h3 className="font-bold text-[#332F3A] mb-1" style={{ fontFamily: 'Nunito, sans-serif' }}>
            Documentation
          </h3>
          <p className="text-sm text-[#635F69]">Browse our API docs</p>
        </div>

        <div className="clay-card shadow-clay-card p-6 text-center hover:-translate-y-2 transition-all cursor-pointer">
          <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-[#F59E0B]/10 flex items-center justify-center">
            <svg className="w-6 h-6 text-[#F59E0B]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="font-bold text-[#332F3A] mb-1" style={{ fontFamily: 'Nunito, sans-serif' }}>
            FAQ
          </h3>
          <p className="text-sm text-[#635F69]">Common questions answered</p>
        </div>

        <div className="clay-card shadow-clay-card p-6 text-center hover:-translate-y-2 transition-all cursor-pointer">
          <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-[#EF4444]/10 flex items-center justify-center">
            <svg className="w-6 h-6 text-[#EF4444]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="font-bold text-[#332F3A] mb-1" style={{ fontFamily: 'Nunito, sans-serif' }}>
            Status Page
          </h3>
          <p className="text-sm text-[#635F69]">Check system status</p>
        </div>
      </div>

      {/* Create New Ticket Button */}
      <div className="mb-8">
        <button
          onClick={() => setShowNewTicketModal(true)}
          className="h-12 px-6 rounded-[20px] bg-gradient-to-br from-[#A78BFA] to-[#7C3AED] text-white font-bold shadow-clay-button hover:shadow-clay-button-hover hover:-translate-y-1 active:scale-[0.92] transition-all duration-200 flex items-center gap-2"
          style={{ fontFamily: 'Nunito, sans-serif' }}
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Create New Ticket
        </button>
      </div>

      {/* Support Tickets */}
      {tickets.length === 0 ? (
        <div className="clay-card shadow-clay-card p-12 text-center">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-[#7C3AED]/10 flex items-center justify-center">
            <svg className="w-8 h-8 text-[#7C3AED]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
            </svg>
          </div>
          <h3 className="text-xl font-bold text-[#332F3A] mb-2" style={{ fontFamily: 'Nunito, sans-serif' }}>
            No support tickets yet
          </h3>
          <p className="text-[#635F69]">
            Click "Create New Ticket" to get help from our support team!
          </p>
        </div>
      ) : (
        <div className="clay-card shadow-clay-card p-6">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-[#E5E1EF]">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-[#635F69]">Subject</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-[#635F69]">Category</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-[#635F69]">Priority</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-[#635F69]">Status</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-[#635F69]">Replies</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-[#635F69]">Last Updated</th>
                </tr>
              </thead>
              <tbody>
                {tickets.map((ticket) => (
                  <tr key={ticket.id} className="border-b border-[#E5E1EF]/50 hover:bg-[#7C3AED]/5 transition-colors cursor-pointer">
                    <td className="py-4 px-4">
                      <div>
                        <p className="font-bold text-[#332F3A]" style={{ fontFamily: 'Nunito, sans-serif' }}>
                          {ticket.subject}
                        </p>
                        <p className="text-xs text-[#635F69]">Created {ticket.createdAt}</p>
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-[#7C3AED]/10 text-[#7C3AED]">
                        {ticket.category}
                      </span>
                    </td>
                    <td className="py-4 px-4">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${
                        priorities.find(p => p.value === ticket.priority)?.color
                      }`}>
                        {priorities.find(p => p.value === ticket.priority)?.label}
                      </span>
                    </td>
                    <td className="py-4 px-4">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${getStatusBadge(ticket.status)}`}>
                        {ticket.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="py-4 px-4 text-[#635F69] font-medium">
                      {ticket.replies}
                    </td>
                    <td className="py-4 px-4 text-[#635F69] font-medium">
                      {ticket.updatedAt}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* New Ticket Modal */}
      {showNewTicketModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/30 backdrop-blur-sm">
          <div className="clay-card shadow-clay-surface p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-black text-[#332F3A] mb-4" style={{ fontFamily: 'Nunito, sans-serif' }}>
              Create Support Ticket
            </h2>
            <p className="text-[#635F69] mb-6">
              Describe your issue and we'll get back to you as soon as possible.
            </p>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-[#332F3A] mb-2">Subject</label>
                <input
                  type="text"
                  value={newTicket.subject}
                  onChange={(e) => setNewTicket({ ...newTicket, subject: e.target.value })}
                  placeholder="Brief description of your issue"
                  className="w-full h-12 px-5 rounded-[16px] bg-[#EFEBF5] shadow-clay-pressed text-[#332F3A] placeholder-[#635F69]/50 font-medium focus:outline-none focus:ring-2 focus:ring-[#7C3AED]/30 transition-all"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-[#332F3A] mb-2">Category</label>
                  <select
                    value={newTicket.category}
                    onChange={(e) => setNewTicket({ ...newTicket, category: e.target.value })}
                    className="w-full h-12 px-5 rounded-[16px] bg-[#EFEBF5] shadow-clay-pressed text-[#332F3A] font-medium focus:outline-none focus:ring-2 focus:ring-[#7C3AED]/30 transition-all"
                  >
                    {categories.map(cat => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-[#332F3A] mb-2">Priority</label>
                  <select
                    value={newTicket.priority}
                    onChange={(e) => setNewTicket({ ...newTicket, priority: e.target.value as any })}
                    className="w-full h-12 px-5 rounded-[16px] bg-[#EFEBF5] shadow-clay-pressed text-[#332F3A] font-medium focus:outline-none focus:ring-2 focus:ring-[#7C3AED]/30 transition-all"
                  >
                    {priorities.map(priority => (
                      <option key={priority.value} value={priority.value}>{priority.label}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-[#332F3A] mb-2">Message</label>
                <textarea
                  value={newTicket.message}
                  onChange={(e) => setNewTicket({ ...newTicket, message: e.target.value })}
                  placeholder="Provide detailed information about your issue..."
                  rows={6}
                  className="w-full px-5 py-3 rounded-[16px] bg-[#EFEBF5] shadow-clay-pressed text-[#332F3A] placeholder-[#635F69]/50 font-medium focus:outline-none focus:ring-2 focus:ring-[#7C3AED]/30 transition-all resize-none"
                />
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowNewTicketModal(false)}
                className="flex-1 h-12 rounded-[20px] bg-white text-[#635F69] font-bold shadow-clay-card hover:shadow-clay-card-hover transition-all"
              >
                Cancel
              </button>
              <button
                onClick={createTicket}
                disabled={!newTicket.subject || !newTicket.message}
                className="flex-1 h-12 rounded-[20px] bg-gradient-to-br from-[#A78BFA] to-[#7C3AED] text-white font-bold shadow-clay-button hover:shadow-clay-button-hover transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Create Ticket
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Vercel ChatBot Placeholder */}
      <div className="fixed bottom-6 right-6 z-40">
        <div className="clay-card shadow-clay-card p-4 rounded-full bg-gradient-to-br from-[#A78BFA] to-[#7C3AED] text-white hover:-translate-y-1 transition-all cursor-pointer">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        </div>
      </div>
    </DashboardLayout>
  );
}
