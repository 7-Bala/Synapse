/**
 * @module FormattingUtilities
 * @description Standardized data display formats for Synapse telemetry and operations.
 */
export function formatBytes(bytes: number, decimals = 2): string {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

export function formatLatency(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(2)}s`;
}

export function formatHash(hash: string, length = 8): string {
  if (!hash) return '';
  if (hash.length <= length * 2) return hash;
  return `${hash.slice(0, length)}...${hash.slice(-length)}`;
}

export function formatDuration(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  if (h > 0) return `${h}h ${m}m ${s}s`;
  if (m > 0) return `${m}m ${s}s`;
  return `${s}s`;
}

export function formatPercentage(val: number, decimals = 1): string {
  return `${(val * 100).toFixed(decimals)}%`;
}

export function formatMemory(bytes: number): string {
  return formatBytes(bytes, 1);
}

export function formatCPU(cores: number): string {
  return `${cores.toFixed(2)} cores`;
}

export function formatNetwork(bps: number): string {
  if (bps === 0) return '0 bps';
  const k = 1000;
  const sizes = ['bps', 'Kbps', 'Mbps', 'Gbps', 'Tbps'];
  const i = Math.floor(Math.log(bps) / Math.log(k));
  return parseFloat((bps / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

export function formatTimestamp(isoString: string): string {
  const d = new Date(isoString);
  return d.toISOString().replace('T', ' ').substring(0, 19);
}

export function formatDate(isoString: string): string {
  return new Date(isoString).toLocaleDateString();
}

export function formatRelativeTime(isoString: string): string {
  const diff = Date.now() - new Date(isoString).getTime();
  const sec = Math.floor(diff / 1000);
  if (sec < 60) return `${sec}s ago`;
  const min = Math.floor(sec / 60);
  if (min < 60) return `${min}m ago`;
  const hrs = Math.floor(min / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}

export function formatConfidence(score: number): string {
  return formatPercentage(score, 1);
}

export function formatDeterminism(score: number): string {
  return score === 1.0 ? '100% (Deterministic)' : formatPercentage(score, 1);
}

export function formatEventsPerSec(eps: number): string {
  return `${eps.toFixed(1)} e/s`;
}

export function formatTokensPerSec(tps: number): string {
  return `${tps.toFixed(1)} tok/s`;
}

export function formatCost(amount: number, currency = 'USD'): string {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency }).format(amount);
}

export function formatCurrency(amount: number, currency = 'USD'): string {
  return formatCost(amount, currency);
}

export function formatLargeNumber(num: number): string {
  return new Intl.NumberFormat('en-US', { notation: 'compact', compactDisplay: 'short' }).format(num);
}

export function formatScientificNotation(num: number): string {
  return num.toExponential(2);
}
