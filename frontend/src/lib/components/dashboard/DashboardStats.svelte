<script>
    import { TrendingUp, Activity, FileText, Users } from "lucide-svelte";
    import * as Card from "$lib/components/ui/card";

    export let trackedCount = 0;
</script>

<div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
    <Card.Root
        style="background-color: #1e293b; border: 1px solid rgba(255,255,255,0.1); border-radius: 12px;"
    >
        <Card.Header
            class="flex flex-row items-center justify-between space-y-0 pb-2"
        >
            <Card.Title class="text-sm font-medium">Total Companies</Card.Title>
            <Users class="h-4 w-4 text-muted-foreground" />
        </Card.Header>
        <Card.Content>
            <div class="text-2xl font-bold">{trackedCount}</div>
            <p class="text-xs text-muted-foreground">+20.1% from last month</p>
        </Card.Content>
    </Card.Root>
    <Card.Root
        style="background-color: #1e293b; border: 1px solid rgba(255,255,255,0.1); border-radius: 12px;"
    >
        <Card.Header
            class="flex flex-row items-center justify-between space-y-0 pb-2"
        >
            <Card.Title class="text-sm font-medium">Total Filings</Card.Title>
            <FileText class="h-4 w-4 text-muted-foreground" />
        </Card.Header>
        <Card.Content>
            <div class="text-2xl font-bold">+2350</div>
            <p class="text-xs text-muted-foreground">+180.1% from last month</p>
        </Card.Content>
    </Card.Root>
    <Card.Root
        style="background-color: #1e293b; border: 1px solid rgba(255,255,255,0.1); border-radius: 12px;"
    >
        <Card.Header
            class="flex flex-row items-center justify-between space-y-0 pb-2"
        >
            <Card.Title class="text-sm font-medium">Analysis Runs</Card.Title>
            <Activity class="h-4 w-4 text-muted-foreground" />
        </Card.Header>
        <Card.Content>
            <div class="text-2xl font-bold">+12,234</div>
            <p class="text-xs text-muted-foreground">+19% from last month</p>
        </Card.Content>
    </Card.Root>
    <Card.Root
        style="background-color: #1e293b; border: 1px solid rgba(255,255,255,0.1); border-radius: 12px;"
    >
        <Card.Header
            class="flex flex-row items-center justify-between space-y-0 pb-2"
        >
            <Card.Title class="text-sm font-medium">Active Monitors</Card.Title>
            <TrendingUp class="h-4 w-4 text-muted-foreground" />
        </Card.Header>
        <Card.Content>
            <div class="text-2xl font-bold">+{trackedCount}</div>
            <p class="text-xs text-muted-foreground">+201 since last hour</p>
        </Card.Content>
    </Card.Root>
</div>

<style>
    /* Manual Grid Fix for Broken Tailwind */
    .grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 1rem;
    }

    @media (min-width: 768px) {
        .grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }

    @media (min-width: 1024px) {
        .grid {
            grid-template-columns: repeat(4, 1fr);
        }
    }
</style>
