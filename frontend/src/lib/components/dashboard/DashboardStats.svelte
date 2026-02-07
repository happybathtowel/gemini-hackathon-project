<script>
    import { TrendingUp, Activity, FileText, Users } from "lucide-svelte";
    import * as Card from "$lib/components/ui/card";

    export let trackedCount = 0;
    export let totalFilings = 0;
    export let analysisRuns = 0;
    export let activeMonitors = 0;
</script>

<div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
    <Card.Root class="bg-slate-800/50 border-white/10 text-white shadow-sm">
        <Card.Header
            class="flex flex-row items-center justify-between space-y-0 pb-2"
        >
            <Card.Title class="text-sm font-medium">Total Companies</Card.Title>
            <Users class="h-4 w-4 text-slate-400" />
        </Card.Header>
        <Card.Content>
            <div class="text-2xl font-bold">{trackedCount}</div>
            <p class="text-xs text-slate-400">+20.1% from last month</p>
        </Card.Content>
    </Card.Root>
    <Card.Root class="bg-slate-800/50 border-white/10 text-white shadow-sm">
        <Card.Header
            class="flex flex-row items-center justify-between space-y-0 pb-2"
        >
            <Card.Title class="text-sm font-medium">Total Filings</Card.Title>
            <FileText class="h-4 w-4 text-slate-400" />
        </Card.Header>
        <Card.Content>
            <div class="text-2xl font-bold">{totalFilings}</div>
            <p class="text-xs text-slate-400">+180.1% from last month</p>
        </Card.Content>
    </Card.Root>
    <Card.Root class="bg-slate-800/50 border-white/10 text-white shadow-sm">
        <Card.Header
            class="flex flex-row items-center justify-between space-y-0 pb-2"
        >
            <Card.Title class="text-sm font-medium">Analysis Runs</Card.Title>
            <Activity class="h-4 w-4 text-slate-400" />
        </Card.Header>
        <Card.Content>
            <div class="text-2xl font-bold">{analysisRuns}</div>
            <p class="text-xs text-slate-400">+19% from last month</p>
        </Card.Content>
    </Card.Root>
    <Card.Root class="bg-slate-800/50 border-white/10 text-white shadow-sm">
        <Card.Header
            class="flex flex-row items-center justify-between space-y-0 pb-2"
        >
            <Card.Title class="text-sm font-medium">Active Monitors</Card.Title>
            <TrendingUp class="h-4 w-4 text-slate-400" />
        </Card.Header>
        <Card.Content>
            <div class="text-2xl font-bold">{activeMonitors}</div>
            <p class="text-xs text-slate-400">+201 since last hour</p>
        </Card.Content>
    </Card.Root>
</div>
