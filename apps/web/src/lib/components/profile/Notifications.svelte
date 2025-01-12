<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import { Label } from 'flowbite-svelte';
    import Toggle from '$lib/components/common/Toggle.svelte';
    import type { UserProfile, UserProfileUpdate } from '$lib/types';
    import { api } from '$lib/api';

    // Define the NotificationSettings type
    interface NotificationSettings {
        workout_reminders: boolean;
        progress_updates: boolean;
        achievement_alerts: boolean;
    }

    export let profile: UserProfile;

    const dispatch = createEventDispatcher();
    let saving = false;
    let error: string | null = null;

    let formData: UserProfileUpdate = {
        notification_settings: {
            workout_reminders: profile.notification_settings?.workout_reminders ?? false,
            progress_updates: profile.notification_settings?.progress_updates ?? false,
            achievement_alerts: profile.notification_settings?.achievement_alerts ?? false
        }
    };

    const updateNotificationSetting = (setting: keyof NotificationSettings, value: boolean) => {
        if (!formData.notification_settings) {
            formData.notification_settings = {
                workout_reminders: false,
                progress_updates: false,
                achievement_alerts: false
            };
        }
        formData.notification_settings[setting] = value;
    };

    async function handleSubmit() {
        try {
            saving = true;
            error = null;
            await api.put('/profiles/me', formData);
            dispatch('saved');
        } catch (e: any) {
            error = e.message || 'Failed to save notification settings';
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
        <!-- Workout Reminders -->
        <div class="flex items-center justify-between">
            <div>
                <Label>Workout Reminders</Label>
                <p class="text-sm text-gray-500">
                    Get notified about your scheduled workouts
                </p>
            </div>
            <Toggle
                checked={formData.notification_settings?.workout_reminders ?? false}
                on:change={(e: CustomEvent<{ checked: boolean }>) => updateNotificationSetting('workout_reminders', e.detail.checked)}
            />
        </div>

        <!-- Progress Updates -->
        <div class="flex items-center justify-between">
            <div>
                <Label>Progress Updates</Label>
                <p class="text-sm text-gray-500">
                    Receive updates about your fitness progress
                </p>
            </div>
            <Toggle
                checked={formData.notification_settings?.progress_updates ?? false}
                on:change={(e: CustomEvent<{ checked: boolean }>) => updateNotificationSetting('progress_updates', e.detail.checked)}
            />
        </div>

        <!-- Achievement Alerts -->
        <div class="flex items-center justify-between">
            <div>
                <Label>Achievement Alerts</Label>
                <p class="text-sm text-gray-500">
                    Get notified when you reach fitness milestones
                </p>
            </div>
            <Toggle
                checked={formData.notification_settings?.achievement_alerts ?? false}
                on:change={(e: CustomEvent<{ checked: boolean }>) => updateNotificationSetting('achievement_alerts', e.detail.checked)}
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