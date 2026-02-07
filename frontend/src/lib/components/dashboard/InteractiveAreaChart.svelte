<script>
    import { onMount } from "svelte";
    import * as Card from "$lib/components/ui/card";
    import { Button } from "$lib/components/ui/button";

    export let data = [];
    export let timeRange = "90d";

    // Chart Dimensions
    let width = 0;
    let height = 250;
    let container;

    // Tooltip state
    let hoverIndex = -1;
    let tooltipX = 0;
    let tooltipY = 0;

    // Scaling helpers
    $: maxVal = Math.max(...data.map((d) => d.count), 5) * 1.1; // Ensure at least some height
    $: xStep = width / (data.length - 1 || 1);

    $: points = data.map((d, i) => {
        const x = i * xStep;
        const y = height - (d.count / maxVal) * height;
        return { x, y, val: d.count };
    });

    // Path Generation
    $: areaPath =
        `M 0 ${height} ` +
        points.map((p) => `L ${p.x} ${p.y}`).join(" ") +
        ` L ${width} ${height} Z`;

    $: linePath =
        points.length > 0
            ? `M 0 ${points[0].y} ` +
              points.map((p) => `L ${p.x} ${p.y}`).join(" ")
            : "";

    function handleMouseMove(e) {
        if (!container) return;
        const rect = container.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const index = Math.min(
            Math.max(Math.round(x / xStep), 0),
            data.length - 1,
        );

        hoverIndex = index;
        tooltipX = x;
        if (points[index]) {
            tooltipX = points[index].x;
        }
    }

    function handleMouseLeave() {
        hoverIndex = -1;
    }
</script>

<div
    class="visual-card w-full bg-slate-800/50 border border-white/10 rounded-xl shadow-sm"
>
    <Card.Root class="bg-transparent border-0 shadow-none">
        <Card.Header
            class="flex items-center gap-2 space-y-0 border-b border-white/5 py-5 sm:flex-row"
        >
            <div class="grid flex-1 gap-1 text-center sm:text-left">
                <Card.Title>Filings Activity</Card.Title>
                <Card.Description>
                    Showing total filings for the last {timeRange === "90d"
                        ? "3 months"
                        : timeRange === "30d"
                          ? "30 days"
                          : "7 days"}
                </Card.Description>
            </div>
        </Card.Header>

        <Card.Content class="px-2 pt-4 sm:px-6 sm:pt-6">
            <div
                class="chart-container aspect-auto h-[250px] w-full relative"
                bind:this={container}
                bind:clientWidth={width}
                on:mousemove={handleMouseMove}
                on:mouseleave={handleMouseLeave}
                role="img"
            >
                {#if width > 0 && data.length > 0}
                    <svg
                        {width}
                        {height}
                        viewBox="0 0 {width} {height}"
                        class="overflow-visible"
                    >
                        <defs>
                            <linearGradient
                                id="fillGradient"
                                x1="0"
                                y1="0"
                                x2="0"
                                y2="1"
                            >
                                <stop
                                    offset="5%"
                                    stop-color="hsl(263.4 70% 50.4%)"
                                    stop-opacity="0.8"
                                />
                                <stop
                                    offset="95%"
                                    stop-color="hsl(263.4 70% 50.4%)"
                                    stop-opacity="0.1"
                                />
                            </linearGradient>
                        </defs>

                        <!-- Area -->
                        <path d={areaPath} fill="url(#fillGradient)" />
                        <!-- Line -->
                        <path
                            d={linePath}
                            fill="none"
                            stroke="hsl(263.4 70% 50.4%)"
                            stroke-width="2"
                        />

                        <!-- Interactive Elements -->
                        {#if hoverIndex !== -1 && points[hoverIndex]}
                            <line
                                x1={points[hoverIndex].x}
                                y1={0}
                                x2={points[hoverIndex].x}
                                y2={height}
                                stroke="white"
                                stroke-dasharray="4 4"
                                opacity="0.5"
                            />
                            <circle
                                cx={points[hoverIndex].x}
                                cy={points[hoverIndex].y}
                                r="4"
                                fill="white"
                                stroke="hsl(263.4 70% 50.4%)"
                                stroke-width="2"
                            />
                        {/if}
                    </svg>

                    <!-- Tooltip -->
                    {#if hoverIndex !== -1 && points[hoverIndex]}
                        <div
                            class="absolute bg-slate-900 border border-slate-700 p-2 rounded shadow-lg text-xs pointer-events-none z-10"
                            style="left: {points[hoverIndex]
                                .x}px; top: 0; transform: translate(-50%, -100%); white-space: nowrap;"
                        >
                            <div class="font-bold mb-1 text-white">
                                {data[hoverIndex].date}
                            </div>
                            <div class="flex items-center gap-2">
                                <div
                                    class="w-2 h-2 rounded-full bg-[hsl(263.4_70%_50.4%)]"
                                ></div>
                                <span class="text-slate-200"
                                    >Filings: {data[hoverIndex].count}</span
                                >
                            </div>
                        </div>
                    {/if}
                {:else if width > 0}
                    <div
                        class="h-full w-full flex items-center justify-center text-slate-500"
                    >
                        No data available
                    </div>
                {/if}
            </div>
        </Card.Content>
    </Card.Root>
</div>
