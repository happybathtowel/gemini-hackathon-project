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
</script>

<div
  class="min-h-screen flex flex-col font-sans"
  style="background-color: #0f172a; padding: 2rem;"
>
  <div
    class="dashboard-container flex flex-col"
    style="
      width: 100%; 
      max-width: 1400px; 
      margin: 0 auto; 
      border: 1px solid rgba(255, 255, 255, 0.1); 
      border-radius: 12px; 
      background-color: #020617; 
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); 
      overflow: hidden;
    "
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
          <DashboardStats trackedCount={trackedTickers.size} />

          <div class="main-dashboard-grid gap-4 items-start">
            <div
              class="overview-section"
              style="background-color: #1e293b; border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);"
            >
              <CompanyGrid
                {trackedTickers}
                {filingsMap}
                onAnalyze={handleAnalyze}
                onComprehensiveAnalyze={handleComprehensiveAnalyze}
              />
            </div>

            <div
              class="recent-section"
              style="background-color: #1e293b; border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);"
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

<style>
  /* Manual Grid Fix for Broken Tailwind */
  .main-dashboard-grid {
    display: flex;
    flex-direction: column;
  }

  @media (min-width: 1024px) {
    .main-dashboard-grid {
      display: grid;
      grid-template-columns: repeat(7, 1fr);
    }
    .overview-section {
      grid-column: span 4 / span 4;
    }
    .recent-section {
      grid-column: span 3 / span 3;
    }
  }
</style>
