'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

export default function AuthCallbackPage() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const token = searchParams.get('token');
        const errorParam = searchParams.get('error');

        if (errorParam) {
            setError(decodeURIComponent(errorParam));
            setTimeout(() => {
                router.push('/login');
            }, 3000);
            return;
        }

        if (token) {
            // Store the session token
            localStorage.setItem('kashrock_dashboard_session', token);

            // Redirect to dashboard
            router.push('/dashboard');
        } else {
            setError('No authentication token received');
            setTimeout(() => {
                router.push('/login');
            }, 3000);
        }
    }, [searchParams, router]);

    return (
        <div className="min-h-screen bg-[#F4F1FA] flex items-center justify-center px-6">
            <div className="clay-card shadow-clay-card p-8 max-w-md w-full text-center">
                {error ? (
                    <>
                        <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-100 flex items-center justify-center">
                            <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </div>
                        <h2 className="text-xl font-bold text-[#332F3A] mb-2" style={{ fontFamily: 'Nunito, sans-serif' }}>
                            Authentication Failed
                        </h2>
                        <p className="text-[#635F69] mb-4">{error}</p>
                        <p className="text-sm text-[#635F69]">Redirecting to login...</p>
                    </>
                ) : (
                    <>
                        <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-[#7C3AED]/10 flex items-center justify-center">
                            <svg className="w-8 h-8 text-[#7C3AED] animate-spin" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                            </svg>
                        </div>
                        <h2 className="text-xl font-bold text-[#332F3A] mb-2" style={{ fontFamily: 'Nunito, sans-serif' }}>
                            Signing you in...
                        </h2>
                        <p className="text-[#635F69]">Please wait while we complete your authentication.</p>
                    </>
                )}
            </div>
        </div>
    );
}
