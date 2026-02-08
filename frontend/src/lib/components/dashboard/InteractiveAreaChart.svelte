<script>
    import { onMount } from "svelte";
    import * as Card from "$lib/components/ui/card";
    import { Button } from "$lib/components/ui/button";

    export let series = []; // [{ name: "AAPL", data: [{date, value}], color: "#..." }]
    export let timeRange = "90d";
    export let label = "Filings";
    export let formatValue = (v) => v;

    // Chart Dimensions
    let width = 0;
    let height = 250;
    let container;

    // Tooltip state
    let hoverIndex = -1;
    let tooltipX = 0;
    let tooltipY = 0;

    // Chart Margins
    const marginTop = 10;
    const marginRight = 10;
    const marginBottom = 20;
    const marginLeft = 40;

    // Derived Dimensions
    $: innerWidth = Math.max(width - marginLeft - marginRight, 0);
    $: innerHeight = Math.max(height - marginTop - marginBottom, 0);

    // Scaling helpers
    // Reset maxVal calculation to check all series
    $: maxVal =
        Math.max(...series.flatMap((s) => s.data.map((d) => d.value)), 5) * 1.1;

    // Assume all series have same length/dates for now
    $: xStep = innerWidth / ((series[0]?.data.length || 1) - 1 || 1);

    // Prepare points for each series
    $: seriesPoints = series.map((s) => {
        return {
            name: s.name,
            color: s.color,
            points: s.data.map((d, i) => ({
                x: i * xStep,
                y: innerHeight - (d.value / maxVal) * innerHeight,
                val: d.value,
                date: d.date,
            })),
        };
    });

    // Generate paths for each series
    $: seriesPaths = seriesPoints.map((s) => {
        const linePath =
            s.points.length > 0
                ? `M 0 ${s.points[0].y} ` +
                  s.points.map((p) => `L ${p.x} ${p.y}`).join(" ")
                : "";

        // Area logic: close the path at the bottom
        const areaPath =
            `M 0 ${innerHeight} ` +
            s.points.map((p) => `L ${p.x} ${p.y}`).join(" ") +
            ` L ${innerWidth} ${innerHeight} Z`;

        return { ...s, linePath, areaPath };
    });

    // Axis Generation
    $: yTicks = [0, 0.25, 0.5, 0.75, 1].map((p) => p * maxVal);
    $: xTicksData =
        series[0]?.data.filter(
            (_, i) => i % Math.ceil((series[0]?.data.length || 10) / 6) === 0,
        ) || [];

    function handleMouseMove(e) {
        if (!container || series.length === 0) return;
        const rect = container.getBoundingClientRect();
        const x = e.clientX - rect.left - marginLeft;

        if (x < 0 || x > innerWidth) {
            hoverIndex = -1;
            return;
        }

        const dataLen = series[0].data.length;
        const index = Math.min(Math.round(x / xStep), dataLen - 1);

        hoverIndex = index;
        // Use the first series for X positioning
        if (seriesPoints[0]?.points[index]) {
            tooltipX = seriesPoints[0].points[index].x;
            // Y is tricky with multiple series, maybe just stick to top or follow one?
            // Let's just keep X alignment.
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
                <Card.Title>{label} Activity</Card.Title>
                <Card.Description>
                    Showing total filings for the last {timeRange === "90d"
                        ? "3 months"
                        : timeRange === "30d"
                          ? "30 days"
                          : "7 days"}
                </Card.Description>
            </div>
            <!-- Legend -->
            <div class="flex items-center gap-4 text-xs">
                {#each series as s}
                    <div class="flex items-center gap-1.5">
                        <div
                            class="w-2 h-2 rounded-full"
                            style="background-color: {s.color}"
                        ></div>
                        <span class="text-muted-foreground">{s.name}</span>
                    </div>
                {/each}
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
                {#if width > 0 && series.length > 0}
                    <svg
                        {width}
                        {height}
                        viewBox="0 0 {width} {height}"
                        class="overflow-visible"
                    >
                        <defs>
                            {#each series as s, i}
                                <linearGradient
                                    id="fillGradient-{i}"
                                    x1="0"
                                    y1="0"
                                    x2="0"
                                    y2="1"
                                >
                                    <stop
                                        offset="5%"
                                        stop-color={s.color}
                                        stop-opacity="0.3"
                                    />
                                    <stop
                                        offset="95%"
                                        stop-color={s.color}
                                        stop-opacity="0.05"
                                    />
                                </linearGradient>
                            {/each}
                        </defs>

                        <g transform="translate({marginLeft}, {marginTop})">
                            <!-- Y-Axis Grid & Labels -->
                            {#each yTicks as tick}
                                <line
                                    x1="0"
                                    y1={innerHeight -
                                        (tick / maxVal) * innerHeight}
                                    x2={innerWidth}
                                    y2={innerHeight -
                                        (tick / maxVal) * innerHeight}
                                    stroke="white"
                                    stroke-opacity="0.1"
                                />
                                <text
                                    x="-10"
                                    y={innerHeight -
                                        (tick / maxVal) * innerHeight}
                                    fill="white"
                                    opacity="0.5"
                                    font-size="10"
                                    text-anchor="end"
                                    dominant-baseline="middle"
                                >
                                    {formatValue(tick)}
                                </text>
                            {/each}

                            <!-- X-Axis Labels -->
                            {#each xTicksData as d, i}
                                {@const tickX =
                                    series[0].data.indexOf(d) * xStep}
                                <text
                                    x={tickX}
                                    y={innerHeight + 15}
                                    fill="white"
                                    opacity="0.5"
                                    font-size="10"
                                    text-anchor="middle"
                                >
                                    {d.date}
                                </text>
                            {/each}

                            <!-- Series Layers (Area then Line) -->
                            {#each seriesPaths as s, i}
                                <!-- Area -->
                                <path
                                    d={s.areaPath}
                                    fill="url(#fillGradient-{i})"
                                />
                                <!-- Line -->
                                <path
                                    d={s.linePath}
                                    fill="none"
                                    stroke={s.color}
                                    stroke-width="2"
                                />
                            {/each}

                            <!-- Interactive Elements -->
                            {#if hoverIndex !== -1 && seriesPoints[0]?.points[hoverIndex]}
                                <!-- Vertical Line -->
                                <line
                                    x1={seriesPoints[0].points[hoverIndex].x}
                                    y1={0}
                                    x2={seriesPoints[0].points[hoverIndex].x}
                                    y2={innerHeight}
                                    stroke="white"
                                    stroke-dasharray="4 4"
                                    opacity="0.5"
                                />
                                <!-- Dots for each series -->
                                {#each seriesPoints as s}
                                    {#if s.points[hoverIndex]}
                                        <circle
                                            cx={s.points[hoverIndex].x}
                                            cy={s.points[hoverIndex].y}
                                            r="4"
                                            fill="white"
                                            stroke={s.color}
                                            stroke-width="2"
                                        />
                                    {/if}
                                {/each}
                            {/if}
                        </g>
                    </svg>

                    <!-- Tooltip -->
                    {#if hoverIndex !== -1 && seriesPoints[0]?.points[hoverIndex]}
                        <div
                            class="absolute bg-slate-900 border border-slate-700 p-2 rounded shadow-lg text-xs pointer-events-none z-10"
                            style="left: {seriesPoints[0].points[hoverIndex].x +
                                marginLeft}px; top: 0; transform: translate(-50%, -100%); white-space: nowrap;"
                        >
                            <div
                                class="font-bold mb-1 text-white border-b border-white/10 pb-1"
                            >
                                {seriesPoints[0].points[hoverIndex].date}
                            </div>
                            <div class="flex flex-col gap-1">
                                {#each seriesPoints as s}
                                    {#if s.points[hoverIndex]}
                                        <div class="flex items-center gap-2">
                                            <div
                                                class="w-2 h-2 rounded-full"
                                                style="background-color: {s.color}"
                                            ></div>
                                            <span class="text-slate-300"
                                                >{s.name}:</span
                                            >
                                            <span class="text-white font-mono"
                                                >{formatValue(
                                                    s.points[hoverIndex].val,
                                                )}</span
                                            >
                                        </div>
                                    {/if}
                                {/each}
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
