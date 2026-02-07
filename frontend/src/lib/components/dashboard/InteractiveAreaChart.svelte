<script>
    import { onMount } from "svelte";
    import * as Card from "$lib/components/ui/card";
    import { Button } from "$lib/components/ui/button";

    // Chart Data (Copied from reference)
    const rawData = [
        { date: "2024-04-01", desktop: 222, mobile: 150 },
        { date: "2024-04-02", desktop: 97, mobile: 180 },
        { date: "2024-04-03", desktop: 167, mobile: 120 },
        { date: "2024-04-04", desktop: 242, mobile: 260 },
        { date: "2024-04-05", desktop: 373, mobile: 290 },
        { date: "2024-04-06", desktop: 301, mobile: 340 },
        { date: "2024-04-07", desktop: 245, mobile: 180 },
        { date: "2024-04-08", desktop: 409, mobile: 320 },
        { date: "2024-04-09", desktop: 59, mobile: 110 },
        { date: "2024-04-10", desktop: 261, mobile: 190 },
        { date: "2024-04-11", desktop: 327, mobile: 350 },
        { date: "2024-04-12", desktop: 292, mobile: 210 },
        { date: "2024-04-13", desktop: 342, mobile: 380 },
        { date: "2024-04-14", desktop: 137, mobile: 220 },
        { date: "2024-04-15", desktop: 120, mobile: 170 },
        { date: "2024-04-16", desktop: 138, mobile: 190 },
        { date: "2024-04-17", desktop: 446, mobile: 360 },
        { date: "2024-04-18", desktop: 364, mobile: 410 },
        { date: "2024-04-19", desktop: 243, mobile: 180 },
        { date: "2024-04-20", desktop: 89, mobile: 150 },
        { date: "2024-04-21", desktop: 137, mobile: 200 },
        { date: "2024-04-22", desktop: 224, mobile: 170 },
        { date: "2024-04-23", desktop: 138, mobile: 230 },
        { date: "2024-04-24", desktop: 387, mobile: 290 },
        { date: "2024-04-25", desktop: 215, mobile: 250 },
        { date: "2024-04-26", desktop: 75, mobile: 130 },
        { date: "2024-04-27", desktop: 383, mobile: 420 },
        { date: "2024-04-28", desktop: 122, mobile: 180 },
        { date: "2024-04-29", desktop: 315, mobile: 240 },
        { date: "2024-04-30", desktop: 454, mobile: 380 },
        { date: "2024-05-01", desktop: 165, mobile: 220 },
        { date: "2024-05-02", desktop: 293, mobile: 310 },
        { date: "2024-05-03", desktop: 247, mobile: 190 },
        { date: "2024-05-04", desktop: 385, mobile: 420 },
        { date: "2024-05-05", desktop: 481, mobile: 390 },
        { date: "2024-05-06", desktop: 498, mobile: 520 },
        { date: "2024-05-07", desktop: 388, mobile: 300 },
        { date: "2024-05-08", desktop: 149, mobile: 210 },
        { date: "2024-05-09", desktop: 227, mobile: 180 },
        { date: "2024-05-10", desktop: 293, mobile: 330 },
        { date: "2024-05-11", desktop: 335, mobile: 270 },
        { date: "2024-05-12", desktop: 197, mobile: 240 },
        { date: "2024-05-13", desktop: 197, mobile: 160 },
        { date: "2024-05-14", desktop: 448, mobile: 490 },
        { date: "2024-05-15", desktop: 473, mobile: 380 },
        { date: "2024-05-16", desktop: 338, mobile: 400 },
        { date: "2024-05-17", desktop: 499, mobile: 420 },
        { date: "2024-05-18", desktop: 315, mobile: 350 },
        { date: "2024-05-19", desktop: 235, mobile: 180 },
        { date: "2024-05-20", desktop: 177, mobile: 230 },
        { date: "2024-05-21", desktop: 82, mobile: 140 },
        { date: "2024-05-22", desktop: 81, mobile: 120 },
        { date: "2024-05-23", desktop: 252, mobile: 290 },
        { date: "2024-05-24", desktop: 294, mobile: 220 },
        { date: "2024-05-25", desktop: 201, mobile: 250 },
        { date: "2024-05-26", desktop: 213, mobile: 170 },
        { date: "2024-05-27", desktop: 420, mobile: 460 },
        { date: "2024-05-28", desktop: 233, mobile: 190 },
        { date: "2024-05-29", desktop: 78, mobile: 130 },
        { date: "2024-05-30", desktop: 340, mobile: 280 },
        { date: "2024-05-31", desktop: 178, mobile: 230 },
    ];

    let timeRange = "90d";
    let filteredData = [];
    let width = 0;
    let height = 250;
    let container;

    // Tooltip state
    let hoverIndex = -1;
    let tooltipX = 0;
    let tooltipY = 0;

    $: {
        const referenceDate = new Date("2024-05-30"); // Using last date of data roughly
        let daysToSubtract = 90;
        if (timeRange === "30d") daysToSubtract = 30;
        if (timeRange === "7d") daysToSubtract = 7;

        const startDate = new Date(referenceDate);
        startDate.setDate(startDate.getDate() - daysToSubtract);

        filteredData = rawData.filter((d) => new Date(d.date) >= startDate);
    }

    // Scaling helpers
    $: maxVal =
        Math.max(...filteredData.map((d) => d.desktop + d.mobile)) * 1.1;
    $: xStep = width / (filteredData.length - 1 || 1);

    $: pointsDesktop = filteredData.map((d, i) => {
        const x = i * xStep;
        // Stack: desktop on bottom (or top? Reference seems to stack)
        // Let's put desktop on bottom
        const y = height - (d.desktop / maxVal) * height;
        return { x, y, val: d.desktop };
    });

    $: pointsMobile = filteredData.map((d, i) => {
        const x = i * xStep;
        // Mobile stacked on top of desktop
        const yBase = height - (d.desktop / maxVal) * height;
        const y = yBase - (d.mobile / maxVal) * height;
        return { x, y, val: d.mobile, yBase };
    });

    // Path Generation (Straight lines for robustness)
    $: pathDesktop =
        `M 0 ${height} ` +
        pointsDesktop.map((p) => `L ${p.x} ${p.y}`).join(" ") +
        ` L ${width} ${height} Z`;

    // Mobile path needs to follow desktop baseline
    $: pathMobile =
        `M 0 ${pointsDesktop[0]?.y || height} ` +
        pointsMobile.map((p) => `L ${p.x} ${p.y}`).join(" ") +
        pointsDesktop
            .slice()
            .reverse()
            .map((p) => `L ${p.x} ${p.y}`)
            .join(" ") +
        " Z";

    function handleMouseMove(e) {
        if (!container) return;
        const rect = container.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const index = Math.min(
            Math.max(Math.round(x / xStep), 0),
            filteredData.length - 1,
        );

        hoverIndex = index;
        tooltipX = x; // Snap to mouse or point? Let's snap to point
        if (pointsMobile[index]) {
            tooltipX = pointsMobile[index].x;
        }
    }

    function handleMouseLeave() {
        hoverIndex = -1;
    }
</script>

<div
    class="visual-card w-full"
    style="background-color: #1e293b; border: 1px solid rgba(255,255,255,0.1); border-radius: 12px;"
>
    <Card.Root class="bg-transparent border-0 shadow-none">
        <Card.Header
            class="flex items-center gap-2 space-y-0 border-b border-white/5 py-5 sm:flex-row"
        >
            <div class="grid flex-1 gap-1 text-center sm:text-left">
                <Card.Title>Total Visitors</Card.Title>
                <Card.Description>
                    Showing total visitors for the last {timeRange === "90d"
                        ? "3 months"
                        : timeRange === "30d"
                          ? "30 days"
                          : "7 days"}
                </Card.Description>
            </div>

            <div class="flex items-center gap-2">
                <select
                    bind:value={timeRange}
                    class="h-9 w-[160px] rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 text-white"
                >
                    <option value="90d">Last 3 months</option>
                    <option value="30d">Last 30 days</option>
                    <option value="7d">Last 7 days</option>
                </select>
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
                {#if width > 0}
                    <svg
                        {width}
                        {height}
                        viewBox="0 0 {width} {height}"
                        class="overflow-visible"
                    >
                        <defs>
                            <linearGradient
                                id="fillDesktop"
                                x1="0"
                                y1="0"
                                x2="0"
                                y2="1"
                            >
                                <stop
                                    offset="5%"
                                    stop-color="hsl(217.2 91.2% 59.8%)"
                                    stop-opacity="0.8"
                                />
                                <stop
                                    offset="95%"
                                    stop-color="hsl(217.2 91.2% 59.8%)"
                                    stop-opacity="0.1"
                                />
                            </linearGradient>
                            <linearGradient
                                id="fillMobile"
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

                        <!-- Desktop Area (Bottom) -->
                        <path
                            d={pathDesktop}
                            fill="url(#fillDesktop)"
                            stroke="hsl(217.2 91.2% 59.8%)"
                            stroke-width="2"
                        />

                        <!-- Mobile Area (Top) -->
                        <path
                            d={pathMobile}
                            fill="url(#fillMobile)"
                            stroke="hsl(263.4 70% 50.4%)"
                            stroke-width="2"
                        />

                        <!-- Interactive Elements -->
                        {#if hoverIndex !== -1 && pointsMobile[hoverIndex]}
                            <line
                                x1={pointsMobile[hoverIndex].x}
                                y1={0}
                                x2={pointsMobile[hoverIndex].x}
                                y2={height}
                                stroke="white"
                                stroke-dasharray="4 4"
                                opacity="0.5"
                            />
                            <circle
                                cx={pointsMobile[hoverIndex].x}
                                cy={pointsMobile[hoverIndex].y}
                                r="4"
                                fill="white"
                                stroke="hsl(263.4 70% 50.4%)"
                                stroke-width="2"
                            />
                            <circle
                                cx={pointsDesktop[hoverIndex].x}
                                cy={pointsDesktop[hoverIndex].y}
                                r="4"
                                fill="white"
                                stroke="hsl(217.2 91.2% 59.8%)"
                                stroke-width="2"
                            />
                        {/if}
                    </svg>

                    <!-- Tooltip -->
                    {#if hoverIndex !== -1 && pointsMobile[hoverIndex]}
                        <div
                            class="absolute bg-background border border-border p-2 rounded shadow-lg text-xs pointer-events-none"
                            style="left: {pointsMobile[hoverIndex]
                                .x}px; top: 0; transform: translate(-50%, -100%); white-space: nowrap;"
                        >
                            <div class="font-bold mb-1">
                                {new Date(
                                    filteredData[hoverIndex].date,
                                ).toLocaleDateString()}
                            </div>
                            <div class="flex items-center gap-2">
                                <div
                                    class="w-2 h-2 rounded-full bg-[hsl(263.4_70%_50.4%)]"
                                ></div>
                                <span
                                    >Mobile: {filteredData[hoverIndex]
                                        .mobile}</span
                                >
                            </div>
                            <div class="flex items-center gap-2">
                                <div
                                    class="w-2 h-2 rounded-full bg-[hsl(217.2_91.2%_59.8%)]"
                                ></div>
                                <span
                                    >Desktop: {filteredData[hoverIndex]
                                        .desktop}</span
                                >
                            </div>
                        </div>
                    {/if}
                {/if}
            </div>
        </Card.Content>
    </Card.Root>
</div>
