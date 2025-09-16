// const API_BASE_URL = 'http://127.0.0.1:8000';    // Local Url
const API_BASE_URL = 'https://deepresearchbackend.victoriousdune-f3f8dc93.centralindia.azurecontainerapps.io';  // Azure URL

// Different timeouts for different operations
const LONG_TIMEOUT_MS = 600000; // 10 minutes for research operations
const SHORT_TIMEOUT_MS = 30000;  // 30 seconds for status checks

const fetchWithTimeout = async (url, options = {}, timeoutMs = SHORT_TIMEOUT_MS) => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    if (error.name === 'AbortError') {
      throw new Error(`Request timeout - operation took longer than ${timeoutMs/1000} seconds`);
    }
    throw error;
  }
};

// Passive wait (no AbortController timeouts)
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// Summary must be truly populated (not empty, not a failure placeholder)
export function isSummaryReady(report) {
  if (!report || typeof report !== 'object') return false;
  const s = (report.summary ?? report.final_report ?? '').toString().trim();
  if (!s) return false;
  const lower = s.toLowerCase();
  if (lower === 'summarization failed.' || lower === 'summarization failed') return false;

  // Require some body; tweak as needed
  const minChars = 120;
  return s.length >= minChars;
}

// Back-compat: some components call hasValidReport; map to summary readiness
export function hasValidReport(report) {
  return isSummaryReady(report);
}

// Strict fetch: wait for COMPLETE, then poll /results until summary is ready
async function getResultsStrict(taskId, { pollIntervalMs = 2000, onProgress } = {}) {
  // 1) Wait for COMPLETE
  while (true) {
    try {
      const res = await fetch(`http://127.0.0.1:8000/status/${encodeURIComponent(taskId)}`, {
        headers: { 'Cache-Control': 'no-store' },
      });
      if (res.ok) {
        const data = await res.json();
        const status = data?.status;
        if (typeof onProgress === 'function') onProgress(`Status: ${status || 'UNKNOWN'}`);
        if (status === 'COMPLETE') break;
        if (status === 'AWAITING_INPUT') {
          throw new Error('Task is awaiting input again. Please refresh and try again.');
        }
      }
    } catch (_) {
      // transient error; keep waiting
    }
    await sleep(pollIntervalMs);
  }

  // 2) Poll results until summary is actually populated
  while (true) {
    try {
      const res = await fetch(`http://127.0.0.1:8000/results/${encodeURIComponent(taskId)}`, {
        headers: { 'Cache-Control': 'no-store' },
      });
      if (res.ok) {
        const report = await res.json();
        if (typeof onProgress === 'function') onProgress('Checking summary...');
        if (isSummaryReady(report)) return report;
      }
    } catch (_) {
      // transient error; keep waiting
    }
    await sleep(pollIntervalMs);
  }
}

// If you have an existing api object, replace its getResults implementation:
export const api = {
  // Start a new research task (long timeout)
  async startResearch(requestData) {
    // Handle both old string format and new object format for backward compatibility
    const body = typeof requestData === 'string' 
      ? JSON.stringify({ query: requestData })
      : JSON.stringify(requestData);
      
    const response = await fetchWithTimeout(`${API_BASE_URL}/research`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body,
    }, LONG_TIMEOUT_MS);
    
    if (!response.ok) {
      throw new Error(`Failed to start research: ${response.statusText}`);
    }
    
    return response.json();
  },

  // Get task status and research questions (short timeout)
  async getTaskStatus(taskId) {
    const response = await fetchWithTimeout(`${API_BASE_URL}/status/${taskId}`, {}, SHORT_TIMEOUT_MS);
    
    if (!response.ok) {
      throw new Error(`Failed to get task status: ${response.statusText}`);
    }
    
    return response.json();
  },

  // Resume task with approved research questions (long timeout)
  async resumeTask(taskId, researchQuestions) {
    const response = await fetchWithTimeout(`${API_BASE_URL}/resume/${taskId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ research_questions: researchQuestions }),
    }, LONG_TIMEOUT_MS);
    
    if (!response.ok) {
      throw new Error(`Failed to resume task: ${response.statusText}`);
    }
    
    return response.json();
  },

  // Replace the api.getResults to use strict mode
  getResults: (taskId, opts) => getResultsStrict(taskId, opts),
};

export default api;
