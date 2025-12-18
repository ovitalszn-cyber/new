'use client';

import { useState } from 'react';

// Sample data
const SOCIAL_PROOF = {
  projection: {
    "source": "kashrock",
    "sport": "cs2",
    "projections": [
      {
        "projection_id": "proj_233510",
        "player_name": "Mol011",
        "player_image": "https://static.prizepicks.com/images/manual/Gzjuzu9.png",
        "stat_type": "CS2_MAPS_1-2_KILLS",
        "line": 26.5,
        "result": null,
        "odds": 100,
        "direction": "over",
        "sport": "esports_cs2",
        "team": "AaB Elite",
        "team_logo": "https://api.theesportslab.com/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBbVdCIiwiZXhwIjpudWxsLCJwdXIiOiJibG9iX2lkIn19--3a4b8c8f5b9a4d8e8c8f5b9a4d8e8c8f5b9a4d8e/5152.webp",
        "opponent": "AMKAL",
        "opponent_logo": "https://api.theesportslab.com/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBbVdCIiwiZXhwIjpudWxsLCJwdXIiOiJibG9iX2lkIn19--3a4b8c8f5b9a4d8e8c8f5b9a4d8e8c8f5b9a4d8e/AMKAL.webp",
        "event_time": "2025-11-30T09:00:00Z",
        "status": "pre_game",
        "links": {
          "bet": "https://app.prizepicks.com/board?league_id=265&stat_type_name=MAPS 1-2 Kills&projection_id=8204498"
        },
        "metadata": {
          "match_id": 143689,
          "team_id": 5152,
          "opponent_id": 8918,
          "player_id": 13255
        },
        "rich_data": {
          "id": 233510,
          "stat_type": "MAPS 1-2 Kills",
          "line_score": "26.5",
          "player": {
            "id": 13255,
            "nickname": "Mol011",
            "country": "Denmark",
            "stats": {
              "dpm": 14.1,
              "kpm": 14.6,
              "headshots": 69.0
            }
          },
          "team": {
            "id": 5152,
            "name": "AaB Elite"
          },
          "opposing_team": {
            "id": 8918,
            "name": "AMKAL"
          }
        }
      }
    ],
    "generated_at": "2025-12-18T16:07:50.397296+00:00"
  },
  fixture: {
    "source": "kashrock",
    "sport": "cs2",
    "fixtures": [
      {
        "fixture_id": "fix_144592",
        "sport": "esports_cs2",
        "status": "upcoming",
        "raw_status": "scheduled",
        "event_time": "2025-11-30T10:00:00Z",
        "competition": "DraculaN #4: Open Qualifier",
        "team1": "Mousquetaires",
        "team1_logo": "https://api.theesportslab.com/rails/active_storage/blobs/redirect/.../mousquetaires.webp",
        "team2": "Young Ninjas",
        "team2_logo": "https://api.theesportslab.com/rails/active_storage/blobs/redirect/.../young-ninjas.webp",
        "score1": 0,
        "score2": 0,
        "metadata": {
          "format": "bestOf3",
          "maps": ["Inferno", "Mirage", "Nuke"]
        },
        "rich_data": {
          "links": [
            {
              "rel": "stream",
              "link": "https://twitch.tv/esl_csgo"
            }
          ]
        }
      }
    ]
  },
  rankings: {
    "source": "kashrock",
    "sport": "cs2",
    "rankings": [
      {
        "player_id": 17169,
        "player_name": "donk",
        "player_image": "https://static.prizepicks.com/images/manual/teamSpirit_jersey.png",
        "team": "Spirit",
        "team_logo": "https://api.theesportslab.com/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBbVdCIiwiZXhwIjpudWxsLCJwdXIiOiJibG9iX2lkIn19--3a4b8c8f5b9a4d8e8c8f5b9a4d8e8c8f5b9a4d8e/959.webp",
        "country": "Russia",
        "rank_stats": {
          "kills": 29815,
          "deaths": 29286,
          "kpm": 18.96,
          "dpm": 19.46,
          "headshots": 21149
        },
        "metadata": {
          "age": 17,
          "country_iso": "RU"
        }
      },
      {
        "player_id": 22747,
        "player_name": "TaZ",
        "player_image": "https://static.prizepicks.com/images/manual/A6xQS5I.png",
        "team": "G2 Esports",
        "team_logo": "https://api.theesportslab.com/rails/active_storage/blobs/redirect/.../g2.webp",
        "country": "Poland",
        "rank_stats": {
          "kills": 1384,
          "kpm": 15.41,
          "dpm": 18.92,
          "headshots": 23922
        }
      }
    ]
  },
  player: {
    "source": "kashrock",
    "player": {
      "id": 17169,
      "first_name": "Danil",
      "last_name": "Kryshkovets",
      "nickname": "donk",
      "age": 17,
      "country": "Russia",
      "countryiso": "RU",
      "team": {
        "id": 959,
        "name": "Spirit",
        "logo": "https://api.theesportslab.com/rails/active_storage/blobs/redirect/.../959.webp"
      },
      "stats": {
        "dpm": 19.46,
        "kpm": 18.96,
        "adm": 4.96,
        "hspm": 10.15,
        "kills": 29815,
        "deaths": 29286,
        "headshots": 21149
      },
      "images": {
        "profile": "https://static.prizepicks.com/images/manual/teamSpirit_jersey.png",
        "flag": "https://flagsapi.com/RU/flat/64.png"
      }
    }
  }
};

// Sanitize helper to redact URLs and sensitive fields
function sanitizeForPreview(obj: any): any {
  if (obj === null || obj === undefined) return obj;
  
  if (typeof obj === 'string') {
    if (obj.includes('http')) return '[redacted]';
    return obj;
  }
  
  if (Array.isArray(obj)) {
    return obj.map(sanitizeForPreview);
  }
  
  if (typeof obj === 'object') {
    const sanitized: any = {};
    for (const [key, value] of Object.entries(obj)) {
      if (key === 'links' || key.endsWith('_logo') || key.endsWith('_image')) {
        sanitized[key] = '[redacted]';
      } else {
        sanitized[key] = sanitizeForPreview(value);
      }
    }
    return sanitized;
  }
  
  return obj;
}

// Tab component
function Tab({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-2 text-sm font-medium rounded-sm transition-colors ${
        active
          ? 'bg-white text-black'
          : 'text-zinc-400 hover:text-white hover:bg-white/5'
      }`}
    >
      {children}
    </button>
  );
}

// Projection card
function ProjectionCard({ data }: { data: any }) {
  const projection = data.projections[0];
  return (
    <div className="bg-[#0C0D0F] border border-white/10 rounded-sm p-6">
      <div className="flex items-start gap-4 mb-4">
        <img src={projection.player_image} alt={projection.player_name} className="w-12 h-12 rounded-full object-cover" />
        <div className="flex-1">
          <h4 className="text-white font-medium">{projection.player_name}</h4>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-zinc-400 text-sm">{projection.team}</span>
            <span className="text-zinc-500 text-sm">vs</span>
            <span className="text-zinc-400 text-sm">{projection.opponent}</span>
          </div>
        </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <span className="text-zinc-500 text-xs uppercase tracking-wider">Market</span>
          <p className="text-white font-medium">{projection.stat_type.replace(/_/g, ' ')}</p>
        </div>
        <div>
          <span className="text-zinc-500 text-xs uppercase tracking-wider">Line</span>
          <p className="text-white font-medium">{projection.line} {projection.direction}</p>
        </div>
      </div>
      
      <div className="flex items-center gap-4 mb-4">
        <div>
          <span className="text-zinc-500 text-xs uppercase tracking-wider">Status</span>
          <p className="text-zinc-300 text-sm">{projection.status}</p>
        </div>
        <div>
          <span className="text-zinc-500 text-xs uppercase tracking-wider">Event Time</span>
          <p className="text-zinc-300 text-sm">{new Date(projection.event_time).toLocaleDateString()}</p>
        </div>
      </div>
      
      <div className="bg-black/30 rounded-sm p-3">
        <p className="text-xs text-zinc-500 mb-2">JSON Preview</p>
        <pre className="text-xs text-zinc-400 font-mono overflow-x-auto">
          {JSON.stringify(sanitizeForPreview(projection), null, 2).slice(0, 500)}...
        </pre>
      </div>
    </div>
  );
}

// Fixture card
function FixtureCard({ data }: { data: any }) {
  const fixture = data.fixtures[0];
  return (
    <div className="bg-[#0C0D0F] border border-white/10 rounded-sm p-6">
      <div className="mb-4">
        <h4 className="text-white font-medium mb-2">{fixture.competition}</h4>
        <div className="flex items-center gap-4">
          <span className="text-zinc-300">{fixture.team1}</span>
          <span className="text-zinc-500">vs</span>
          <span className="text-zinc-300">{fixture.team2}</span>
        </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <span className="text-zinc-500 text-xs uppercase tracking-wider">Format</span>
          <p className="text-white font-medium">{fixture.metadata.format}</p>
        </div>
        <div>
          <span className="text-zinc-500 text-xs uppercase tracking-wider">Maps</span>
          <p className="text-white font-medium">{fixture.metadata.maps.join(', ')}</p>
        </div>
      </div>
      
      <div className="flex items-center gap-4 mb-4">
        <div>
          <span className="text-zinc-500 text-xs uppercase tracking-wider">Status</span>
          <p className="text-zinc-300 text-sm">{fixture.status}</p>
        </div>
        <div>
          <span className="text-zinc-500 text-xs uppercase tracking-wider">Event Time</span>
          <p className="text-zinc-300 text-sm">{new Date(fixture.event_time).toLocaleDateString()}</p>
        </div>
      </div>
      
      <div className="bg-black/30 rounded-sm p-3">
        <p className="text-xs text-zinc-500 mb-2">JSON Preview</p>
        <pre className="text-xs text-zinc-400 font-mono overflow-x-auto">
          {JSON.stringify(sanitizeForPreview(fixture), null, 2).slice(0, 500)}...
        </pre>
      </div>
    </div>
  );
}

// Rankings card
function RankingsCard({ data }: { data: any }) {
  return (
    <div className="bg-[#0C0D0F] border border-white/10 rounded-sm p-6">
      <div className="space-y-4">
        {data.rankings.slice(0, 2).map((player: any, index: number) => (
          <div key={player.player_id} className="flex items-start gap-4">
            <img src={player.player_image} alt={player.player_name} className="w-12 h-12 rounded-full object-cover" />
            <div className="flex-1">
              <h4 className="text-white font-medium">{player.player_name}</h4>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-zinc-400 text-sm">{player.team}</span>
                <span className="text-zinc-500 text-sm">• {player.country}</span>
              </div>
              <div className="grid grid-cols-3 gap-2 mt-2">
                <div>
                  <span className="text-zinc-500 text-xs">KPM</span>
                  <p className="text-white text-sm">{player.rank_stats.kpm}</p>
                </div>
                <div>
                  <span className="text-zinc-500 text-xs">DPM</span>
                  <p className="text-white text-sm">{player.rank_stats.dpm}</p>
                </div>
                <div>
                  <span className="text-zinc-500 text-xs">Headshots</span>
                  <p className="text-white text-sm">{player.rank_stats.headshots || 'N/A'}</p>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      <div className="bg-black/30 rounded-sm p-3 mt-4">
        <p className="text-xs text-zinc-500 mb-2">JSON Preview</p>
        <pre className="text-xs text-zinc-400 font-mono overflow-x-auto">
          {JSON.stringify(sanitizeForPreview(data.rankings.slice(0, 2)), null, 2).slice(0, 500)}...
        </pre>
      </div>
    </div>
  );
}

// Player profile card
function PlayerCard({ data }: { data: any }) {
  const player = data.player;
  return (
    <div className="bg-[#0C0D0F] border border-white/10 rounded-sm p-6">
      <div className="flex items-start gap-4 mb-4">
        <img src={player.images.profile} alt={player.nickname} className="w-16 h-16 rounded-full object-cover" />
        <div className="flex-1">
          <h4 className="text-white font-medium text-lg">{player.nickname}</h4>
          <p className="text-zinc-400">{player.first_name} {player.last_name}</p>
          <div className="flex items-center gap-2 mt-1">
            <img src={player.images.flag} alt={player.country} className="w-4 h-4" />
            <span className="text-zinc-400 text-sm">{player.country} • Age {player.age}</span>
          </div>
          <div className="flex items-center gap-2 mt-2">
            <span className="text-zinc-300 text-sm">{player.team.name}</span>
          </div>
        </div>
      </div>
      
      <div className="grid grid-cols-3 gap-4 mb-4">
        <div>
          <span className="text-zinc-500 text-xs uppercase tracking-wider">KPM</span>
          <p className="text-white font-medium">{player.stats.kpm}</p>
        </div>
        <div>
          <span className="text-zinc-500 text-xs uppercase tracking-wider">DPM</span>
          <p className="text-white font-medium">{player.stats.dpm}</p>
        </div>
        <div>
          <span className="text-zinc-500 text-xs uppercase tracking-wider">Kills</span>
          <p className="text-white font-medium">{player.stats.kills.toLocaleString()}</p>
        </div>
        <div>
          <span className="text-zinc-500 text-xs uppercase tracking-wider">Deaths</span>
          <p className="text-white font-medium">{player.stats.deaths.toLocaleString()}</p>
        </div>
        <div>
          <span className="text-zinc-500 text-xs uppercase tracking-wider">Headshots</span>
          <p className="text-white font-medium">{player.stats.headshots.toLocaleString()}</p>
        </div>
        <div>
          <span className="text-zinc-500 text-xs uppercase tracking-wider">HSPM</span>
          <p className="text-white font-medium">{player.stats.hspm}</p>
        </div>
      </div>
      
      <div className="bg-black/30 rounded-sm p-3">
        <p className="text-xs text-zinc-500 mb-2">JSON Preview</p>
        <pre className="text-xs text-zinc-400 font-mono overflow-x-auto">
          {JSON.stringify(sanitizeForPreview(player), null, 2).slice(0, 500)}...
        </pre>
      </div>
    </div>
  );
}

export default function EsportsSocialProof() {
  const [activeTab, setActiveTab] = useState<'projection' | 'fixture' | 'rankings' | 'player'>('projection');
  
  const tabs = [
    { id: 'projection' as const, label: 'Projection' },
    { id: 'fixture' as const, label: 'Fixture' },
    { id: 'rankings' as const, label: 'Rankings' },
    { id: 'player' as const, label: 'Player Profile' },
  ];
  
  return (
    <section className="py-24 max-w-7xl mx-auto px-6">
      <div className="text-center mb-16">
        <h2 className="text-3xl md:text-4xl font-medium tracking-tight text-white mb-4">
          Real esports objects — normalized, ready to ship
        </h2>
        <p className="text-lg text-zinc-500">
          Examples from KashRock Esports responses. External links redacted.
        </p>
      </div>
      
      <div className="flex justify-center mb-8">
        <div className="bg-[#0C0D0F] border border-white/10 rounded-sm p-1 inline-flex">
          {tabs.map((tab) => (
            <Tab
              key={tab.id}
              active={activeTab === tab.id}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </Tab>
          ))}
        </div>
      </div>
      
      <div className="max-w-4xl mx-auto">
        {activeTab === 'projection' && <ProjectionCard data={SOCIAL_PROOF.projection} />}
        {activeTab === 'fixture' && <FixtureCard data={SOCIAL_PROOF.fixture} />}
        {activeTab === 'rankings' && <RankingsCard data={SOCIAL_PROOF.rankings} />}
        {activeTab === 'player' && <PlayerCard data={SOCIAL_PROOF.player} />}
      </div>
    </section>
  );
}
