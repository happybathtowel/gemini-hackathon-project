<script>
    import { Button } from "$lib/components/ui/button";
    import { createEventDispatcher } from "svelte";
    import { ChevronDown, ChevronRight } from "lucide-svelte";

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

    // Grouping Logic
    $: groupedFilings = (() => {
        const groups = {};
        allFilings.forEach((f) => {
            const key = `${f.ticker}-${f.form}-${f.filingDate}`;
            if (!groups[key]) {
                groups[key] = [];
            }
            groups[key].push(f);
        });
        // Convert back to array, preserving original sort order (roughly)
        // Since allFilings is sorted by date desc, we can just iterate keys
        // But keys iteration order isn't guaranteed. Better to rely on first appearance.
        const result = [];
        const seenKeys = new Set();
        allFilings.forEach((f) => {
            const key = `${f.ticker}-${f.form}-${f.filingDate}`;
            if (!seenKeys.has(key)) {
                seenKeys.add(key);
                result.push({
                    key,
                    ticker: f.ticker,
                    form: f.form,
                    filingDate: f.filingDate,
                    items: groups[key],
                });
            }
        });
        return result;
    })();

    let expandedGroups = new Set();

    function toggleGroup(key) {
        if (expandedGroups.has(key)) {
            expandedGroups.delete(key);
        } else {
            expandedGroups.add(key);
        }
        expandedGroups = expandedGroups; // trigger reactivity
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
                        class="h-12 px-4 align-middle font-medium text-muted-foreground w-[50px]"
                    ></th>
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
                {#each groupedFilings as group (group.key)}
                    {#if group.items.length > 1}
                        <!-- Group Header Row -->
                        <tr
                            class="border-b border-white/10 transition-colors hover:bg-muted/50 cursor-pointer bg-muted/20"
                            on:click={() => toggleGroup(group.key)}
                        >
                            <td class="p-4 align-middle text-center">
                                {#if expandedGroups.has(group.key)}
                                    <ChevronDown class="h-4 w-4" />
                                {:else}
                                    <ChevronRight class="h-4 w-4" />
                                {/if}
                            </td>
                            <td class="p-4 align-middle font-medium"
                                >{group.ticker}</td
                            >
                            <td class="p-4 align-middle">
                                {group.form}
                                <span class="text-muted-foreground ml-2"
                                    >({group.items.length} filings)</span
                                >
                            </td>
                            <td class="p-4 align-middle">{group.filingDate}</td>
                            <td class="p-4 align-middle text-right">
                                <Button
                                    variant="secondary"
                                    size="sm"
                                    class="h-7 text-xs"
                                    disabled={false}
                                    onclick={(e) => {
                                        e.stopPropagation();
                                        dispatch("analyzeBatch", group.items);
                                    }}
                                >
                                    Analyze Group
                                </Button>
                            </td>
                        </tr>
                        <!-- Expanded Items -->
                        {#if expandedGroups.has(group.key)}
                            {#each group.items as filing}
                                <tr
                                    class="border-b border-white/10 transition-colors hover:bg-muted/50 bg-black/20"
                                >
                                    <td class="p-4 align-middle"></td>
                                    <td class="p-4 align-middle opacity-50"
                                        >{filing.ticker}</td
                                    >
                                    <td class="p-4 align-middle">
                                        {filing.form}
                                        <span
                                            class="text-xs text-muted-foreground ml-2 font-mono"
                                        >
                                            {filing.accessionNumber}
                                        </span>
                                    </td>
                                    <td class="p-4 align-middle opacity-50"
                                        >{filing.filingDate}</td
                                    >
                                    <td class="p-4 align-middle text-right">
                                        <Button
                                            variant="outline"
                                            size="sm"
                                            class=""
                                            disabled={false}
                                            onclick={() =>
                                                handleAnalyze(filing)}
                                        >
                                            Analyze
                                        </Button>
                                    </td>
                                </tr>
                            {/each}
                        {/if}
                    {:else}
                        <!-- Single Item Row -->
                        {#each group.items as filing}
                            <tr
                                class="border-b border-white/10 transition-colors hover:bg-muted/50"
                            >
                                <td class="p-4 align-middle"></td>
                                <td class="p-4 align-middle font-medium"
                                    >{filing.ticker}</td
                                >
                                <td class="p-4 align-middle">
                                    {filing.form}
                                    <span
                                        class="text-xs text-muted-foreground ml-2 font-mono"
                                    >
                                        {filing.accessionNumber}
                                    </span>
                                </td>
                                <td class="p-4 align-middle"
                                    >{filing.filingDate}</td
                                >
                                <td class="p-4 align-middle text-right">
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        class=""
                                        disabled={false}
                                        onclick={() => handleAnalyze(filing)}
                                    >
                                        Analyze
                                    </Button>
                                </td>
                            </tr>
                        {/each}
                    {/if}
                {/each}
                {#if allFilings.length === 0}
                    <tr>
                        <td
                            colspan="5"
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
