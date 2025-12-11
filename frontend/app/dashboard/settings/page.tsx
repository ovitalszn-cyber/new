'use client';

import { useState } from 'react';
import DashboardLayout from '@/components/DashboardLayout';

interface UserSettings {
  profile: {
    name: string;
    email: string;
    company: string;
    timezone: string;
    language: string;
  };
  notifications: {
    emailAlerts: boolean;
    apiUsageAlerts: boolean;
    billingAlerts: boolean;
    productUpdates: boolean;
    securityAlerts: boolean;
  };
  api: {
    rateLimitAlerts: boolean;
    errorReporting: boolean;
  };
  billing: {
    plan: string;
    autoRenew: boolean;
    billingEmail: string;
  };
  security: {
    twoFactorEnabled: boolean;
    ipWhitelist: string[];
    apiKeyRotation: boolean;
  };
}

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState('profile');
  const [settings, setSettings] = useState<UserSettings>({
    profile: {
      name: 'John Doe',
      email: 'john@example.com',
      company: 'Acme Corp',
      timezone: 'UTC',
      language: 'English',
    },
    notifications: {
      emailAlerts: true,
      apiUsageAlerts: true,
      billingAlerts: true,
      productUpdates: false,
      securityAlerts: true,
    },
    api: {
      rateLimitAlerts: true,
      errorReporting: true,
    },
    billing: {
      plan: 'Developer',
      autoRenew: true,
      billingEmail: 'john@example.com',
    },
    security: {
      twoFactorEnabled: false,
      ipWhitelist: [],
      apiKeyRotation: false,
    },
  });

  const tabs = [
    { id: 'profile', label: 'Profile', icon: 'user' },
    { id: 'notifications', label: 'Notifications', icon: 'bell' },
    { id: 'api', label: 'API', icon: 'code' },
    { id: 'billing', label: 'Billing', icon: 'credit-card' },
    { id: 'security', label: 'Security', icon: 'shield' },
  ];

  const updateSetting = (category: keyof UserSettings, field: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [field]: value,
      },
    }));
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'profile':
        return (
          <div className="space-y-6">
            <div className="grid sm:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-[#332F3A] mb-2">Name</label>
                <input
                  type="text"
                  value={settings.profile.name}
                  onChange={(e) => updateSetting('profile', 'name', e.target.value)}
                  className="w-full h-12 px-5 rounded-[16px] bg-[#EFEBF5] shadow-clay-pressed text-[#332F3A] font-medium focus:outline-none focus:ring-2 focus:ring-[#7C3AED]/30 transition-all"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-[#332F3A] mb-2">Email</label>
                <input
                  type="email"
                  value={settings.profile.email}
                  onChange={(e) => updateSetting('profile', 'email', e.target.value)}
                  className="w-full h-12 px-5 rounded-[16px] bg-[#EFEBF5] shadow-clay-pressed text-[#332F3A] font-medium focus:outline-none focus:ring-2 focus:ring-[#7C3AED]/30 transition-all"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-[#332F3A] mb-2">Company</label>
                <input
                  type="text"
                  value={settings.profile.company}
                  onChange={(e) => updateSetting('profile', 'company', e.target.value)}
                  className="w-full h-12 px-5 rounded-[16px] bg-[#EFEBF5] shadow-clay-pressed text-[#332F3A] font-medium focus:outline-none focus:ring-2 focus:ring-[#7C3AED]/30 transition-all"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-[#332F3A] mb-2">Timezone</label>
                <select
                  value={settings.profile.timezone}
                  onChange={(e) => updateSetting('profile', 'timezone', e.target.value)}
                  className="w-full h-12 px-5 rounded-[16px] bg-[#EFEBF5] shadow-clay-pressed text-[#332F3A] font-medium focus:outline-none focus:ring-2 focus:ring-[#7C3AED]/30 transition-all"
                >
                  <option value="UTC">UTC</option>
                  <option value="America/New_York">Eastern Time (ET)</option>
                  <option value="America/Chicago">Central Time (CT)</option>
                  <option value="America/Denver">Mountain Time (MT)</option>
                  <option value="America/Los_Angeles">Pacific Time (PT)</option>
                  <option value="Europe/London">London (GMT)</option>
                  <option value="Europe/Paris">Paris (CET)</option>
                  <option value="Asia/Tokyo">Tokyo (JST)</option>
                  <option value="Australia/Sydney">Sydney (AEDT)</option>
                </select>
              </div>
            </div>
          </div>
        );
      case 'notifications':
        return (
          <div className="space-y-6">
            <div className="space-y-4">
              {Object.entries(settings.notifications).map(([key, value]) => (
                <div key={key} className="flex items-center justify-between p-4 clay-card shadow-clay-card">
                  <div>
                    <p className="font-bold text-[#332F3A]" style={{ fontFamily: 'Nunito, sans-serif' }}>
                      {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                    </p>
                    <p className="text-sm text-[#635F69]">
                      {key === 'emailAlerts' && 'Receive email notifications about your account'}
                      {key === 'apiUsageAlerts' && 'Get alerts when you approach API limits'}
                      {key === 'billingAlerts' && 'Notifications about billing and payments'}
                      {key === 'productUpdates' && 'Updates about new features and improvements'}
                      {key === 'securityAlerts' && 'Security-related notifications'}
                    </p>
                  </div>
                  <button
                    onClick={() => updateSetting('notifications', key, !value)}
                    className={`w-14 h-8 rounded-full transition-colors ${
                      value ? 'bg-[#7C3AED]' : 'bg-[#E5E1EF]'
                    } relative`}
                  >
                    <div className={`w-6 h-6 rounded-full bg-white transition-transform absolute top-1 ${
                      value ? 'translate-x-7' : 'translate-x-1'
                    }`} />
                  </button>
                </div>
              ))}
            </div>
          </div>
        );
      case 'api':
        return (
          <div className="space-y-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 clay-card shadow-clay-card">
                <div>
                  <p className="font-bold text-[#332F3A]" style={{ fontFamily: 'Nunito, sans-serif' }}>
                    Rate Limit Alerts
                  </p>
                  <p className="text-sm text-[#635F69]">Get notified when approaching API limits</p>
                </div>
                <button
                  onClick={() => updateSetting('api', 'rateLimitAlerts', !settings.api.rateLimitAlerts)}
                  className={`w-14 h-8 rounded-full transition-colors ${
                    settings.api.rateLimitAlerts ? 'bg-[#7C3AED]' : 'bg-[#E5E1EF]'
                  } relative`}
                >
                  <div className={`w-6 h-6 rounded-full bg-white transition-transform absolute top-1 ${
                    settings.api.rateLimitAlerts ? 'translate-x-7' : 'translate-x-1'
                  }`} />
                </button>
              </div>
              <div className="flex items-center justify-between p-4 clay-card shadow-clay-card">
                <div>
                  <p className="font-bold text-[#332F3A]" style={{ fontFamily: 'Nunito, sans-serif' }}>
                    Error Reporting
                  </p>
                  <p className="text-sm text-[#635F69]">Automatically report API errors</p>
                </div>
                <button
                  onClick={() => updateSetting('api', 'errorReporting', !settings.api.errorReporting)}
                  className={`w-14 h-8 rounded-full transition-colors ${
                    settings.api.errorReporting ? 'bg-[#7C3AED]' : 'bg-[#E5E1EF]'
                  } relative`}
                >
                  <div className={`w-6 h-6 rounded-full bg-white transition-transform absolute top-1 ${
                    settings.api.errorReporting ? 'translate-x-7' : 'translate-x-1'
                  }`} />
                </button>
              </div>
            </div>
          </div>
        );
      case 'billing':
        return (
          <div className="space-y-6">
            <div className="clay-card shadow-clay-card p-6">
              <h3 className="font-bold text-[#332F3A] mb-4" style={{ fontFamily: 'Nunito, sans-serif' }}>
                Current Plan: <span className="text-[#7C3AED]">{settings.billing.plan}</span>
              </h3>
              <button className="h-12 px-6 rounded-[20px] bg-gradient-to-br from-[#A78BFA] to-[#7C3AED] text-white font-bold shadow-clay-button hover:shadow-clay-button-hover transition-all">
                Upgrade Plan
              </button>
            </div>
            <div>
              <label className="block text-sm font-medium text-[#332F3A] mb-2">Billing Email</label>
              <input
                type="email"
                value={settings.billing.billingEmail}
                onChange={(e) => updateSetting('billing', 'billingEmail', e.target.value)}
                className="w-full h-12 px-5 rounded-[16px] bg-[#EFEBF5] shadow-clay-pressed text-[#332F3A] font-medium focus:outline-none focus:ring-2 focus:ring-[#7C3AED]/30 transition-all"
              />
            </div>
            <div className="flex items-center justify-between p-4 clay-card shadow-clay-card">
              <div>
                <p className="font-bold text-[#332F3A]" style={{ fontFamily: 'Nunito, sans-serif' }}>
                  Auto Renew
                </p>
                <p className="text-sm text-[#635F69]">Automatically renew your subscription</p>
              </div>
              <button
                onClick={() => updateSetting('billing', 'autoRenew', !settings.billing.autoRenew)}
                className={`w-14 h-8 rounded-full transition-colors ${
                  settings.billing.autoRenew ? 'bg-[#7C3AED]' : 'bg-[#E5E1EF]'
                } relative`}
              >
                <div className={`w-6 h-6 rounded-full bg-white transition-transform absolute top-1 ${
                  settings.billing.autoRenew ? 'translate-x-7' : 'translate-x-1'
                }`} />
              </button>
            </div>
          </div>
        );
      case 'security':
        return (
          <div className="space-y-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 clay-card shadow-clay-card">
                <div>
                  <p className="font-bold text-[#332F3A]" style={{ fontFamily: 'Nunito, sans-serif' }}>
                    Two-Factor Authentication
                  </p>
                  <p className="text-sm text-[#635F69]">Add an extra layer of security to your account</p>
                </div>
                <button
                  onClick={() => updateSetting('security', 'twoFactorEnabled', !settings.security.twoFactorEnabled)}
                  className={`w-14 h-8 rounded-full transition-colors ${
                    settings.security.twoFactorEnabled ? 'bg-[#7C3AED]' : 'bg-[#E5E1EF]'
                  } relative`}
                >
                  <div className={`w-6 h-6 rounded-full bg-white transition-transform absolute top-1 ${
                    settings.security.twoFactorEnabled ? 'translate-x-7' : 'translate-x-1'
                  }`} />
                </button>
              </div>
              <div className="flex items-center justify-between p-4 clay-card shadow-clay-card">
                <div>
                  <p className="font-bold text-[#332F3A]" style={{ fontFamily: 'Nunito, sans-serif' }}>
                    API Key Rotation
                  </p>
                  <p className="text-sm text-[#635F69]">Automatically rotate API keys every 90 days</p>
                </div>
                <button
                  onClick={() => updateSetting('security', 'apiKeyRotation', !settings.security.apiKeyRotation)}
                  className={`w-14 h-8 rounded-full transition-colors ${
                    settings.security.apiKeyRotation ? 'bg-[#7C3AED]' : 'bg-[#E5E1EF]'
                  } relative`}
                >
                  <div className={`w-6 h-6 rounded-full bg-white transition-transform absolute top-1 ${
                    settings.security.apiKeyRotation ? 'translate-x-7' : 'translate-x-1'
                  }`} />
                </button>
              </div>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <DashboardLayout>
      {/* Page Header */}
      <div className="mb-8">
        <h1 
          className="text-3xl sm:text-4xl font-black text-[#332F3A] mb-2"
          style={{ fontFamily: 'Nunito, sans-serif' }}
        >
          Settings
        </h1>
        <p className="text-[#635F69]">
          Manage your account settings and preferences.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex space-x-1 mb-8 bg-[#EFEBF5] p-1 rounded-[20px]">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex-1 h-12 px-4 rounded-[16px] font-medium transition-all ${
              activeTab === tab.id
                ? 'bg-white text-[#7C3AED] shadow-clay-card'
                : 'text-[#635F69] hover:text-[#332F3A]'
            }`}
            style={{ fontFamily: 'Nunito, sans-serif' }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="clay-card shadow-clay-card p-8">
        {renderTabContent()}
      </div>

      {/* Save Button */}
      <div className="mt-8">
        <button className="h-12 px-8 rounded-[20px] bg-gradient-to-br from-[#A78BFA] to-[#7C3AED] text-white font-bold shadow-clay-button hover:shadow-clay-button-hover transition-all">
          Save Changes
        </button>
      </div>
    </DashboardLayout>
  );
}