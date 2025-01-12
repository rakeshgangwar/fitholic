<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import { Button, Label, Toggle } from 'flowbite-svelte';
    import type { UserProfile, UserProfileUpdate } from '$lib/types';
    import { api } from '$lib/api';
    import { theme } from '$lib/stores/theme';
    import { language } from '$lib/stores/language';
    import { units } from '$lib/stores/units';
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

    // Debounce function to prevent too many API calls
    function debounce(func: Function, wait: number) {
        let timeout: NodeJS.Timeout;
        return function executedFunction(...args: any[]) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Update theme with immediate effect and persist to backend
    const updateTheme = async (newTheme: 'light' | 'dark' | 'system') => {
        try {
            error = null;
            theme.set(newTheme);
            await api.put('/profiles/me', { theme: newTheme });
            dispatch('saved');
        } catch (e: any) {
            error = e.message || settings_errors_save_theme_failed();
            // Revert on error
            if (profile.theme && (profile.theme === 'light' || profile.theme === 'dark' || profile.theme === 'system')) {
                theme.set(profile.theme);
            }
        }
    };

    // Debounced theme update
    const debouncedThemeUpdate = debounce(updateTheme, 300);

    // Update language with immediate effect
    const updateLanguage = async (newLanguage: 'en' | 'es' | 'fr' | 'de') => {
        try {
            error = null;
            language.set(newLanguage);
            await api.put('/profiles/me', { language: newLanguage });
            dispatch('saved');
        } catch (e: any) {
            error = e.message || settings_errors_save_language_failed();
            if (profile.language && (profile.language === 'en' || profile.language === 'es' || profile.language === 'fr' || profile.language === 'de')) {
                language.set(profile.language);
            }
        }
    };

    // Toggle between metric and imperial units
    const toggleUnits = async () => {
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
    };
</script>

<div class="space-y-6">
    {#if error}
        <div class="text-red-500 mb-4 rounded-md bg-red-50 p-2">{error}</div>
    {/if}

    <div class="space-y-6">
        <!-- Theme -->
        <div class="flex flex-col gap-4">
            <Label>{settings_theme_label()}</Label>
            <div class="flex gap-4">
                {#each themeOptions as option}
                    <button
                        class="px-4 py-2 rounded-md {$theme === option.value ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}"
                        on:click={() => debouncedThemeUpdate(option.value)}
                    >
                        {option.label}
                    </button>
                {/each}
            </div>
            <p class="text-sm text-gray-500">{settings_theme_description()}</p>
        </div>

        <!-- Language -->
        <div class="flex flex-col gap-4">
            <Label>{settings_language_label()}</Label>
            <div class="flex gap-4 flex-wrap">
                {#each languageOptions as option}
                    <button
                        class="px-4 py-2 rounded-md {$language === option.value ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}"
                        on:click={() => updateLanguage(option.value)}
                    >
                        {option.label}
                    </button>
                {/each}
            </div>
            <p class="text-sm text-gray-500">{settings_language_description()}</p>
        </div>

        <!-- Units Toggle -->
        <div class="flex items-center justify-between">
            <div>
                <Label>{settings_units_label()}</Label>
                <p class="text-sm text-gray-500">
                    {$units === 'metric' ? settings_units_metric() : settings_units_imperial()}
                </p>
            </div>
            <Toggle
                checked={$units === 'imperial'}
                on:change={toggleUnits}
                class="w-20"
            >
                <div slot="offLabel">{settings_units_metric()}</div>
                <div slot="default">{$units === 'metric' ? settings_units_metric() : settings_units_imperial()}</div>
            </Toggle>
        </div>
    </div>
</div> 