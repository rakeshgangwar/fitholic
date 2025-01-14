<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import type { UserProfile, UserProfileUpdate } from '$lib/types';
    import { api } from '$lib/api';

    import { Label } from '$lib/components/ui/label';
    import { Button } from '$lib/components/ui/button';
    import { Switch } from '$lib/components/ui/switch';
    import { Select, SelectTrigger, SelectContent, SelectItem } from '$lib/components/ui/select';
    import { Alert, AlertTitle, AlertDescription } from '$lib/components/ui/alert';
    import { AlertCircle } from 'lucide-svelte';

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

    let profileVisibility = formData.privacy_settings?.profile_visibility ?? 'private';
    $: if (formData.privacy_settings) {
        formData.privacy_settings.profile_visibility = profileVisibility;
    }

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

    async function handleSubmit(event: SubmitEvent) {
        event.preventDefault();
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

<form class="space-y-6" on:submit={handleSubmit}>
    {#if error}
        <Alert variant="destructive">
            <AlertCircle class="h-4 w-4" />
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
        </Alert>
    {/if}

    <div class="space-y-6">
        <!-- Profile Visibility -->
        <div class="space-y-2">
            <Label for="visibility">Profile Visibility</Label>
            <Select value={profileVisibility} onValueChange={(value: string) => profileVisibility = value as 'public' | 'private' | 'friends'}>
                <SelectTrigger class="w-full">
                    <span class="text-muted-foreground">{profileVisibility || 'Select visibility'}</span>
                </SelectTrigger>
                <SelectContent>
                    {#each visibilityOptions as option}
                        <SelectItem value={option.value}>{option.label}</SelectItem>
                    {/each}
                </SelectContent>
            </Select>
            <p class="text-sm text-muted-foreground">
                Control who can view your profile information
            </p>
        </div>

        <!-- Share Workouts -->
        <div class="flex items-center justify-between">
            <div class="space-y-1">
                <Label>Share Workouts</Label>
                <p class="text-sm text-muted-foreground">
                    Allow others to see your workout history
                </p>
            </div>
            <Switch
                checked={formData.privacy_settings?.share_workouts ?? false}
                onCheckedChange={(checked: boolean) => updatePrivacySetting('share_workouts', checked)}
            />
        </div>

        <!-- Share Progress -->
        <div class="flex items-center justify-between">
            <div class="space-y-1">
                <Label>Share Progress</Label>
                <p class="text-sm text-muted-foreground">
                    Allow others to see your fitness progress
                </p>
            </div>
            <Switch
                checked={formData.privacy_settings?.share_progress ?? false}
                onCheckedChange={(checked: boolean) => updatePrivacySetting('share_progress', checked)}
            />
        </div>
    </div>

    <div class="flex justify-end">
        <Button type="submit" disabled={saving}>
            {saving ? 'Saving...' : 'Save Changes'}
        </Button>
    </div>
</form> 