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

  import {
    trackTicker,
    analyzeFiling,
    getFeed,
    analyzeCompany,
    getTrackedTickers,
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

  // Derive Chart Data (Filings over time)
  $: chartData = (() => {
    const allFilings = Object.values(filingsMap).flat();
    const countsByDate = {};

    allFilings.forEach((f) => {
      // Normalize date to YYYY-MM-DD
      const date = f.filingDate.split(" ")[0]; // Assuming "YYYY-MM-DD" or similar
      countsByDate[date] = (countsByDate[date] || 0) + 1;
    });

    // Sort by date
    const sortedDates = Object.keys(countsByDate).sort();

    // Fill in gaps? For now, just map existing dates.
    // Ideally we'd fill gaps with 0 for a smooth line, but let's start simple.
    return sortedDates.map((date) => ({
      date,
      count: countsByDate[date],
    }));
  })();
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
          <Button variant="outline" class="hidden sm:flex items-center gap-2">
            <Calendar class="h-4 w-4" />
            <span>Jan 20, 2023 - Feb 09, 2023</span>
          </Button>
          <Button size="sm">
            <Download class="mr-2 h-4 w-4" />
            Download
          </Button>
        </div>
      </div>

      <Tabs.Root value="overview" class="space-y-4">
        <Tabs.List>
          <Tabs.Trigger value="overview">Overview</Tabs.Trigger>
          <Tabs.Trigger value="analytics" disabled>Analytics</Tabs.Trigger>
          <Tabs.Trigger value="reports" disabled>Reports</Tabs.Trigger>
          <Tabs.Trigger value="notifications" disabled
            >Notifications</Tabs.Trigger
          >
        </Tabs.List>

        <Tabs.Content value="overview" class="space-y-4">
          <InteractiveAreaChart data={chartData} {timeRange} />
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
