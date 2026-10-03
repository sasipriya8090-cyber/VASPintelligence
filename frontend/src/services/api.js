/**
 * API Service for interacting with FastAPI Backend.
 * Handles wallet intelligence analysis, case investigations, and system status.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

class ApiService {
  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  async _request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    try {
      const response = await fetch(url, { ...options, headers });
      if (!response.ok) {
        let errorMsg = `Server error (${response.status})`;
        try {
          const errData = await response.json();
          errorMsg = errData.detail || errorMsg;
        } catch (_) {}
        throw new Error(errorMsg);
      }
      return await response.json();
    } catch (err) {
      if (err.name === 'TypeError' && err.message.includes('fetch')) {
        throw new Error('Unable to connect to intelligence backend. Please verify FastAPI service is running on port 8000.');
      }
      throw err;
    }
  }

  /**
   * Health status check
   */
  async checkHealth() {
    return this._request('/api/health');
  }

  /**
   * List all investigations
   */
  async getInvestigations(skip = 0, limit = 50) {
    return this._request(`/api/investigations?skip=${skip}&limit=${limit}`);
  }

  /**
   * Get single investigation by ID
   */
  async getInvestigation(id) {
    return this._request(`/api/investigations/${id}`);
  }

  /**
   * Create a new investigation case
   */
  async createInvestigation(caseData) {
    return this._request('/api/investigations', {
      method: 'POST',
      body: JSON.stringify(caseData),
    });
  }

  /**
   * Core analysis endpoint: validate and query DEMO blockchain + VASP attribution
   */
  async analyzeWallet(walletAddress, blockchain = 'ethereum') {
    // Client-side pre-validation
    const cleanAddr = (walletAddress || '').trim();
    if (!cleanAddr) {
      throw new Error('Please enter a wallet address.');
    }
    if (blockchain === 'ethereum' && !/^0x[a-fA-F0-9]{40}$/.test(cleanAddr)) {
      throw new Error('Invalid Ethereum address format. Must begin with 0x followed by 40 hex characters.');
    }

    return this._request('/api/analyze/wallet', {
      method: 'POST',
      body: JSON.stringify({
        wallet_address: cleanAddr,
        blockchain: blockchain.toLowerCase(),
      }),
    });
  }
}

export const api = new ApiService();
export default api;
