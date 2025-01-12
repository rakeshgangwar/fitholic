<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import { Button, Label, Select } from 'flowbite-svelte';
    import type { UserProfile, UserProfileUpdate } from '$lib/types';
    import { api } from '$lib/api';

    export let profile: UserProfile;

    const dispatch = createEventDispatcher();
    let saving = false;
    let error: string | null = null;

    let formData: UserProfileUpdate = {
        theme: profile.theme || 'system',
        language: profile.language || 'en',
        units: profile.units || 'metric'
    };

    const themeOptions = [
        { value: 'light', label: 'Light' },
        { value: 'dark', label: 'Dark' },
        { value: 'system', label: 'System Default' }
    ];

    const languageOptions = [
        { value: 'en', label: 'English' },
        { value: 'es', label: 'Español' },
        { value: 'fr', label: 'Français' },
        { value: 'de', label: 'Deutsch' }
    ];

    const unitOptions = [
        { value: 'metric', label: 'Metric (kg, cm)' },
        { value: 'imperial', label: 'Imperial (lbs, inches)' }
    ];

    async function handleSubmit() {
        try {
            saving = true;
            error = null;
            await api.put('/profiles/me', formData);
            dispatch('saved');
        } catch (e: any) {
            error = e.message || 'Failed to save settings';
        } finally {
            saving = false;
        }
    }
</script>

<form on:submit|preventDefault={handleSubmit} class="space-y-6">
    {#if error}
        <div class="text-red-500 mb-4">{error}</div>
    {/if}

    <div class="space-y-4">
        <!-- Theme -->
        <div>
            <Label for="theme">Theme</Label>
            <select 
                id="theme" 
                bind:value={formData.theme}
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            >
                {#each themeOptions as option}
                    <option value={option.value}>{option.label}</option>
                {/each}
            </select>
            <p class="text-sm text-gray-500 mt-1">
                Choose your preferred app theme
            </p>
        </div>

        <!-- Language -->
        <div>
            <Label for="language">Language</Label>
            <select 
                id="language" 
                bind:value={formData.language}
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            >
                {#each languageOptions as option}
                    <option value={option.value}>{option.label}</option>
                {/each}
            </select>
            <p class="text-sm text-gray-500 mt-1">
                Select your preferred language
            </p>
        </div>

        <!-- Units -->
        <div>
            <Label for="units">Measurement Units</Label>
            <select 
                id="units" 
                bind:value={formData.units}
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            >
                {#each unitOptions as option}
                    <option value={option.value}>{option.label}</option>
                {/each}
            </select>
            <p class="text-sm text-gray-500 mt-1">
                Choose your preferred measurement system
            </p>
        </div>
    </div>

    <div class="flex justify-end mt-6">
        <button 
            type="submit" 
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            disabled={saving}
        >
            {saving ? 'Saving...' : 'Save Changes'}
        </button>
    </div>
</form> 