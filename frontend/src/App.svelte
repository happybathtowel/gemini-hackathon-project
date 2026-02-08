<script>
  import { onMount } from "svelte";
  import { Calendar, Download } from "lucide-svelte";
  import { Button } from "$lib/components/ui/button";
  import * as Tabs from "$lib/components/ui/tabs";

  import Navbar from "$lib/components/dashboard/Navbar.svelte";
  import DashboardStats from "$lib/components/dashboard/DashboardStats.svelte";
  import CompanyGrid from "$lib/components/dashboard/CompanyGrid.svelte";
  import RecentActivity from "$lib/components/dashboard/RecentActivity.svelte";
  import AnalysisModal from "$lib/components/dashboard/AnalysisModal.svelte";
  import InteractiveAreaChart from "$lib/components/dashboard/InteractiveAreaChart.svelte";
  import ReportsList from "$lib/components/dashboard/ReportsList.svelte";

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

  // Restore allFilings for ReportsList
  $: allFilings = Object.values(filingsMap)
    .flat()
    .sort((a, b) => {
      return (
        new Date(b.filingDate).getTime() - new Date(a.filingDate).getTime()
      );
    });
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
          <Button size="sm">
            <Download class="mr-2 h-4 w-4" />
            Download
          </Button>
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
              />
            </div>

            <div
              class="lg:col-span-3 bg-slate-800/50 border border-white/10 rounded-xl p-6 shadow-sm"
            >
              <RecentActivity {feedItems} />
            </div>
          </div>
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
              {allFilings}
              onAnalyze={handleAnalyze}
              on:analyzeBatch={handleAnalyzeBatch}
            />
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
