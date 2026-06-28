import { useState, useEffect } from 'react';
import { Cpu, Activity, Clock, Target, ShieldCheck, AlertTriangle } from 'lucide-react';

type EventType = 'EvidenceReceived' | 'SpecialistCompleted' | 'ConsensusUpdated' | 'DownstreamSystemsUpdated';

interface SynapseEvent {
  timestamp_ms: number;
  evidence_cycle: number;
  event_type: EventType;
  payload?: any;
  specialist?: string;
  confidence?: number;
  findings?: string;
  decision?: string;
  human_review_required?: boolean;
  systems?: { system: string; status: string }[];
}

export default function App() {
  const [events, setEvents] = useState<SynapseEvent[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  
  // State
  const [cycle, setCycle] = useState(0);
  const [evidence, setEvidence] = useState<any[]>([]);
  const [specialists, setSpecialists] = useState<Record<string, { findings: string, conf: number, active: boolean }>>({});
  const [consensus, setConsensus] = useState<any>(null);
  const [downstream, setDownstream] = useState<any[]>([]);
  const [history, setHistory] = useState<any[]>([]);

  useEffect(() => {
    fetch('/events.json')
      .then(res => res.json())
      .then(data => setEvents(data))
      .catch(err => console.error("Failed to load events", err));
  }, []);

  useEffect(() => {
    if (!isPlaying || currentIndex >= events.length) return;
    
    // We space events out evenly for the demo since the backend timestamps are 10ms apart
    const timer = setTimeout(() => {
      processEvent(events[currentIndex]);
      setCurrentIndex(prev => prev + 1);
    }, 400); // 400ms per event for readability

    return () => clearTimeout(timer);
  }, [isPlaying, currentIndex, events]);

  const processEvent = (ev: SynapseEvent) => {
    setCycle(ev.evidence_cycle);
    
    if (ev.event_type === 'EvidenceReceived') {
      setEvidence(ev.payload);
      // Reset specialists for new cycle
      setSpecialists({});
      setConsensus(null);
    } 
    else if (ev.event_type === 'SpecialistCompleted') {
      setSpecialists(prev => ({
        ...prev,
        [ev.specialist!]: { findings: ev.findings!, conf: ev.confidence!, active: true }
      }));
    }
    else if (ev.event_type === 'ConsensusUpdated') {
      const cons = { decision: ev.decision, conf: ev.confidence, hr: ev.human_review_required };
      setConsensus(cons);
      setHistory(prev => {
        const filtered = prev.filter(h => h.cycle !== ev.evidence_cycle);
        return [...filtered, { cycle: ev.evidence_cycle, ...cons }];
      });
    }
    else if (ev.event_type === 'DownstreamSystemsUpdated') {
      setDownstream(ev.systems || []);
    }
  };

  const restart = () => {
    setCurrentIndex(0);
    setCycle(0);
    setEvidence([]);
    setSpecialists({});
    setConsensus(null);
    setDownstream([]);
    setHistory([]);
    setIsPlaying(true);
  };

  const getConfColor = (conf: number) => {
    if (conf >= 0.8) return 'text-success';
    if (conf >= 0.5) return 'text-warning';
    return 'text-danger';
  };

  const specialistList = [
    "Vision Specialist", 
    "Source Specialist", 
    "Timeline Specialist", 
    "Contradiction Specialist", 
    "Prediction Specialist", 
    "Consensus Specialist"
  ];

  return (
    <div className="h-screen w-screen bg-background text-gray-200 flex flex-col font-sans overflow-hidden p-4 gap-4">
      
      {/* HEADER */}
      <header className="flex justify-between items-center synapse-panel shrink-0 bg-surfaceHighlight border-gray-700">
        <div className="flex items-center gap-3">
          <Activity className="text-primary" size={24} />
          <h1 className="text-xl font-bold tracking-widest uppercase">Synapse OS</h1>
        </div>
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <span className="text-gray-500 uppercase text-xs font-bold">Profile</span>
            <span className="text-sm font-mono text-primary">SUPPLY_CHAIN_FLASH_CRISIS</span>
          </div>
          <div className="flex items-center gap-2 border-l border-gray-700 pl-6">
            <span className="text-gray-500 uppercase text-xs font-bold">Status</span>
            <span className="text-sm font-mono text-success animate-pulse">ACTIVE ARBITRATION</span>
          </div>
          <button 
            onClick={restart}
            className="ml-4 bg-gray-800 hover:bg-gray-700 text-xs px-4 py-1.5 rounded text-white font-semibold transition-colors"
          >
            {isPlaying ? 'RESTART' : 'START REPLAY'}
          </button>
        </div>
      </header>

      <div className="flex flex-1 gap-4 overflow-hidden">
        
        {/* LEFT: EVIDENCE */}
        <div className="w-1/4 flex flex-col gap-4">
          <div className="synapse-panel flex-1 flex flex-col">
            <h2 className="synapse-title flex items-center gap-2"><Clock size={14}/> Evidence Feed</h2>
            <div className="mb-4">
              <span className="text-gray-500 text-xs">CYCLE: </span>
              <span className="text-2xl font-mono text-white ml-2">{cycle || '-'}</span>
            </div>
            <div className="flex-1 overflow-y-auto pr-2 space-y-3">
              {evidence.map((ev: any, i) => (
                <div key={i} className="bg-gray-900 border border-gray-800 p-3 rounded text-sm">
                  <div className="text-xs text-primary font-bold mb-1 uppercase">{ev.source}</div>
                  <div className="text-gray-300 leading-relaxed font-mono text-xs">{ev.content}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* CENTER: SPECIALIST NETWORK */}
        <div className="w-2/4 flex flex-col gap-4">
          <div className="synapse-panel flex-1">
            <h2 className="synapse-title flex items-center gap-2"><Cpu size={14}/> Specialist Network</h2>
            <div className="grid grid-cols-2 gap-4 mt-4">
              {specialistList.map(spec => {
                const data = specialists[spec];
                const isActive = !!data;
                return (
                  <div key={spec} className={`border rounded p-3 transition-colors duration-300 ${isActive ? 'bg-gray-800 border-primary' : 'bg-transparent border-gray-800'}`}>
                    <div className="flex justify-between items-center mb-2">
                      <h3 className={`text-xs font-bold uppercase ${isActive ? 'text-white' : 'text-gray-600'}`}>{spec}</h3>
                      {isActive && <Target size={14} className="text-primary" />}
                    </div>
                    {isActive ? (
                      <div>
                        <p className="text-xs text-gray-400 font-mono line-clamp-3 mb-2">{data.findings}</p>
                        <div className="flex items-center gap-2">
                          <span className="text-[10px] text-gray-500 uppercase">Confidence</span>
                          <span className={`font-mono text-xs font-bold ${getConfColor(data.conf)}`}>
                            {(data.conf * 100).toFixed(0)}%
                          </span>
                        </div>
                      </div>
                    ) : (
                      <p className="text-xs text-gray-700 italic">Waiting for evidence delta...</p>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* RIGHT: CONSENSUS */}
        <div className="w-1/4 flex flex-col gap-4">
          <div className="synapse-panel h-1/2 flex flex-col">
            <h2 className="synapse-title flex items-center gap-2"><ShieldCheck size={14}/> Arbitration Consensus</h2>
            {consensus ? (
              <div className="flex-1 flex flex-col justify-center items-center text-center p-2">
                <div className={`text-3xl font-bold uppercase mb-2 ${getConfColor(consensus.conf)}`}>
                  {(consensus.conf * 100).toFixed(0)}%
                </div>
                <div className="text-gray-500 text-xs uppercase tracking-widest mb-4">Global Confidence</div>
                <div className="text-sm text-white font-mono bg-gray-900 border border-gray-800 p-3 rounded w-full">
                  {consensus.decision}
                </div>
                {consensus.hr && (
                  <div className="mt-4 flex items-center gap-2 text-warning text-xs font-bold bg-warning/10 px-3 py-1.5 rounded">
                    <AlertTriangle size={14}/> HUMAN REVIEW REQUIRED
                  </div>
                )}
              </div>
            ) : (
              <div className="flex-1 flex items-center justify-center text-gray-700 text-sm italic">
                Calculating...
              </div>
            )}
          </div>

          <div className="synapse-panel h-1/2 flex flex-col">
            <h2 className="synapse-title">Decision History</h2>
            <div className="flex-1 overflow-y-auto space-y-2">
              {history.map((h, i) => (
                <div key={i} className="flex justify-between items-center text-xs bg-gray-900 p-2 rounded">
                  <span className="text-gray-500">CYC_{h.cycle}</span>
                  <span className="text-gray-300 truncate max-w-[120px] px-2">{h.decision}</span>
                  <span className={`font-bold ${getConfColor(h.conf)}`}>{(h.conf*100).toFixed(0)}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* BOTTOM: DOWNSTREAM SYSTEMS */}
      <div className="shrink-0 h-32 synapse-panel flex flex-col">
        <h2 className="synapse-title">Downstream Enterprise Systems</h2>
        <div className="flex flex-1 gap-4">
          {downstream.length > 0 ? (
            downstream.map((sys, i) => {
              const isPanic = sys.status.includes('PANIC') || sys.status.includes('SURGE') || sys.status.includes('DELAY') || sys.status.includes('REROUTING');
              const isNominal = sys.status.includes('NOMINAL');
              const color = isPanic ? 'text-danger' : isNominal ? 'text-success' : 'text-warning';
              const border = isPanic ? 'border-danger/30 bg-danger/5' : isNominal ? 'border-success/30 bg-success/5' : 'border-warning/30 bg-warning/5';
              
              return (
                <div key={i} className={`flex-1 border rounded p-3 flex flex-col justify-center ${border} transition-colors duration-500`}>
                  <div className="text-gray-400 text-xs font-bold uppercase tracking-wider mb-1">{sys.system}</div>
                  <div className={`font-mono text-xs font-bold ${color}`}>{sys.status}</div>
                </div>
              );
            })
          ) : (
            <div className="flex-1 flex items-center justify-center text-gray-600 text-sm">
              Waiting for consensus baseline...
            </div>
          )}
        </div>
      </div>

    </div>
  );
}
