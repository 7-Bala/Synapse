import { useState, useEffect } from 'react';
import { Cpu, Activity, Clock, ShieldCheck, AlertTriangle, FileText, Camera, Radio, Server, Anchor } from 'lucide-react';

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

const TOTAL_CYCLES = 5;

function generateMockLatency() {
  return Math.floor(Math.random() * 150) + 120; // 120-270ms
}

function getEvidenceIcon(source: string) {
  const s = source.toLowerCase();
  if (s.includes('social')) return <Radio size={16} />;
  if (s.includes('drone') || s.includes('satellite') || s.includes('image')) return <Camera size={16} />;
  if (s.includes('telemetry') || s.includes('ais')) return <Anchor size={16} />;
  if (s.includes('api')) return <Server size={16} />;
  return <FileText size={16} />;
}

function getEvidenceCredibility(source: string) {
  const s = source.toLowerCase();
  if (s.includes('social')) return 0.18;
  if (s.includes('drone')) return 0.82;
  if (s.includes('satellite')) return 0.94;
  if (s.includes('authority')) return 0.97;
  if (s.includes('telemetry')) return 0.88;
  if (s.includes('procurement')) return 0.99;
  return 0.75;
}

export default function App() {
  const [events, setEvents] = useState<SynapseEvent[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  
  // State
  const [cycle, setCycle] = useState(0);
  const [arbitrationStatus, setArbitrationStatus] = useState("AWAITING START");
  const [evidenceList, setEvidenceList] = useState<any[]>([]);
  const [specialists, setSpecialists] = useState<Record<string, { findings: string, conf: number, status: 'Thinking...' | 'COMPLETE' | 'UNCERTAIN', latency: number }>>({});
  const [consensus, setConsensus] = useState<any>(null);
  const [prevConsensusConf, setPrevConsensusConf] = useState<number>(0);
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
    
    // Smooth 600ms pacing for drama
    const timer = setTimeout(() => {
      processEvent(events[currentIndex]);
      setCurrentIndex(prev => prev + 1);
    }, 600);

    return () => clearTimeout(timer);
  }, [isPlaying, currentIndex, events]);

  const processEvent = (ev: SynapseEvent) => {
    setCycle(ev.evidence_cycle);
    
    if (ev.event_type === 'EvidenceReceived') {
      setArbitrationStatus("RECEIVING EVIDENCE");
      
      const enrichedPayload = ev.payload.map((e: any) => ({
        ...e,
        credibility: getEvidenceCredibility(e.source),
        timestamp: new Date().toLocaleTimeString([], { hour12: false })
      }));
      
      setEvidenceList(prev => [...enrichedPayload, ...prev]);
      
      // Reset specialists to thinking state for active network visualization
      const specList = ["Vision Specialist", "Source Specialist", "Timeline Specialist", "Contradiction Specialist", "Prediction Specialist", "Consensus Specialist"];
      const newSpecs: any = {};
      specList.forEach(s => {
        newSpecs[s] = { findings: "Analyzing evidence delta...", conf: 0, status: 'Thinking...', latency: 0 };
      });
      setSpecialists(newSpecs);
      
    } 
    else if (ev.event_type === 'SpecialistCompleted') {
      setArbitrationStatus("SPECIALISTS ACTIVE");
      setSpecialists(prev => ({
        ...prev,
        [ev.specialist!]: { 
          findings: ev.findings!, 
          conf: ev.confidence!, 
          status: ev.confidence! < 0.5 ? 'UNCERTAIN' : 'COMPLETE', 
          latency: generateMockLatency() 
        }
      }));
    }
    else if (ev.event_type === 'ConsensusUpdated') {
      setArbitrationStatus("CONSENSUS UPDATING");
      
      if (consensus) {
        setPrevConsensusConf(consensus.conf);
      }
      
      const cons = { 
        decision: ev.decision, 
        conf: ev.confidence, 
        hr: ev.human_review_required,
        reasoning: "Reasoning synthesized from specialist network."
      };
      setConsensus(cons);
      setHistory(prev => {
        const filtered = prev.filter(h => h.cycle !== ev.evidence_cycle);
        return [...filtered, { cycle: ev.evidence_cycle, ...cons, timestamp: new Date().toLocaleTimeString([], { hour12: false }) }];
      });
    }
    else if (ev.event_type === 'DownstreamSystemsUpdated') {
      setArbitrationStatus(cycle === TOTAL_CYCLES ? "ENTERPRISE STABILIZED" : "DOWNSTREAM REACTION");
      setDownstream(ev.systems || []);
    }
  };

  const restart = () => {
    setCurrentIndex(0);
    setCycle(0);
    setEvidenceList([]);
    setSpecialists({});
    setConsensus(null);
    setPrevConsensusConf(0);
    setDownstream([]);
    setHistory([]);
    setArbitrationStatus("AWAITING START");
    setIsPlaying(true);
  };

  const getConfColor = (conf: number) => {
    if (conf >= 0.8) return 'text-success';
    if (conf >= 0.5) return 'text-warning';
    return 'text-danger';
  };
  
  const getDownstreamSubtext = (sys: string, status: string) => {
    if (status.includes('NOMINAL')) return "Nominal operations";
    if (sys === 'Fuel Procurement') return "+$3.2M Market Exposure";
    if (sys === 'Route Optimizer') return "12 Ships Rerouted";
    if (sys === 'Insurance Pricing') return "Risk Premium Escalated";
    if (sys === 'Scheduling Engine') return "Slot Cascade Warning";
    return "Action Pending";
  };

  const specialistList = [
    "Vision Specialist", 
    "Source Specialist", 
    "Timeline Specialist", 
    "Contradiction Specialist", 
    "Prediction Specialist", 
    "Consensus Specialist"
  ];

  // SVG Graph generation
  const graphPoints = history.map((h, i) => {
    const x = (i / (TOTAL_CYCLES - 1 || 1)) * 100;
    const y = 100 - (h.conf * 100);
    return `${x},${y}`;
  }).join(' ');

  return (
    <div className="h-screen w-screen bg-background text-gray-200 flex flex-col font-sans overflow-hidden p-4 gap-4">
      
      {/* HEADER */}
      <header className="flex justify-between items-center synapse-panel shrink-0 bg-surfaceHighlight border-gray-700">
        <div className="flex items-center gap-3">
          <Activity className="text-primary" size={24} />
          <h1 className="text-xl font-bold tracking-widest uppercase text-white">Synapse OS</h1>
        </div>
        <div className="flex items-center gap-8">
          <div className="flex flex-col">
            <span className="text-gray-500 uppercase text-[10px] font-bold tracking-widest">Simulation Profile</span>
            <span className="text-sm font-mono text-gray-200">SUPPLY_CHAIN_FLASH_CRISIS</span>
          </div>
          <div className="flex flex-col border-l border-gray-700 pl-6">
            <span className="text-gray-500 uppercase text-[10px] font-bold tracking-widest">Evidence Cycle</span>
            <span className="text-sm font-mono text-white">{cycle} / {TOTAL_CYCLES}</span>
          </div>
          <div className="flex flex-col border-l border-gray-700 pl-6 w-48">
            <span className="text-gray-500 uppercase text-[10px] font-bold tracking-widest">Status</span>
            <span className={`text-sm font-mono ${arbitrationStatus.includes('STABILIZED') ? 'text-success' : 'text-primary animate-pulse'}`}>
              {arbitrationStatus}
            </span>
          </div>
          <button 
            onClick={restart}
            className="ml-4 bg-gray-800 hover:bg-gray-700 text-xs px-6 py-2 rounded text-white font-semibold transition-colors border border-gray-600"
          >
            {isPlaying && currentIndex < events.length ? 'RESTARTING...' : 'START REPLAY'}
          </button>
        </div>
      </header>

      <div className="flex flex-1 gap-4 overflow-hidden h-0">
        
        {/* LEFT: EVIDENCE */}
        <div className="w-1/4 flex flex-col gap-4">
          <div className="synapse-panel flex-1 flex flex-col overflow-hidden">
            <h2 className="synapse-title flex items-center gap-2"><Clock size={14}/> Incoming Evidence</h2>
            
            <div className="flex-1 overflow-y-auto pr-2 space-y-3">
              {evidenceList.map((ev: any, i) => (
                <div key={i} className={`bg-gray-900/50 border border-gray-800 p-3 rounded text-sm transition-all duration-500 ${i === 0 ? 'border-l-4 border-l-primary bg-gray-800' : ''}`}>
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-gray-400">{getEvidenceIcon(ev.source)}</span>
                      <span className="text-xs text-primary font-bold uppercase">{ev.source}</span>
                    </div>
                    <span className="text-[10px] text-gray-500 font-mono">{ev.timestamp}</span>
                  </div>
                  <div className="text-gray-300 leading-relaxed font-mono text-xs mb-2">{ev.content}</div>
                  <div className="flex justify-between items-center pt-2 border-t border-gray-800">
                    <span className="text-[10px] text-gray-500 uppercase">Credibility</span>
                    <span className={`font-mono text-[10px] ${ev.credibility > 0.8 ? 'text-success' : 'text-danger'}`}>
                      {ev.credibility.toFixed(2)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* CENTER: SPECIALIST NETWORK */}
        <div className="w-2/4 flex flex-col gap-4">
          <div className="synapse-panel flex-1 flex flex-col">
            <h2 className="synapse-title flex items-center gap-2"><Cpu size={14}/> Specialist Execution Network</h2>
            <div className="grid grid-cols-2 gap-4 mt-2 overflow-y-auto">
              {specialistList.map(spec => {
                const data = specialists[spec];
                if (!data) return (
                  <div key={spec} className="border border-gray-800/50 rounded p-3 bg-transparent opacity-50">
                    <h3 className="text-xs font-bold uppercase text-gray-600">{spec}</h3>
                    <p className="text-[10px] text-gray-700 italic mt-2">Awaiting data...</p>
                  </div>
                );

                const isThinking = data.status === 'Thinking...';
                const isUncertain = data.status === 'UNCERTAIN';
                
                let borderColor = 'border-gray-700';
                if (isThinking) borderColor = 'border-primary shadow-[0_0_10px_rgba(59,130,246,0.2)] animate-pulse';
                else if (isUncertain) borderColor = 'border-danger';
                else borderColor = 'border-success';

                return (
                  <div key={spec} className={`border rounded p-3 bg-gray-900/30 transition-all duration-300 ${borderColor}`}>
                    <div className="flex justify-between items-center mb-2 border-b border-gray-800 pb-2">
                      <h3 className="text-xs font-bold uppercase text-gray-200">{spec}</h3>
                      <span className={`text-[9px] font-mono px-2 py-0.5 rounded ${isThinking ? 'bg-primary/20 text-primary' : isUncertain ? 'bg-danger/20 text-danger' : 'bg-success/20 text-success'}`}>
                        {data.status}
                      </span>
                    </div>
                    
                    <p className={`text-xs font-mono line-clamp-2 mb-3 h-8 ${isThinking ? 'text-gray-500' : 'text-gray-300'}`}>
                      {data.findings}
                    </p>
                    
                    <div className="flex justify-between items-center text-[10px] uppercase font-bold text-gray-500">
                      <div>
                        Conf <span className={`font-mono ml-1 ${getConfColor(data.conf)}`}>{(data.conf * 100).toFixed(0)}%</span>
                      </div>
                      <div className="font-mono text-gray-400">
                        {data.latency > 0 ? `${data.latency}ms` : '---'}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* RIGHT: CONSENSUS */}
        <div className="w-1/4 flex flex-col gap-4">
          <div className="synapse-panel flex-[1.5] flex flex-col">
            <h2 className="synapse-title flex items-center gap-2"><ShieldCheck size={14}/> Arbitration Decision</h2>
            {consensus ? (
              <div className="flex flex-col h-full justify-between">
                <div>
                  <div className="text-gray-500 text-[10px] uppercase tracking-widest mb-1">Current Recommendation</div>
                  <div className="text-sm text-white font-mono bg-gray-800 border border-gray-700 p-3 rounded w-full shadow-lg">
                    {consensus.decision}
                  </div>
                </div>
                
                <div className="flex items-end justify-between mt-4">
                  <div>
                    <div className="text-gray-500 text-[10px] uppercase tracking-widest mb-1">Confidence</div>
                    <div className={`text-4xl font-bold font-mono ${getConfColor(consensus.conf)} transition-all duration-1000`}>
                      {(consensus.conf * 100).toFixed(0)}%
                    </div>
                  </div>
                  {prevConsensusConf > 0 && (
                    <div className={`text-xs font-bold font-mono mb-1 ${consensus.conf >= prevConsensusConf ? 'text-success' : 'text-danger'}`}>
                      {consensus.conf >= prevConsensusConf ? '▲' : '▼'} {Math.abs((consensus.conf - prevConsensusConf) * 100).toFixed(0)}%
                    </div>
                  )}
                </div>

                <div className="mt-4">
                  <div className="text-gray-500 text-[10px] uppercase tracking-widest mb-1">Synthesized Reasoning</div>
                  <div className="text-xs text-gray-400 font-mono leading-relaxed bg-gray-900/50 p-2 rounded">
                    {consensus.reasoning}
                  </div>
                </div>

                {consensus.hr && (
                  <div className="mt-4 flex items-center justify-center gap-2 text-danger text-xs font-bold bg-danger/10 px-3 py-2 border border-danger/30 rounded">
                    <AlertTriangle size={14}/> HUMAN REVIEW REQUIRED
                  </div>
                )}
              </div>
            ) : (
              <div className="flex-1 flex items-center justify-center text-gray-600 text-sm font-mono uppercase tracking-widest">
                Awaiting Baseline
              </div>
            )}
          </div>

          <div className="synapse-panel flex-1 flex flex-col">
            <h2 className="synapse-title">Confidence Evolution</h2>
            <div className="flex-1 w-full bg-gray-900/50 rounded relative overflow-hidden flex items-end">
              {history.length > 0 && (
                <svg className="w-full h-full absolute inset-0" viewBox="0 0 100 100" preserveAspectRatio="none">
                  {/* Grid */}
                  <line x1="0" y1="50" x2="100" y2="50" stroke="#333" strokeDasharray="2,2" strokeWidth="0.5"/>
                  <polyline 
                    points={graphPoints} 
                    fill="none" 
                    stroke="#3b82f6" 
                    strokeWidth="2" 
                    vectorEffect="non-scaling-stroke"
                    className="transition-all duration-700 ease-out"
                  />
                  {history.map((h, i) => (
                    <circle 
                      key={i}
                      cx={(i / (TOTAL_CYCLES - 1 || 1)) * 100}
                      cy={100 - (h.conf * 100)}
                      r="2"
                      fill="#3b82f6"
                    />
                  ))}
                </svg>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* BOTTOM: DECISION EVOLUTION & ENTERPRISE SYSTEMS */}
      <div className="shrink-0 h-40 flex gap-4">
        
        {/* Decision Timeline */}
        <div className="synapse-panel w-1/4 flex flex-col overflow-hidden">
          <h2 className="synapse-title">Decision Timeline</h2>
          <div className="flex-1 overflow-y-auto space-y-2 pr-2">
            {history.map((h, i) => (
              <div key={i} className="flex flex-col">
                <div className={`flex justify-between items-center text-[10px] p-2 rounded transition-colors ${i === history.length - 1 ? 'bg-primary/10 border border-primary/30' : 'bg-gray-900/50'}`}>
                  <span className="text-gray-500 font-mono w-16">{h.timestamp}</span>
                  <span className="text-gray-200 font-mono truncate max-w-[140px] px-2">{h.decision}</span>
                  <span className={`font-bold font-mono ${getConfColor(h.conf)}`}>{(h.conf*100).toFixed(0)}%</span>
                </div>
                {i < history.length - 1 && <div className="text-center text-gray-700 my-0.5">↓</div>}
              </div>
            ))}
          </div>
        </div>

        {/* Enterprise Status Board */}
        <div className="synapse-panel flex-1 flex flex-col">
          <h2 className="synapse-title">Downstream Enterprise Systems</h2>
          <div className="flex flex-1 gap-4">
            {downstream.length > 0 ? (
              downstream.map((sys, i) => {
                const isPanic = sys.status.includes('PANIC') || sys.status.includes('SURGE') || sys.status.includes('DELAY') || sys.status.includes('REROUTING');
                const isNominal = sys.status.includes('NOMINAL');
                const color = isPanic ? 'text-danger' : isNominal ? 'text-success' : 'text-warning';
                const border = isPanic ? 'border-danger/30 bg-danger/5' : isNominal ? 'border-success/30 bg-success/10' : 'border-warning/30 bg-warning/5';
                
                return (
                  <div key={i} className={`flex-1 border rounded p-4 flex flex-col justify-between ${border} transition-all duration-700`}>
                    <div className="text-gray-400 text-xs font-bold uppercase tracking-wider">{sys.system}</div>
                    <div>
                      <div className={`font-mono text-sm font-bold ${color} mb-1`}>{sys.status}</div>
                      <div className="text-[10px] text-gray-500 font-mono uppercase">{getDownstreamSubtext(sys.system, sys.status)}</div>
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="flex-1 flex items-center justify-center text-gray-600 text-sm font-mono uppercase tracking-widest">
                Awaiting consensus baseline...
              </div>
            )}
          </div>
        </div>
        
      </div>

    </div>
  );
}
