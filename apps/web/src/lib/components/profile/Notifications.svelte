<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import type { UserProfile, UserProfileUpdate } from '$lib/types';
    import { api } from '$lib/api';

    import { Label } from '$lib/components/ui/label';
    import { Button } from '$lib/components/ui/button';
    import { Switch } from '$lib/components/ui/switch';
    import { Alert, AlertTitle, AlertDescription } from '$lib/components/ui/alert';
    import { AlertCircle } from 'lucide-svelte';

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

    async function handleSubmit(event: SubmitEvent) {
        event.preventDefault();
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

<form class="space-y-6" on:submit={handleSubmit}>
    {#if error}
        <Alert variant="destructive">
            <AlertCircle class="h-4 w-4" />
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
        </Alert>
    {/if}

    <div class="space-y-6">
        <!-- Workout Reminders -->
        <div class="flex items-center justify-between">
            <div class="space-y-1">
                <Label>Workout Reminders</Label>
                <p class="text-sm text-muted-foreground">
                    Get notified about your scheduled workouts
                </p>
            </div>
            <Switch
                checked={formData.notification_settings?.workout_reminders ?? false}
                on:change={(e) => updateNotificationSetting('workout_reminders', e.currentTarget.checked)}
            />
        </div>

        <!-- Progress Updates -->
        <div class="flex items-center justify-between">
            <div class="space-y-1">
                <Label>Progress Updates</Label>
                <p class="text-sm text-muted-foreground">
                    Receive updates about your fitness progress
                </p>
            </div>
            <Switch
                checked={formData.notification_settings?.progress_updates ?? false}
                on:change={(e) => updateNotificationSetting('progress_updates', e.currentTarget.checked)}
            />
        </div>

        <!-- Achievement Alerts -->
        <div class="flex items-center justify-between">
            <div class="space-y-1">
                <Label>Achievement Alerts</Label>
                <p class="text-sm text-muted-foreground">
                    Get notified when you reach fitness milestones
                </p>
            </div>
            <Switch
                checked={formData.notification_settings?.achievement_alerts ?? false}
                on:change={(e) => updateNotificationSetting('achievement_alerts', e.currentTarget.checked)}
            />
        </div>
    </div>

    <div class="flex justify-end">
        <Button type="submit" disabled={saving}>
            {saving ? 'Saving...' : 'Save Changes'}
        </Button>
    </div>
</form> 