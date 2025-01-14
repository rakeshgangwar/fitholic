<!-- Profile Management Page -->
<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';
    import type { UserProfile } from '$lib/types';
    import type { AxiosResponse } from 'axios';
    import PersonalInfo from '$lib/components/profile/PersonalInfo.svelte';
    import AppSettings from '$lib/components/profile/AppSettings.svelte';
    import Notifications from '$lib/components/profile/Notifications.svelte';
    import Privacy from '$lib/components/profile/Privacy.svelte';
    import { settings_title, profile_personal_info_tab, profile_app_settings_tab, profile_notifications_tab, profile_privacy_tab, common_error_save_failed, common_error_generic, common_retry } from '$lib/paraglide/messages';
    
    import * as Tabs from '$lib/components/ui/tabs';
    import * as Alert from '$lib/components/ui/alert';
    import * as Card from '$lib/components/ui/card';
    import { Button } from '$lib/components/ui/button';
    import { AlertCircle } from 'lucide-svelte';
    import { Toaster } from '$lib/components/ui/sonner';

    let profile: UserProfile | null = null;
    let activeTab = 'settings';
    let loading = true;
    let error: string | null = null;

    const tabs = [
        { id: 'settings', title: profile_app_settings_tab() },
        { id: 'personal', title: profile_personal_info_tab() },
        { id: 'notifications', title: profile_notifications_tab() },
        { id: 'privacy', title: profile_privacy_tab() }
    ];

    async function createProfile(): Promise<UserProfile> {
        try {
            // Create a new profile with default settings
            const defaultProfile = {
                height: null,
                weight: null,
                date_of_birth: null,
                gender: null,
                fitness_goals: [],
                preferred_workout_duration: 60,
                preferred_workout_days: [],
                available_equipment: [],
                theme: "system",
                language: "en",
                units: "metric",
                notification_settings: {
                    workout_reminders: true,
                    progress_updates: true,
                    achievement_alerts: true
                },
                privacy_settings: {
                    profile_visibility: "private",
                    share_workouts: false,
                    share_progress: false
                }
            };
            
            const response = await api.post<UserProfile>('/profiles/me', defaultProfile);
            error = null;
            return response.data;
        } catch (e: any) {
            error = e.message || common_error_save_failed();
            throw e;
        }
    }

    onMount(async () => {
        try {
            loading = true;
            try {
                const response = await api.get<UserProfile>('/profiles/me');
                profile = response.data;
            } catch (e: any) {
                if (e.response?.status === 404) {
                    // Profile doesn't exist, create one
                    profile = await createProfile();
                } else {
                    throw e;
                }
            }
        } catch (e: any) {
            error = e.message || common_error_generic();
        } finally {
            loading = false;
        }
    });

    const handleSaved = async () => {
        // Refresh the profile data without page reload
        try {
            const response = await api.get<UserProfile>('/profiles/me');
            profile = response.data;
        } catch (e: any) {
            error = e.message || common_error_generic();
        }
    };
</script>

<Toaster richColors />

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="py-10">
        <header class="mb-6">
            <h1 class="text-3xl font-bold leading-tight">
                {settings_title()}
            </h1>
        </header>

        <Card.Root>
            <Card.Content>
                {#if loading}
                    <div class="flex items-center justify-center py-6">
                        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                    </div>
                {:else if error}
                    <Alert.Root class="mt-2" variant="destructive">
                        <AlertCircle class="h-4 w-4" />
                        <Alert.Title>Error</Alert.Title>
                        <Alert.Description>{error}</Alert.Description>
                        <Button 
                            variant="outline" 
                            class="mt-2" 
                            on:click={async () => {
                                try {
                                    loading = true;
                                    const response = await api.get<UserProfile>('/profiles/me');
                                    profile = response.data;
                                    error = null;
                                } catch (e: any) {
                                    error = e.message || common_error_generic();
                                } finally {
                                    loading = false;
                                }
                            }}
                        >
                            {common_retry()}
                        </Button>
                    </Alert.Root>
                {:else if profile}
                    <Tabs.Root value={activeTab} class="mt-2" onValueChange={(value: string) => activeTab = value}>
                        <div>
                            <div class="overflow-x-auto">
                                <Tabs.List class="inline-flex h-10 items-center justify-start px-1 w-full md:w-auto">
                                    {#each tabs as tab}
                                        <Tabs.Trigger 
                                            value={tab.id}
                                            class="inline-flex items-center justify-center whitespace-nowrap px-3 py-1.5 text-sm font-medium ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow-sm relative h-9 rounded-none border-b-2 border-b-transparent bg-transparent px-4 pb-3 pt-2 font-semibold text-muted-foreground shadow-none transition-none data-[state=active]:border-b-primary data-[state=active]:text-foreground data-[state=active]:shadow-none"
                                        >
                                            {tab.title}
                                        </Tabs.Trigger>
                                    {/each}
                                </Tabs.List>
                            </div>
                        </div>
                        <div class="mt-6">
                            
                            <Tabs.Content value="settings">
                                <Card.Root>
                                    <Card.Content class="pt-6">
                                        <AppSettings {profile} on:saved={handleSaved} />
                                    </Card.Content>
                                </Card.Root>
                            </Tabs.Content>
                            <Tabs.Content value="personal">
                                <Card.Root>
                                    <Card.Content class="pt-6">
                                        <PersonalInfo {profile} on:saved={handleSaved} />
                                    </Card.Content>
                                </Card.Root>
                            </Tabs.Content>
                            <Tabs.Content value="notifications">
                                <Card.Root>
                                    <Card.Content class="pt-6">
                                        <Notifications {profile} on:saved={handleSaved} />
                                    </Card.Content>
                                </Card.Root>
                            </Tabs.Content>
                            <Tabs.Content value="privacy">
                                <Card.Root>
                                    <Card.Content class="pt-6">
                                        <Privacy {profile} on:saved={handleSaved} />
                                    </Card.Content>
                                </Card.Root>
                            </Tabs.Content>
                        </div>
                    </Tabs.Root>
                {/if}
            </Card.Content>
        </Card.Root>
    </div>
</div> 