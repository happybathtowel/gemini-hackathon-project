<script>
    import * as Card from "$lib/components/ui/card";
    import { Button } from "$lib/components/ui/button";

    export let trackedTickers = new Set();
    export let filingsMap = {};
    export let onAnalyze;
    export let onComprehensiveAnalyze;

    $: chartData = Array.from(trackedTickers).map((ticker) => {
        const count = filingsMap[ticker]?.length || 0;
        return { name: ticker, total: count };
    });
</script>

<Card.Root class="h-full bg-transparent border-0 shadow-none p-0">
    <Card.Header>
        <Card.Title>Overview</Card.Title>
    </Card.Header>
    <Card.Content class="pl-2">
        {#if chartData.length > 0}
            <div class="space-y-4">
                {#each chartData as data}
                    <div class="flex items-center">
                        <div class="w-16 text-sm font-medium">{data.name}</div>
                        <div
                            class="flex-1 h-8 bg-secondary rounded-full overflow-hidden mx-4 relative group cursor-pointer"
                            on:click={() => onComprehensiveAnalyze(data.name)}
                        >
                            <div
                                class="h-full bg-primary transition-all duration-500 ease-in-out"
                                style="width: {Math.max(
                                    (data.total / 50) * 100,
                                    5,
                                )}%"
                            ></div>
                            <div
                                class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity text-xs font-bold text-primary-foreground"
                            >
                                Analyze {data.name}
                            </div>
                        </div>
                        <div
                            class="w-12 text-sm text-right text-muted-foreground"
                        >
                            {data.total} filings
                        </div>
                    </div>
                {/each}
            </div>
        {:else}
            <div
                class="h-[350px] flex items-center justify-center text-muted-foreground"
            >
                No data available. Add a ticker to see analysis.
            </div>
        {/if}
    </Card.Content>
</Card.Root>
