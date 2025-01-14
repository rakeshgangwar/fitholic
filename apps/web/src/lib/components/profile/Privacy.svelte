<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import type { UserProfile, UserProfileUpdate } from '$lib/types';
    import { api } from '$lib/api';
    import { toast } from 'svelte-sonner';

    import { Label } from '$lib/components/ui/label';
    import { Button } from '$lib/components/ui/button';
    import { Switch } from '$lib/components/ui/switch';
    import { RadioGroup, RadioGroupItem } from '$lib/components/ui/radio-group';
    import { Alert, AlertTitle, AlertDescription } from '$lib/components/ui/alert';
    import { AlertCircle } from 'lucide-svelte';

    export let profile: UserProfile;

    const dispatch = createEventDispatcher();
    let saving = false;
    let error: string | null = null;

    type VisibilityOption = 'public' | 'private' | 'friends';

    // Initialize with default values to avoid undefined
    let formData: UserProfileUpdate = {
        privacy_settings: {
            profile_visibility: (profile.privacy_settings?.profile_visibility || 'private') as VisibilityOption,
            share_workouts: profile.privacy_settings?.share_workouts ?? false,
            share_progress: profile.privacy_settings?.share_progress ?? false
        }
    };

    let profileVisibility: VisibilityOption = formData.privacy_settings?.profile_visibility || 'private';

    const visibilityOptions = [
        { value: 'public', label: 'Public - Anyone can view' },
        { value: 'friends', label: 'Friends Only - Only your connections can view' },
        { value: 'private', label: 'Private - Only you can view' }
    ] as const;

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

    $: if (formData.privacy_settings) {
        formData.privacy_settings.profile_visibility = profileVisibility;
    }

    async function handleSubmit(event: SubmitEvent) {
        event.preventDefault();
        try {
            saving = true;
            error = null;
            
            // Ensure profile_visibility is properly set before sending
            if (formData.privacy_settings) {
                formData.privacy_settings.profile_visibility = profileVisibility;
            }
            
            const response = await api.put('/profiles/me', formData);
            
            // Update the profile with the new settings
            if (response.data?.privacy_settings) {
                profile.privacy_settings = response.data.privacy_settings;
            }
            
            toast.success('Privacy settings saved successfully');
            dispatch('saved');
        } catch (e: any) {
            error = e.message || 'Failed to save privacy settings';
            toast.error(error);
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
        <!-- Section Header -->
        <div class="border-b pb-2">
            <h3 class="text-lg font-medium">Privacy Settings</h3>
            <p class="text-sm text-muted-foreground">Control who can see your profile and activities.</p>
        </div>

        <!-- Profile Visibility Section -->
        <div class="space-y-6">

            <div class="space-y-4">
                <RadioGroup 
                    value={profileVisibility}
                    onValueChange={(value: VisibilityOption) => {
                        profileVisibility = value;
                        if (formData.privacy_settings) {
                            formData.privacy_settings.profile_visibility = value;
                        }
                    }}
                    class="space-y-3"
                >
                    {#each visibilityOptions as option}
                        <div class="flex items-center space-x-2">
                            <RadioGroupItem value={option.value} id={option.value} />
                            <Label for={option.value} class="font-normal">
                                {option.label}
                            </Label>
                        </div>
                    {/each}
                </RadioGroup>
            </div>
        </div>

        <!-- Sharing Preferences Section -->
        <div class="space-y-6">

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
    </div>

    <div class="flex justify-end pt-4 border-t">
        <Button type="submit" disabled={saving}>
            {saving ? 'Saving...' : 'Save Changes'}
        </Button>
    </div>
</form> 