<script>
    import * as Card from "$lib/components/ui/card";
    import * as Avatar from "$lib/components/ui/avatar";

    export let feedItems = [];
</script>

<Card.Root class="col-span-3">
    <Card.Header>
        <Card.Title>Recent Activity</Card.Title>
        <Card.Description>
            You made {feedItems.length} filings queries this month.
        </Card.Description>
    </Card.Header>
    <Card.Content>
        <div class="space-y-8">
            {#each feedItems as item}
                <div class="flex items-center">
                    <Avatar.Root class="h-9 w-9">
                        <Avatar.Fallback
                            >{item.ticker.substring(0, 2)}</Avatar.Fallback
                        >
                    </Avatar.Root>
                    <div class="ml-4 space-y-1">
                        <p class="text-sm font-medium leading-none">
                            {item.ticker}
                        </p>
                        <p class="text-sm text-muted-foreground">{item.form}</p>
                    </div>
                    <div class="ml-auto font-medium">{item.filingDate}</div>
                </div>
            {/each}
            {#if feedItems.length === 0}
                <div class="text-center text-muted-foreground text-sm">
                    No recent activity.
                </div>
            {/if}
        </div>
    </Card.Content>
</Card.Root>
