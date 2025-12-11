import NextAuth from "next-auth";
import GoogleProvider from "next-auth/providers/google";

const handler = NextAuth({
    providers: [
        GoogleProvider({
            clientId: process.env.GOOGLE_CLIENT_ID || "",
            clientSecret: process.env.GOOGLE_CLIENT_SECRET || "",
        }),
    ],
    pages: {
        signIn: '/login',
    },
    callbacks: {
        async jwt({ token, account }) {
            if (account) {
                // Initial sign in
                const idToken = account.id_token;

                // Exchange Google ID Token for KashRock Backend Token
                try {
                    const apiUrl = process.env.NEXT_PUBLIC_PUBLIC_API_BASE || 'http://127.0.0.1:8000';
                    console.log(`Exchanging Google Token with Backend at ${apiUrl}/v1/auth/google`);

                    const res = await fetch(`${apiUrl}/v1/auth/google`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ id_token: idToken }),
                    });

                    if (res.ok) {
                        const data = await res.json();
                        token.backendAccessToken = data.access_token;
                        token.userProfile = data.user;
                        console.log("Backend auth success");
                    } else {
                        console.error("Backend auth failed", res.status, await res.text());
                    }
                } catch (e) {
                    console.error("Backend auth error", e);
                }
            }
            return token;
        },
        async session({ session, token }) {
            // @ts-ignore
            session.accessToken = token.backendAccessToken; // This is the KashRock JWT
            // @ts-ignore
            if (token.userProfile) {
                // @ts-ignore
                session.user = { ...session.user, ...token.userProfile };
            }
            return session;
        },
    },
    secret: process.env.NEXTAUTH_SECRET,
});

export { handler as GET, handler as POST };
