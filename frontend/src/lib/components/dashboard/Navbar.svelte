<script>
    import {
        TrendingUp,
        Search,
        ChevronsUpDown,
        Check,
        PlusCircle,
    } from "lucide-svelte";
    import { Button } from "$lib/components/ui/button";
    import { Input } from "$lib/components/ui/input";
    import * as Avatar from "$lib/components/ui/avatar";
    import * as DropdownMenu from "$lib/components/ui/dropdown-menu";
    import { cn } from "$lib/utils";

    export let onTrack;

    let tickerInput = "";

    // Team Switcher State
    let open = false;
    let selectedTeam = {
        label: "Alicia Koch",
        value: "personal",
    };

    const groups = [
        {
            label: "Personal Account",
            teams: [
                {
                    label: "Alicia Koch",
                    value: "personal",
                },
            ],
        },
        {
            label: "Teams",
            teams: [
                {
                    label: "Acme Inc.",
                    value: "acme-inc",
                },
                {
                    label: "Monsters Inc.",
                    value: "monsters",
                },
            ],
        },
    ];

    async function handleKeydown(e) {
        if (e.key === "Enter") {
            await triggerTrack();
        }
    }

    async function triggerTrack() {
        if (onTrack && tickerInput) {
            await onTrack(tickerInput);
            tickerInput = "";
        }
    }
</script>

<header
    class="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50"
>
    <div
        class="flex h-16 items-center px-4 max-w-7xl mx-auto justify-between w-full"
    >
        <div class="mr-4 hidden md:flex">
            <DropdownMenu.Root bind:open>
                <DropdownMenu.Trigger asChild>
                    {#snippet children({ props })}
                        <Button
                            {...props}
                            variant="outline"
                            role="combobox"
                            aria-expanded={open}
                            aria-label="Select a team"
                            class="w-[200px] justify-between"
                        >
                            <Avatar.Root class="mr-2 h-5 w-5">
                                <Avatar.Image
                                    src={`https://avatar.vercel.sh/${selectedTeam.value}.png`}
                                    alt={selectedTeam.label}
                                    class="grayscale"
                                />
                                <Avatar.Fallback>SC</Avatar.Fallback>
                            </Avatar.Root>
                            {selectedTeam.label}
                            <ChevronsUpDown
                                class="ml-auto h-4 w-4 opacity-50"
                            />
                        </Button>
                    {/snippet}
                </DropdownMenu.Trigger>
                <DropdownMenu.Content class="w-[200px]">
                    <DropdownMenu.Group>
                        <DropdownMenu.Label>Personal Account</DropdownMenu.Label
                        >
                        <DropdownMenu.Item
                            on:click={() => {
                                selectedTeam = groups[0].teams[0];
                                open = false;
                            }}
                            class="text-sm"
                        >
                            <Avatar.Root class="mr-2 h-5 w-5">
                                <Avatar.Image
                                    src="https://avatar.vercel.sh/personal.png"
                                    alt="Personal Account"
                                    class="grayscale"
                                />
                                <Avatar.Fallback>SC</Avatar.Fallback>
                            </Avatar.Root>
                            Alicia Koch
                            <Check
                                class={cn(
                                    "ml-auto h-4 w-4",
                                    selectedTeam.value === "personal"
                                        ? "opacity-100"
                                        : "opacity-0",
                                )}
                            />
                        </DropdownMenu.Item>
                    </DropdownMenu.Group>
                    <DropdownMenu.Separator />
                    <DropdownMenu.Group>
                        <DropdownMenu.Label>Teams</DropdownMenu.Label>
                        {#each groups[1].teams as team}
                            <DropdownMenu.Item
                                on:click={() => {
                                    selectedTeam = team;
                                    open = false;
                                }}
                                class="text-sm"
                            >
                                <Avatar.Root class="mr-2 h-5 w-5">
                                    <Avatar.Image
                                        src={`https://avatar.vercel.sh/${team.value}.png`}
                                        alt={team.label}
                                        class="grayscale"
                                    />
                                    <Avatar.Fallback>SC</Avatar.Fallback>
                                </Avatar.Root>
                                {team.label}
                                <Check
                                    class={cn(
                                        "ml-auto h-4 w-4",
                                        selectedTeam.value === team.value
                                            ? "opacity-100"
                                            : "opacity-0",
                                    )}
                                />
                            </DropdownMenu.Item>
                        {/each}
                    </DropdownMenu.Group>
                    <DropdownMenu.Separator />
                    <DropdownMenu.Item>
                        <PlusCircle class="mr-2 h-5 w-5" />
                        Create Team
                    </DropdownMenu.Item>
                </DropdownMenu.Content>
            </DropdownMenu.Root>
        </div>

        <nav
            class="flex items-center gap-6 text-sm font-medium text-muted-foreground hidden md:flex mx-6"
        >
            <a
                href="#"
                class="text-foreground transition-colors hover:text-foreground"
                >Overview</a
            >
            <a href="#" class="transition-colors hover:text-foreground"
                >Analytics</a
            >
            <a href="#" class="transition-colors hover:text-foreground"
                >Reports</a
            >
        </nav>

        <div class="flex items-center gap-4">
            <div class="relative w-full max-w-sm hidden sm:block">
                <Search
                    class="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground"
                />
                <Input
                    bind:value={tickerInput}
                    type="search"
                    placeholder="Search..."
                    class="pl-8 w-[200px] lg:w-[300px]"
                    onkeydown={handleKeydown}
                />
            </div>

            <DropdownMenu.Root>
                <DropdownMenu.Trigger asChild>
                    {#snippet children({ props })}
                        <Button
                            {...props}
                            variant="ghost"
                            size="icon"
                            class="relative hover:bg-transparent"
                        >
                            <Avatar.Root class="h-8 w-8">
                                <Avatar.Fallback>ME</Avatar.Fallback>
                            </Avatar.Root>
                        </Button>
                    {/snippet}
                </DropdownMenu.Trigger>
                <DropdownMenu.Content align="end" class="w-56">
                    <DropdownMenu.Label>My Account</DropdownMenu.Label>
                    <DropdownMenu.Separator />
                    <DropdownMenu.Group>
                        <DropdownMenu.Item>Profile</DropdownMenu.Item>
                        <DropdownMenu.Item>Billing</DropdownMenu.Item>
                        <DropdownMenu.Item>Settings</DropdownMenu.Item>
                        <DropdownMenu.Item>New Team</DropdownMenu.Item>
                    </DropdownMenu.Group>
                    <DropdownMenu.Separator />
                    <DropdownMenu.Item>Log out</DropdownMenu.Item>
                </DropdownMenu.Content>
            </DropdownMenu.Root>
        </div>
    </div>
</header>

<style>
    /* Manual Flex Fix for Broken Tailwind */
    .container {
        display: flex;
        height: 3.5rem; /* h-14 */
        align-items: center;
        padding-left: 2rem;
        padding-right: 2rem;
        width: 100%;
        max-width: 80rem; /* max-w-7xl */
        margin-left: auto;
        margin-right: auto;
    }

    /* Left group (Team + Nav) */
    .container > div:first-child {
        display: none;
    }
    .container > nav {
        display: none;
    }

    /* Right group (Search + User) */
    .container > div:last-child {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-left: auto;
    }

    @media (min-width: 768px) {
        .container > div:first-child {
            display: flex;
            margin-right: 1.5rem;
        }
        .container > nav {
            display: flex;
            align-items: center;
            column-gap: 1.5rem; /* gap-6 */
        }
    }
</style>
