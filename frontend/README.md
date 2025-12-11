# KashRock EV Slips Frontend

Modern, beautiful UI for the KashRock EV betting slips platform.

## Features

- 🎯 **Real-time EV Slips**: Automatically fetches and displays profitable betting opportunities
- 🎨 **Modern Design**: Beautiful dark theme with purple accents
- 🔄 **Auto-refresh**: Updates every 30 seconds
- 🎲 **Mixed Sports**: Combine props from multiple sports in one slip
- 📊 **Advanced Filtering**: Filter by sport, leg count, EV threshold
- 📱 **Responsive**: Works on desktop, tablet, and mobile

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables (create `.env.local`):
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_KEY=your_api_key_here
```

3. Run the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## Configuration

- `NEXT_PUBLIC_API_URL`: Backend API URL (default: http://localhost:8000)
- `NEXT_PUBLIC_API_KEY`: Optional API key for authentication

## Tech Stack

- **Next.js 16**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **React 19**: Latest React features
