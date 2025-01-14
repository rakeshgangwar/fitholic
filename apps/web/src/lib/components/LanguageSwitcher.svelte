<script lang="ts">
    import { language } from '$lib/stores/language';
    import { api } from '$lib/api';
    import { onMount } from 'svelte';
    import { 
        settings_language_options_en,
        settings_language_options_es,
        settings_language_options_fr,
        settings_language_options_de,
        settings_language_options_hi
    } from '$lib/paraglide/messages';

    const languageOptions = [
        { value: 'en' as const, label: settings_language_options_en() },
        { value: 'es' as const, label: settings_language_options_es() },
        { value: 'fr' as const, label: settings_language_options_fr() },
        { value: 'de' as const, label: settings_language_options_de() },
        { value: 'hi' as const, label: settings_language_options_hi() }
    ];

    let loading = true;

    onMount(async () => {
        try {
            const response = await api.get('/profiles/me');
            const profile = response.data;
            if (profile.language && (profile.language === 'en' || profile.language === 'es' || profile.language === 'fr' || profile.language === 'de' || profile.language === 'hi')) {
                language.set(profile.language);
            }
        } catch (e) {
            console.error('Failed to fetch profile:', e);
        } finally {
            loading = false;
        }
    });

    async function handleLanguageChange(event: Event) {
        const select = event.target as HTMLSelectElement;
        const newLanguage = select.value as 'en' | 'es' | 'fr' | 'de' | 'hi';
        
        try {
            // Update the store first for immediate feedback
            language.set(newLanguage);
            // Then persist to backend
            await api.put('/profiles/me', { language: newLanguage });
        } catch (e) {
            console.error('Failed to update language:', e);
            // You might want to show an error toast here
        }
    }
</script>

<div class="relative inline-block text-left">
    <select
        class="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md bg-transparent"
        value={$language}
        on:change={handleLanguageChange}
        disabled={loading}
    >
        {#each languageOptions as option}
            <option value={option.value}>
                {option.label}
            </option>
        {/each}
    </select>
</div> 