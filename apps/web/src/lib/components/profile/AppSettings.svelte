<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import type { UserProfile, UserProfileUpdate } from '$lib/types';
    import { api } from '$lib/api';
    import { theme } from '$lib/stores/theme';
    import { language } from '$lib/stores/language';
    import { units } from '$lib/stores/units';
    import { toast } from 'svelte-sonner';
    
    import { Label } from '$lib/components/ui/label';
    import { Button } from '$lib/components/ui/button';
    import { Switch } from '$lib/components/ui/switch';
    import { Alert, AlertTitle, AlertDescription } from '$lib/components/ui/alert';
    import { AlertCircle } from 'lucide-svelte';
    import { cn } from '$lib/utils';
    
    import { 
        settings_theme_options_light,
        settings_theme_options_dark,
        settings_theme_options_system,
        settings_language_options_en,
        settings_language_options_es,
        settings_language_options_fr,
        settings_language_options_de,
        settings_language_options_hi,
        settings_errors_save_theme_failed,
        settings_errors_save_language_failed,
        settings_errors_save_units_failed,
        settings_theme_label,
        settings_theme_description,
        settings_language_label,
        settings_language_description,
        settings_units_label,
        settings_units_metric,
        settings_units_imperial
    } from '$lib/paraglide/messages';

    export let profile: UserProfile;

    const dispatch = createEventDispatcher();
    let error: string | null = null;

    // Initialize stores with profile values
    $: {
        if (profile.theme && (profile.theme === 'light' || profile.theme === 'dark' || profile.theme === 'system')) {
            theme.set(profile.theme);
        }
        if (profile.language && (profile.language === 'en' || profile.language === 'es' || profile.language === 'fr' || profile.language === 'de' || profile.language === 'hi')) {
            language.set(profile.language);
        }
        if (profile.units && (profile.units === 'metric' || profile.units === 'imperial')) {
            units.set(profile.units);
        }
    }

    const themeOptions = [
        { value: 'light' as const, label: settings_theme_options_light() },
        { value: 'dark' as const, label: settings_theme_options_dark() },
        { value: 'system' as const, label: settings_theme_options_system() }
    ];

    const languageOptions = [
        { value: 'en' as const, label: settings_language_options_en() },
        { value: 'es' as const, label: settings_language_options_es() },
        { value: 'fr' as const, label: settings_language_options_fr() },
        { value: 'de' as const, label: settings_language_options_de() },
        { value: 'hi' as const, label: settings_language_options_hi() }
    ];

    // Update theme with immediate effect and persist to backend
    async function updateTheme(newTheme: 'light' | 'dark' | 'system') {
        console.log('Theme update called with:', newTheme);
        try {
            error = null;
            theme.set(newTheme);
            await api.put('/profiles/me', { theme: newTheme });
            dispatch('saved');
        } catch (e: any) {
            console.error('Error updating theme:', e);
            error = e.message || settings_errors_save_theme_failed();
            // Revert on error
            if (profile.theme && (profile.theme === 'light' || profile.theme === 'dark' || profile.theme === 'system')) {
                theme.set(profile.theme);
            }
        }
    }

    // Update language with immediate effect
    async function updateLanguage(newLanguage: 'en' | 'es' | 'fr' | 'de' | 'hi') {
        console.log('Language update called with:', newLanguage);
        try {
            error = null;
            const response = await api.put('/profiles/me', { language: newLanguage });
            console.log('Language update response:', response);
            language.set(newLanguage);
            toast.success('Language updated successfully');
            // Dispatch saved event with skipRefresh flag
            dispatch('saved');
        } catch (e: any) {
            console.error('Error updating language:', e);
            error = e.message || settings_errors_save_language_failed();
            toast.error(error);
            // Revert on error
            if (profile.language && (profile.language === 'en' || profile.language === 'es' || profile.language === 'fr' || profile.language === 'de' || profile.language === 'hi')) {
                language.set(profile.language);
            }
        }
    }

    // Toggle between metric and imperial units
    async function toggleUnits() {
        const newUnits = $units === 'metric' ? 'imperial' : 'metric';
        try {
            error = null;
            units.set(newUnits);
            await api.put('/profiles/me', { units: newUnits });
            dispatch('saved');
        } catch (e: any) {
            error = e.message || settings_errors_save_units_failed();
            if (profile.units && (profile.units === 'metric' || profile.units === 'imperial')) {
                units.set(profile.units);
            }
        }
    }
</script>

<div class="space-y-6">
    {#if error}
        <Alert variant="destructive">
            <AlertCircle class="h-4 w-4" />
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
        </Alert>
    {/if}

    <div class="space-y-6">
        <!-- Theme -->
        <div class="space-y-4">
            <div>
                <Label>{settings_theme_label()}</Label>
                <p class="text-sm text-muted-foreground">{settings_theme_description()}</p>
            </div>
            <div class="flex gap-4">
                {#each themeOptions as option}
                    <button
                        type="button"
                        class={cn(
                            "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 h-9 px-4 py-2",
                            $theme === option.value
                                ? "bg-primary text-primary-foreground hover:bg-primary/90"
                                : "border border-input bg-background hover:bg-accent hover:text-accent-foreground"
                        )}
                        on:click={() => updateTheme(option.value)}
                    >
                        {option.label}
                    </button>
                {/each}
            </div>
        </div>

        <!-- Language -->
        <div class="space-y-4">
            <div>
                <Label>{settings_language_label()}</Label>
                <p class="text-sm text-muted-foreground">{settings_language_description()}</p>
            </div>
            <div class="flex gap-4 flex-wrap">
                {#each languageOptions as option}
                    <button
                        type="button"
                        class={cn(
                            "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 h-9 px-4 py-2",
                            $language === option.value
                                ? "bg-primary text-primary-foreground hover:bg-primary/90"
                                : "border border-input bg-background hover:bg-accent hover:text-accent-foreground"
                        )}
                        on:click={() => updateLanguage(option.value)}
                    >
                        {option.label}
                    </button>
                {/each}
            </div>
        </div>

        <!-- Units Toggle -->
        <div class="flex items-center justify-between">
            <div class="space-y-1">
                <Label>{settings_units_label()}</Label>
                <p class="text-sm text-muted-foreground">
                    {$units === 'metric' ? settings_units_metric() : settings_units_imperial()}
                </p>
            </div>
            <Switch
                checked={$units === 'imperial'}
                on:change={toggleUnits}
            />
        </div>
    </div>
</div> 