<script>
    import { Button } from "$lib/components/ui/button";
    import { createEventDispatcher } from "svelte";

    // We can accept onAnalyze as a prop or dispatch an event.
    // Dispatching is more idiomatic for events, but App.svelte seems to pass functions.
    // I'll support both for flexibility, but primary usage will be via onAnalyze prop if passed.
    export let allFilings = [];
    export let onAnalyze;

    const dispatch = createEventDispatcher();

    function handleAnalyze(filing) {
        if (onAnalyze) {
            onAnalyze(filing.url, filing.ticker, filing.form);
        } else {
            dispatch("analyze", filing);
        }
    }
</script>

<div class="rounded-md border border-white/10 bg-slate-800/50">
    <div class="relative w-full overflow-auto">
        <table class="w-full caption-bottom text-sm text-left">
            <thead class="[&_tr]:border-b [&_tr]:border-white/10">
                <tr
                    class="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted"
                >
                    <th
                        class="h-12 px-4 align-middle font-medium text-muted-foreground w-[100px]"
                        >Ticker</th
                    >
                    <th
                        class="h-12 px-4 align-middle font-medium text-muted-foreground"
                        >Form</th
                    >
                    <th
                        class="h-12 px-4 align-middle font-medium text-muted-foreground"
                        >Filing Date</th
                    >
                    <th
                        class="h-12 px-4 align-middle font-medium text-muted-foreground text-right"
                        >Action</th
                    >
                </tr>
            </thead>
            <tbody class="[&_tr:last-child]:border-0">
                {#each allFilings as filing}
                    <tr
                        class="border-b border-white/10 transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted"
                    >
                        <td class="p-4 align-middle font-medium"
                            >{filing.ticker}</td
                        >
                        <td class="p-4 align-middle">{filing.form}</td>
                        <td class="p-4 align-middle">{filing.filingDate}</td>
                        <td class="p-4 align-middle text-right">
                            <Button
                                variant="outline"
                                size="sm"
                                on:click={() => handleAnalyze(filing)}
                            >
                                Analyze
                            </Button>
                        </td>
                    </tr>
                {/each}
                {#if allFilings.length === 0}
                    <tr>
                        <td
                            colspan="4"
                            class="p-4 text-center text-muted-foreground"
                            >No reports available. Track a company to see
                            filings.</td
                        >
                    </tr>
                {/if}
            </tbody>
        </table>
    </div>
</div>
