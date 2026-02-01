const API_BASE = "http://localhost:8000";

export async function trackTicker(ticker) {
    const response = await fetch(`${API_BASE}/api/track`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ticker }),
    });
    if (!response.ok) throw new Error("Failed to track ticker");
    return response.json();
}

export async function analyzeFiling(url, ticker, form) {
    // Correct query params syntax
    const response = await fetch(`${API_BASE}/api/analyze?url=${encodeURIComponent(url)}&ticker=${ticker}&form=${form}`, {
        method: "POST"
    });
    if (!response.ok) throw new Error("Failed to analyze filing");
    return response.json();
}

export async function getFeed() {
    const response = await fetch(`${API_BASE}/api/feed`);
    if (!response.ok) throw new Error("Failed to get feed");
    return response.json();
}

export async function analyzeCompany(ticker) {
    const response = await fetch(`${API_BASE}/api/analyze-company`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ticker }),
    });
    if (!response.ok) throw new Error("Failed to analyze company");
    return response.json();
}

export async function getTrackedTickers() {
    const response = await fetch(`${API_BASE}/api/tracked`);
    if (!response.ok) throw new Error("Failed to get tracked tickers");
    return response.json();
}
