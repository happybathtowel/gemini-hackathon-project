<script>
  import { onMount } from "svelte";
  import { trackTicker, analyzeFiling, getFeed, analyzeCompany } from "./api";

  let tickerInput = "";
  let trackedTickers = new Set();
  let filingsMap = {}; // { AAPL: [filing1, filing2] }
  let activeAnalysis = null; // { ticker: 'AAPL', form: 'Comprehensive', content: '...' }
  let loading = false;
  let loadingAnalysis = false;
  let loadingStatus = ""; // Detailed status for long operations

  async function handleTrack() {
    if (!tickerInput) return;
    loading = true;
    try {
      const data = await trackTicker(tickerInput);
      trackedTickers.add(data.ticker);
      trackedTickers = trackedTickers; // Trigger reactivity
      filingsMap[data.ticker] = data.recent_filings;
      tickerInput = "";
    } catch (e) {
      alert(e.message);
    } finally {
      loading = false;
    }
  }

  async function handleAnalyze(url, ticker, form) {
    loadingAnalysis = true;
    loadingStatus = `Analyzing ${form}...`;
    try {
      const res = await analyzeFiling(url, ticker, form);
      activeAnalysis = {
        ticker,
        form: `${form} Analysis`,
        content: res.analysis,
      };
    } catch (e) {
      alert(e.message);
    } finally {
      loadingAnalysis = false;
      loadingStatus = "";
    }
  }

  async function handleComprehensiveAnalyze(ticker) {
    loadingAnalysis = true;
    loadingStatus = `Performing Comprehensive Analysis for ${ticker} (Scanning recent filings)...`;
    try {
      const res = await analyzeCompany(ticker);
      activeAnalysis = {
        ticker,
        form: "Comprehensive Report",
        content: res.report,
      };
    } catch (e) {
      alert(e.message);
    } finally {
      loadingAnalysis = false;
      loadingStatus = "";
    }
  }

  function closeAnalysis() {
    activeAnalysis = null;
  }
</script>

<main class="min-h-screen text-gray-100 p-8">
  <header class="mb-12 flex justify-between items-center">
    <div>
      <h1
        class="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-brand-400 to-purple-600"
      >
        SEC INSIGHT
      </h1>
      <p class="text-gray-400 mt-2">
        Real-time market intelligence powered by Gemini 3
      </p>
    </div>
    <div class="glass-panel p-2 flex gap-2">
      <input
        bind:value={tickerInput}
        type="text"
        placeholder="Enter Ticker (e.g. AAPL)"
        class="bg-transparent border-none outline-none px-4 text-white placeholder-gray-500 w-64"
        on:keydown={(e) => e.key === "Enter" && handleTrack()}
      />
      <button
        on:click={handleTrack}
        disabled={loading}
        class="bg-brand-500 hover:bg-brand-400 text-white px-6 py-2 rounded-lg transition-colors font-medium disabled:opacity-50"
      >
        {loading ? "Tracking..." : "Track"}
      </button>
    </div>
  </header>

  <section class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    {#each Array.from(trackedTickers) as ticker}
      <div class="glass-panel p-6 hover:border-brand-500/50 transition-colors">
        <h2 class="text-2xl font-bold mb-4 flex justify-between items-center">
          {ticker}
          <span class="text-xs bg-brand-500/20 text-brand-400 px-2 py-1 rounded"
            >Live</span
          >
        </h2>

        <div class="space-y-3">
          <button
            on:click={() => handleComprehensiveAnalyze(ticker)}
            class="w-full mb-4 bg-gradient-to-r from-purple-600 to-brand-500 hover:from-purple-500 hover:to-brand-400 text-white py-2 rounded-lg font-medium shadow-lg shadow-brand-500/20 transition-all text-sm flex items-center justify-center gap-2"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-4 w-4"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z"
              />
            </svg>
            Comprehensive Analysis
          </button>

          <p
            class="text-xs text-gray-400 uppercase tracking-widest font-semibold"
          >
            Recent Filings
          </p>
          {#if filingsMap[ticker]}
            {#each filingsMap[ticker].slice(0, 5) as filing}
              <div
                class="flex justify-between items-center p-2 rounded hover:bg-white/5 transition-colors group"
              >
                <div>
                  <div class="font-bold text-sm text-white">{filing.form}</div>
                  <div class="text-xs text-gray-500">{filing.filingDate}</div>
                </div>
                <button
                  on:click={() =>
                    handleAnalyze(filing.url, ticker, filing.form)}
                  class="opacity-0 group-hover:opacity-100 text-xs bg-brand-500/20 text-brand-400 px-3 py-1 rounded hover:bg-brand-500 hover:text-white transition-all"
                >
                  Analyze
                </button>
              </div>
            {/each}
          {:else}
            <p class="text-gray-500 text-sm">No recent filings found.</p>
          {/if}
        </div>
      </div>
    {/each}

    {#if trackedTickers.size === 0}
      <div class="col-span-full text-center py-20 text-gray-600">
        <p class="text-xl">Track a company to start receiving intelligence.</p>
      </div>
    {/if}
  </section>

  <!-- Analysis Modal -->
  {#if activeAnalysis || loadingAnalysis}
    <div
      class="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-8 z-50"
      on:click={closeAnalysis}
    >
      <div
        class="glass-panel w-full max-w-4xl max-h-[90vh] overflow-y-auto p-8 relative"
        on:click|stopPropagation
      >
        {#if loadingAnalysis}
          <div class="flex flex-col items-center justify-center h-64">
            <div
              class="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-500 mb-4"
            ></div>
            <p class="text-brand-400 animate-pulse">
              {loadingStatus || "Gemini 3 is analyzing..."}
            </p>
          </div>
        {:else}
          <button
            on:click={closeAnalysis}
            class="absolute top-4 right-4 text-gray-400 hover:text-white"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
          <div
            class="flex justify-between items-end mb-6 border-b border-gray-700 pb-4"
          >
            <div>
              <h2 class="text-3xl font-bold text-white">
                {activeAnalysis.title || activeAnalysis.ticker}
              </h2>
              <p class="text-brand-400">{activeAnalysis.form}</p>
            </div>
            <div class="text-xs text-gray-500">Generated by Gemini 2.0</div>
          </div>

          <div
            class="prose prose-invert prose-indigo max-w-none whitespace-pre-wrap font-sans leading-relaxed"
          >
            <!-- Simple markdown rendering -->
            {@html activeAnalysis.content
              .replace(
                /^# (.*$)/gim,
                '<h1 class="text-2xl font-bold text-white mb-4">$1</h1>',
              )
              .replace(
                /^## (.*$)/gim,
                '<h2 class="text-xl font-semibold text-brand-300 mt-6 mb-3">$1</h2>',
              )
              .replace(
                /^### (.*$)/gim,
                '<h3 class="text-lg font-medium text-white mt-4 mb-2">$1</h3>',
              )
              .replace(
                /\*\*(.*?)\*\*/g,
                '<strong class="text-white">$1</strong>',
              )
              .replace(
                /^\- (.*$)/gim,
                '<li class="ml-4 list-disc text-gray-300">$1</li>',
              )}
          </div>
        {/if}
      </div>
    </div>
  {/if}
</main>
