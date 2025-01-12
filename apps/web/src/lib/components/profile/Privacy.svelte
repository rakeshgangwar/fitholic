<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import { Button, Label, Select } from 'flowbite-svelte';
    import Toggle from '$lib/components/common/Toggle.svelte';
    import type { UserProfile, UserProfileUpdate } from '$lib/types';
    import { api } from '$lib/api';

    export let profile: UserProfile;

    const dispatch = createEventDispatcher();
    let saving = false;
    let error: string | null = null;

    // Initialize with default values to avoid undefined
    let formData: UserProfileUpdate = {
        privacy_settings: {
            profile_visibility: profile.privacy_settings?.profile_visibility ?? 'private',
            share_workouts: profile.privacy_settings?.share_workouts ?? false,
            share_progress: profile.privacy_settings?.share_progress ?? false
        }
    };

    const visibilityOptions = [
        { value: 'public', label: 'Public - Anyone can view' },
        { value: 'friends', label: 'Friends Only - Only your connections can view' },
        { value: 'private', label: 'Private - Only you can view' }
    ];

    // Ensure privacy_settings is always defined
    const updatePrivacySetting = (setting: 'share_workouts' | 'share_progress', value: boolean) => {
        if (!formData.privacy_settings) {
            formData.privacy_settings = {
                profile_visibility: 'private',
                share_workouts: false,
                share_progress: false
            };
        }
        formData.privacy_settings[setting] = value;
    };

    async function handleSubmit() {
        try {
            saving = true;
            error = null;
            await api.put('/profiles/me', formData);
            dispatch('saved');
        } catch (e: any) {
            error = e.message || 'Failed to save privacy settings';
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
        <!-- Profile Visibility -->
        <div>
            <Label for="visibility">Profile Visibility</Label>
            <select 
                id="visibility"
                value={formData.privacy_settings?.profile_visibility ?? 'private'}
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                on:change={(e) => {
                    if (formData.privacy_settings) {
                        formData.privacy_settings.profile_visibility = (e.target as HTMLSelectElement).value as 'public' | 'private' | 'friends';
                    }
                }}
            >
                {#each visibilityOptions as option}
                    <option value={option.value}>{option.label}</option>
                {/each}
            </select>
            <p class="text-sm text-gray-500 mt-1">
                Control who can view your profile information
            </p>
        </div>

        <!-- Share Workouts -->
        <div class="flex items-center justify-between">
            <div>
                <Label>Share Workouts</Label>
                <p class="text-sm text-gray-500">
                    Allow others to see your workout history
                </p>
            </div>
            <Toggle
                checked={formData.privacy_settings?.share_workouts ?? false}
                on:change={(e: CustomEvent<{ checked: boolean }>) => updatePrivacySetting('share_workouts', e.detail.checked)}
            />
        </div>

        <!-- Share Progress -->
        <div class="flex items-center justify-between">
            <div>
                <Label>Share Progress</Label>
                <p class="text-sm text-gray-500">
                    Allow others to see your fitness progress
                </p>
            </div>
            <Toggle
                checked={formData.privacy_settings?.share_progress ?? false}
                on:change={(e: CustomEvent<{ checked: boolean }>) => updatePrivacySetting('share_progress', e.detail.checked)}
            />
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