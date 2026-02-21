<script>
  import { onMount } from "svelte";
  import { Calendar, Download, ChevronDown } from "lucide-svelte";
  import { Button } from "$lib/components/ui/button";
  import * as Tabs from "$lib/components/ui/tabs";
  import * as DropdownMenu from "$lib/components/ui/dropdown-menu";

  import Navbar from "$lib/components/dashboard/Navbar.svelte";
  import DashboardStats from "$lib/components/dashboard/DashboardStats.svelte";
  import CompanyGrid from "$lib/components/dashboard/CompanyGrid.svelte";
  import RecentActivity from "$lib/components/dashboard/RecentActivity.svelte";
  import AnalysisModal from "$lib/components/dashboard/AnalysisModal.svelte";
  import InteractiveAreaChart from "$lib/components/dashboard/InteractiveAreaChart.svelte";
  import ReportsList from "$lib/components/dashboard/ReportsList.svelte";
  import ConfidenceMeter from "$lib/components/dashboard/ConfidenceMeter.svelte";

  import {
    trackTicker,
    analyzeFiling,
    getFeed,
    analyzeCompany,
    getTrackedTickers,
    analyzeBatch,
    getStockHistory,
  } from "./api";

  let trackedTickers = new Set();
  let filingsMap = {};
  let activeAnalysis = null;
  let loading = false;
  let loadingAnalysis = false;
  let loadingStatus = "";
  let feedItems = [];
  let selectedTicker = null;

  onMount(async () => {
    try {
      const { tickers } = await getTrackedTickers();
      // Hydrate state
      for (const t of tickers) {
        loading = true;
        try {
          const data = await trackTicker(t);
          trackedTickers.add(data.ticker);
          trackedTickers = trackedTickers; // Trigger reactivity
          filingsMap[data.ticker] = data.recent_filings;
        } catch (e) {
          console.error(e);
        }
      }
      loading = false;

      // Get Feed
      const feed = await getFeed();
      feedItems = feed.updates;
    } catch (e) {
      console.error("Failed to load dashboard data", e);
    }
  });

  async function handleTrack(ticker) {
    if (!ticker) return;
    loading = true;
    try {
      const data = await trackTicker(ticker);
      trackedTickers.add(data.ticker);
      trackedTickers = trackedTickers;
      handleTickerSelect(data.ticker);
      filingsMap[data.ticker] = data.recent_filings;

      // Refresh feed
      const feed = await getFeed();
      feedItems = feed.updates;
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

  async function handleAnalyzeBatch(event) {
    const filings = event.detail; // Array of filings
    if (!filings || filings.length === 0) return;

    const ticker = filings[0].ticker;
    const form = filings[0].form;
    const date = filings[0].filingDate;

    loadingAnalysis = true;
    loadingStatus = `Analyzing batch of ${filings.length} ${form} filings...`;

    try {
      const res = await analyzeBatch(ticker, filings);
      activeAnalysis = {
        ticker,
        form: `${form} Batch (${date})`,
        title: `Batch Analysis (${filings.length} filings)`,
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
    loadingStatus = `Performing Comprehensive Analysis for ${ticker}...`;
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

  // Reactive Stats
  $: totalFilings = Object.values(filingsMap).reduce(
    (acc, filings) => acc + filings.length,
    0,
  );
  // Mock analysis runs for now, or derive from some state if available.
  // For hackathon, we can just say it's proportional to filings or start at 0.
  $: analysisRuns = Math.floor(totalFilings * 0.8) + (activeAnalysis ? 1 : 0);

  // Time Range for Chart
  let timeRange = "90d";

  // Stock Price Data
  let stockSeries = [];
  const colors = [
    "hsl(263.4 70% 50.4%)", // Violet (Primary)
    "hsl(217.2 91.2% 59.8%)", // Blue
    "hsl(142.1 76.2% 36.3%)", // Green
    "hsl(47.9 95.8% 53.1%)", // Yellow
    "hsl(346.8 77.2% 49.8%)", // Red
    "hsl(24.6 95% 53.1%)", // Orange
  ];

  async function updateStockChart() {
    if (trackedTickers.size > 0) {
      const tickers = Array.from(trackedTickers);
      try {
        const promises = tickers.map((ticker) =>
          getStockHistory(ticker, "1mo"),
        );
        const results = await Promise.all(promises);

        stockSeries = results.map((res, index) => ({
          name: res.ticker,
          color: colors[index % colors.length],
          data: res.history.map((h) => ({
            value: h.price,
            date: h.date,
          })),
        }));
      } catch (e) {
        console.error("Failed to load stock history", e);
      }
    } else {
      stockSeries = [];
    }
  }

  // Reactively update chart when tickers change
  $: if (trackedTickers.size >= 0) {
    updateStockChart();
  }

  // Insider Confidence State
  let confidenceScore = 50;
  let confidenceSentiment = "Neutral";
  let confidenceSummary = "Click refresh to analyze recent filings.";
  let confidenceReasoning = [];
  let confidenceCache = {}; // { ticker: { score, sentiment, summary, reasoning } }

  function handleTickerSelect(ticker) {
    selectedTicker = ticker;

    if (confidenceCache[ticker]) {
      const cached = confidenceCache[ticker];
      confidenceScore = cached.score;
      confidenceSentiment = cached.sentiment;
      confidenceSummary = cached.summary;
      confidenceReasoning = cached.reasoning;
    } else {
      confidenceScore = 50;
      confidenceSentiment = "Neutral";
      confidenceSummary = "Click refresh to analyze " + ticker;
      confidenceReasoning = [];
    }
  }

  async function calculateConfidence() {
    if (allFilings.length === 0) {
      confidenceSummary = "No filings available to analyze.";
      return;
    }

    confidenceSummary = "Analyzing recent filings for whale activity...";

    // Filter filings by selected ticker if available
    let relevantFilings = allFilings;
    if (selectedTicker) {
      relevantFilings = allFilings.filter((f) => f.ticker === selectedTicker);
    }

    if (relevantFilings.length === 0) {
      confidenceSummary = `No filings available for ${selectedTicker || "analysis"}.`;
      return;
    }

    // Take top 20 recent filings
    const recentFilings = relevantFilings.slice(0, 20);
    const ticker = selectedTicker || recentFilings[0].ticker;
    console.log("Analyzing ticker:", ticker);

    confidenceSummary = `Analyzing ${ticker} filings...`;

    try {
      const res = await analyzeBatch(ticker, recentFilings);
      if (res.analysis) {
        // Check if it's the new JSON format
        if (typeof res.analysis === "object") {
          confidenceScore =
            res.analysis.confidence_score !== undefined
              ? res.analysis.confidence_score
              : 50;
          confidenceSentiment = res.analysis.sentiment || "Neutral";
          confidenceSummary = res.analysis.summary || "No summary provided.";
          // Handle potential missing field if backend is old version or failed to parse
          confidenceReasoning = res.analysis.reasoning || [];

          // Cache the result
          confidenceCache[ticker] = {
            score: confidenceScore,
            sentiment: confidenceSentiment,
            summary: confidenceSummary,
            reasoning: confidenceReasoning,
          };
        } else {
          // Fallback for text
          confidenceSummary = "Analysis complete (Text format).";
          confidenceReasoning = [];
        }
      }
    } catch (e) {
      console.error("Confidence analysis failed", e);
      confidenceSummary = "Failed: " + e.message;
    }
  }

  // Restore allFilings for ReportsList
  $: allFilings = Object.values(filingsMap)
    .flat()
    .sort((a, b) => {
      return (
        new Date(b.filingDate).getTime() - new Date(a.filingDate).getTime()
      );
    });

  // Filter filings for Reports tab if a ticker is selected
  $: reportsFilings = selectedTicker
    ? allFilings.filter((f) => f.ticker === selectedTicker)
    : allFilings;
</script>

<div class="min-h-screen flex flex-col font-sans bg-slate-950 p-8">
  <div
    class="w-full max-w-[1400px] mx-auto border border-white/10 rounded-xl bg-slate-950 shadow-2xl overflow-hidden flex flex-col"
  >
    <Navbar onTrack={handleTrack} />

    <main class="w-full flex-1 space-y-4 p-8 pt-6">
      <div class="flex items-center justify-between space-y-2">
        <h2 class="text-3xl font-bold tracking-tight text-white">Dashboard</h2>
        <div class="flex items-center space-x-2">
          <!-- <Button variant="outline" class="hidden sm:flex items-center gap-2">
            <Calendar class="h-4 w-4" />
            <span>Jan 20, 2023 - Feb 09, 2023</span>
          </Button> -->
          <div class="flex items-center gap-2">
            <DropdownMenu.Root>
              <DropdownMenu.Trigger asChild>
                {#snippet children({ props })}
                  <Button
                    {...props}
                    variant="outline"
                    size="sm"
                    class="gap-2 min-w-[140px] justify-between"
                    disabled={false}
                  >
                    <span class="truncate"
                      >{selectedTicker || "Select Ticker"}</span
                    >
                    <ChevronDown class="h-4 w-4 opacity-50" />
                  </Button>
                {/snippet}
              </DropdownMenu.Trigger>
              <DropdownMenu.Content
                class="w-[200px]"
                align="end"
                portalProps={{}}
              >
                <DropdownMenu.Label class="font-normal" inset={false}
                  >Select Ticker</DropdownMenu.Label
                >
                <DropdownMenu.Separator class="-mx-1 my-1 h-px bg-muted" />
                {#if trackedTickers.size === 0}
                  <div class="p-2 text-sm text-muted-foreground text-center">
                    No tickers tracked
                  </div>
                {:else}
                  {#each Array.from(trackedTickers) as ticker}
                    <DropdownMenu.Item
                      onclick={() => handleTickerSelect(ticker)}
                      class="cursor-pointer"
                      inset={false}
                    >
                      {ticker}
                    </DropdownMenu.Item>
                  {/each}
                {/if}
              </DropdownMenu.Content>
            </DropdownMenu.Root>

            <Button size="sm" class="gap-2" disabled={false}>
              <Download class="mr-2 h-4 w-4" />
              Download
            </Button>
          </div>
        </div>
      </div>

      <Tabs.Root value="overview" class="space-y-4">
        <Tabs.List>
          <Tabs.Trigger value="overview" class="cursor-pointer"
            >Overview</Tabs.Trigger
          >
          <Tabs.Trigger value="analytics" class="cursor-pointer"
            >Analytics</Tabs.Trigger
          >
          <Tabs.Trigger value="reports" class="cursor-pointer"
            >Reports</Tabs.Trigger
          >
          <Tabs.Trigger value="notifications" class="cursor-pointer"
            >Notifications</Tabs.Trigger
          >
        </Tabs.List>

        <Tabs.Content value="overview" class="space-y-4">
          <InteractiveAreaChart
            series={stockSeries}
            {timeRange}
            label={"Price"}
            formatValue={(v) => `$${v.toFixed(2)}`}
          />
          <DashboardStats
            trackedCount={trackedTickers.size}
            {totalFilings}
            {analysisRuns}
            activeMonitors={trackedTickers.size}
          />

          <div class="grid grid-cols-1 lg:grid-cols-7 gap-6 items-start">
            <div
              class="lg:col-span-4 bg-slate-800/50 border border-white/10 rounded-xl p-6 shadow-sm"
            >
              <CompanyGrid
                {trackedTickers}
                {filingsMap}
                onAnalyze={handleAnalyze}
                onComprehensiveAnalyze={handleComprehensiveAnalyze}
                onSelect={handleTickerSelect}
              />
            </div>

            <div
              class="lg:col-span-3 bg-slate-800/50 border border-white/10 rounded-xl p-6 shadow-sm"
            >
              <RecentActivity {feedItems} />
            </div>
          </div>
        </Tabs.Content>

        <Tabs.Content value="analytics" class="space-y-4">
          <div class="flex items-center justify-between">
            <h3 class="text-xl font-bold text-white">
              {#if selectedTicker}
                Analytics for <span class="text-blue-400">{selectedTicker}</span
                >
              {:else}
                Select a company to view analytics
              {/if}
            </h3>
          </div>

          {#if selectedTicker}
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- Insider Confidence Meter -->
              <ConfidenceMeter
                score={confidenceScore}
                sentiment={confidenceSentiment}
                summary={confidenceSummary}
                ticker={selectedTicker}
                on:refresh={calculateConfidence}
              />

              <!-- Confidence Reasoning / Explanation -->
              <div
                class="bg-slate-800/50 border border-white/10 rounded-xl p-6 flex flex-col"
              >
                <div class="flex items-center justify-between mb-4">
                  <h4 class="text-lg font-semibold text-white">
                    Analysis Reasoning
                  </h4>
                  {#if confidenceReasoning.length > 0}
                    <span
                      class="text-xs text-slate-400 bg-slate-800 px-2 py-1 rounded-full border border-white/5"
                      >{confidenceReasoning.length} factors</span
                    >
                  {/if}
                </div>

                {#if confidenceReasoning && confidenceReasoning.length > 0}
                  <ul class="space-y-3">
                    {#each confidenceReasoning as point}
                      <li class="flex items-start gap-3 text-sm text-slate-300">
                        <span
                          class="mt-1.5 w-1.5 h-1.5 rounded-full bg-blue-400 shrink-0"
                        ></span>
                        <span class="leading-relaxed">{point}</span>
                      </li>
                    {/each}
                  </ul>
                {:else}
                  <div
                    class="flex-1 flex flex-col items-center justify-center text-center p-4"
                  >
                    <p class="text-slate-400 italic mb-2">
                      No detailed reasoning available.
                    </p>
                    <p class="text-xs text-slate-500">
                      Try refreshing the analysis to generate key insights.
                    </p>
                  </div>
                {/if}
              </div>
            </div>
          {:else}
            <div
              class="p-12 text-center border border-dashed border-slate-700 rounded-xl bg-slate-900/20"
            >
              <div
                class="w-16 h-16 bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-4"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="w-8 h-8 text-slate-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
              </div>
              <h4 class="text-lg font-medium text-white mb-2">
                No Company Selected
              </h4>
              <p class="text-slate-400 max-w-md mx-auto">
                Search for and select a company in the Overview tab to view
                detailed insider confidence analysis.
              </p>
            </div>
          {/if}
        </Tabs.Content>

        <Tabs.Content value="reports" class="space-y-4">
          <div class="border border-white/10 rounded-xl p-6 bg-slate-800/50">
            <div class="mb-4">
              <h3 class="text-lg font-medium text-white">All Filings</h3>
              <p class="text-sm text-muted-foreground">
                View and analyze all tracked filings.
              </p>
            </div>
            <ReportsList
              allFilings={reportsFilings}
              onAnalyze={handleAnalyze}
              on:analyzeBatch={handleAnalyzeBatch}
            />
          </div>
        </Tabs.Content>

        <Tabs.Content value="notifications" class="space-y-4">
          <div
            class="border border-white/10 rounded-xl p-6 bg-slate-800/50 max-w-md mx-auto mt-10"
          >
            <div class="mb-6 text-center">
              <h3 class="text-xl font-medium text-white mb-2">
                Get Email Alerts
              </h3>
              <p class="text-sm text-muted-foreground">
                Subscribe to get notified when new filings are analyzed for your
                tracked tickers.
              </p>
            </div>

            <div class="space-y-4">
              <div class="space-y-2">
                <label for="email" class="text-sm font-medium text-slate-300"
                  >Email Address</label
                >
                <input
                  type="email"
                  id="email"
                  placeholder="you@example.com"
                  class="flex h-10 w-full rounded-md border border-white/10 bg-slate-950 px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 text-white"
                />
              </div>
              <Button
                class="w-full"
                onclick={() => alert("Email alerts coming soon!")}
                disabled={false}
              >
                Subscribe to Alerts
              </Button>
            </div>
          </div>
        </Tabs.Content>
      </Tabs.Root>
    </main>
  </div>
</div>

{#if activeAnalysis || loadingAnalysis}
  <AnalysisModal
    {activeAnalysis}
    {loadingAnalysis}
    {loadingStatus}
    onClose={closeAnalysis}
  />
{/if}
