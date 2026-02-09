<script>
    import { onMount, createEventDispatcher } from "svelte";
    import { Button } from "$lib/components/ui/button";

    const dispatch = createEventDispatcher();

    export let score = 50;
    export let sentiment = "Neutral";
    export let summary = "No analysis available.";
    export let ticker = "";

    // Determine color based on score
    $: color =
        score >= 60
            ? "text-green-400"
            : score <= 40
              ? "text-red-400"
              : "text-yellow-400";
    $: gaugeColor =
        score >= 60 ? "#4ade80" : score <= 40 ? "#f87171" : "#facc15";

    // Calculate rotation for gauge needle (-90 to 90 degrees)
    // 0 = -90deg, 50 = 0deg, 100 = 90deg
    $: rotation = (score / 100) * 180 - 90;
</script>

<div
    class="flex flex-col items-center p-6 bg-slate-900/50 rounded-xl border border-white/10"
>
    <h3 class="text-lg font-medium text-white mb-2">
        {ticker} Insider Confidence
    </h3>

    <!-- Gauge SVG -->
    <div class="relative w-48 h-24 mb-4 overflow-hidden">
        <svg viewBox="0 0 200 100" class="w-full h-full">
            <!-- Background Arc -->
            <path
                d="M 20 100 A 80 80 0 0 1 180 100"
                fill="none"
                stroke="#334155"
                stroke-width="20"
            />

            <!-- Sections (Optional, for visual guide) -->
            <!-- Bearish -->
            <path
                d="M 20 100 A 80 80 0 0 1 65.4 36.6"
                fill="none"
                stroke="#ef4444"
                stroke-width="20"
                stroke-opacity="0.2"
            />
            <!-- Bullish -->
            <path
                d="M 134.6 36.6 A 80 80 0 0 1 180 100"
                fill="none"
                stroke="#22c55e"
                stroke-width="20"
                stroke-opacity="0.2"
            />

            <!-- Needle -->
            <g
                class="transition-transform duration-1000 ease-out origin-[100px_100px]"
                style="transform: rotate({rotation}deg)"
            >
                <polygon points="100,100 90,100 100,20" fill={gaugeColor} />
            </g>

            <!-- Center Dot -->
            <circle cx="100" cy="100" r="10" fill="white" />
        </svg>
    </div>

    <div class="text-center">
        <div class="text-4xl font-bold {color} transition-colors duration-500">
            {score}
        </div>
        <div
            class="text-sm font-medium text-white uppercase tracking-wider mb-2"
        >
            {sentiment}
        </div>
        <p class="text-sm text-slate-400 max-w-sm mb-4">{summary}</p>

        <Button
            variant="outline"
            size="sm"
            class="text-xs border-white/20 hover:bg-white/10"
            onclick={() => dispatch("refresh")}
            disabled={false}
        >
            Refresh Confidence
        </Button>
    </div>
</div>
