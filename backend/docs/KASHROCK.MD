Here is a clean, structured, long-form description you can drop into a .md file so Windsurf can immediately understand the full context of Kashrock and how the system is supposed to work. The tone is neutral and technical so it’s perfect for an internal doc, but the strategic framing stays sharp.

⸻

Kashrock – System Overview

Kashrock is an infrastructure-level platform designed to serve as the core backend for developers building sports betting applications, trading tools, automated models, and analytics products. Instead of functioning as a consumer-facing sportsbook, Kashrock provides the data, real-time odds pipelines, market intelligence, and modular APIs that allow builders to create entire betting ecosystems on top of it.

Kashrock’s mission is to become the backbone of the next generation of betting apps—similar to how Stripe underpins payments and Twilio underpins communications—by making high-quality odds, market signals, and data orchestration accessible to developers at scale.

⸻

Core Value Proposition
	1.	Unified Odds Infrastructure
	•	Aggregates odds from multiple global sportsbooks.
	•	Provides normalized, standardized endpoints so developers don’t need to scrape, clean, or map odds themselves.
	•	Supports both pre-game and in-play (live) markets.
	2.	Real-Time Odds Delivery
	•	Low-latency distribution suitable for trading models, algo bettors, and real-time applications.
	•	Optional WebSocket or SSE connections for streaming.
	3.	Developer-Centric Architecture
	•	Full REST API and streaming endpoints.
	•	Focus on scenario-based documentation, code examples, and ease of integration.
	•	Designed for teams building:
	•	Betting apps
	•	Model-driven trading systems
	•	Odds comparison tools
	•	Player prop engines
	•	Arbitrage/scanner services
	•	Sports data dashboards
	4.	Exportable Odds + Timestamps
	•	Based on user feedback: ability to export live odds with associated game timestamps.
	•	Enables auditing, model training, backtesting, and analytics.

⸻

System Components

1. Scraping Layer

Responsible for:
	•	Collecting odds and market data from target sportsbooks.
	•	Handling anti-bot systems, rate limits, and dynamic rendering.
	•	Normalizing inconsistent data structures across books.
	•	Mapping teams, leagues, markets, and sports using unified identifiers.

The scraping layer outputs raw data into the ingestion pipeline.

⸻

2. Ingestion and Normalization Layer

This layer:
	•	Cleans, deduplicates, and standardizes odds from multiple sources.
	•	Combines multiple books into one coherent format.
	•	Applies timestamping to every odds change event.
	•	Publishes structured events to the internal event bus.

Core tasks include:
	•	Model-friendly formatting
	•	Conflict resolution (e.g., differing lines)
	•	Market mapping and alignment
	•	Status tracking (scheduled, in-play, delayed, closed)

⸻

3. Real-Time Event Bus

The internal messaging backbone.

Purposes:
	•	Distributes odds updates to API consumers.
	•	Allows connected systems (APIs, analytics tools, usage dashboards) to stay synchronized with the live feed.
	•	Supports replay functionality for exporting or backtesting odds movements.

⸻

4. API Layer

The public interface for developers.

Endpoints
	•	Odds API
	•	Moneyline, spreads, totals, props.
	•	Pre-game + live.
	•	Example: /v1/odds/live?league=nfl
	•	Historical/Export API
	•	Downloadable odds with timestamps.
	•	Useful for data science, model training, arbitrage research.
	•	Metadata API
	•	Teams, leagues, schedules, line mappings.

API Characteristics
	•	Low latency
	•	Scalable
	•	Designed for reliability under high load
	•	Focused on developer ergonomics

⸻

5. Dashboard (Future)

A frontend layer allowing developers to:
	•	Monitor API usage
	•	Configure webhooks
	•	View latency metrics
	•	Manage API keys
	•	See odds streams visually
	•	Access logs for odds replay

⸻

6. Security and Anti-Scraping Protection

To ensure the Kashrock API itself cannot be easily scraped, multiple layers are implemented:
	•	API keys with rotating signatures
	•	Rate limiting per IP and per key
	•	Behavior-based anomaly detection
	•	Time-based request signing (HMAC)
	•	Optional JWT session tokens
	•	Response watermarking and fingerprinting

This makes Kashrock significantly harder to scrape compared to typical public-facing sportsbooks.

⸻

Product Vision

Kashrock aims to become the default choice for developers who want to build anything in the sports betting space. Instead of reinventing odds pipelines, data scrapers, and normalizers, developers can plug into Kashrock and focus on building unique experiences, trading engines, or betting apps.

The long-term vision is a fully modular ecosystem:
	•	Odds feeds
	•	Player props engine
	•	Model plug-ins
	•	Risk management utilities
	•	Automated betting tools
	•	Scalable streaming infrastructure

Kashrock evolves from just an odds provider into a full-stack developer platform for sports betting applications.
