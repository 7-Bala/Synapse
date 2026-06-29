/**
 * Evidence models for injecting data into the system.
 */
export interface SourceReference {
  id: string;
  name: string;
  type: string;
  url?: string;
}

export interface Citation {
  evidenceId: string;
  snippet: string;
  source: SourceReference;
}

export interface ProvenanceChain {
  nodeId: string;
  action: string;
  timestamp: string;
}

export interface Evidence {
  id: string;
  timestamp: string;
  content: string;
  source: string;
  citations?: Citation[];
  provenance?: ProvenanceChain[];
}
