<!-- Profile Management Page -->
<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';
    import type { UserProfile } from '$lib/types';
    import { Button, Card } from 'flowbite-svelte';
    import PersonalInfo from '$lib/components/profile/PersonalInfo.svelte';
    import AppSettings from '$lib/components/profile/AppSettings.svelte';
    import Notifications from '$lib/components/profile/Notifications.svelte';
    import Privacy from '$lib/components/profile/Privacy.svelte';

    let profile: UserProfile | null = null;
    let activeTab: 'personal' | 'settings' | 'notifications' | 'privacy' = 'personal';
    let loading = true;
    let error: string | null = null;

    async function createProfile() {
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
            
            profile = await api.post('/profiles/me', defaultProfile);
            error = null;
        } catch (e: any) {
            error = e.message || 'Failed to create profile';
            throw e;
        }
    }

    onMount(async () => {
        try {
            loading = true;
            try {
                const response = await api.get('/profiles/me');
                profile = response.data;
            } catch (e: any) {
                if (e.response?.status === 404) {
                    // Profile doesn't exist, create one
                    await createProfile();
                } else {
                    throw e;
                }
            }
        } catch (e: any) {
            error = e.message || 'Failed to load profile';
        } finally {
            loading = false;
        }
    });

    const handleSaved = () => {
        // Refresh the profile data
        window.location.reload();
    };
</script>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="py-10">
        <header>
            <h1 class="text-3xl font-bold leading-tight text-gray-900">
                Profile Settings
            </h1>
        </header>

        {#if loading}
            <div class="flex justify-center items-center h-64">
                <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
            </div>
        {:else if error}
            <div class="mt-6 rounded-md bg-red-50 p-4">
                <div class="flex">
                    <div class="flex-shrink-0">
                        <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                        </svg>
                    </div>
                    <div class="ml-3">
                        <p class="text-sm font-medium text-red-800">{error}</p>
                    </div>
                </div>
                <Button color="primary" class="mt-4" on:click={() => window.location.reload()}>
                    Retry
                </Button>
            </div>
        {:else if profile}
            <div class="mt-6 border-b border-gray-200">
                <nav class="-mb-px flex space-x-8">
                    <button 
                        class="whitespace-nowrap pb-4 px-1 border-b-2 font-medium text-sm {activeTab === 'personal' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
                        on:click={() => activeTab = 'personal'}
                    >
                        Personal Info
                    </button>
                    <button 
                        class="whitespace-nowrap pb-4 px-1 border-b-2 font-medium text-sm {activeTab === 'settings' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
                        on:click={() => activeTab = 'settings'}
                    >
                        App Settings
                    </button>
                    <button 
                        class="whitespace-nowrap pb-4 px-1 border-b-2 font-medium text-sm {activeTab === 'notifications' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
                        on:click={() => activeTab = 'notifications'}
                    >
                        Notifications
                    </button>
                    <button 
                        class="whitespace-nowrap pb-4 px-1 border-b-2 font-medium text-sm {activeTab === 'privacy' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
                        on:click={() => activeTab = 'privacy'}
                    >
                        Privacy
                    </button>
                </nav>
            </div>

            <div class="mt-6">
                {#if activeTab === 'personal'}
                    <PersonalInfo {profile} on:saved={handleSaved} />
                {:else if activeTab === 'settings'}
                    <AppSettings {profile} on:saved={handleSaved} />
                {:else if activeTab === 'notifications'}
                    <Notifications {profile} on:saved={handleSaved} />
                {:else}
                    <Privacy {profile} on:saved={handleSaved} />
                {/if}
            </div>
        {/if}
    </div>
</div> 