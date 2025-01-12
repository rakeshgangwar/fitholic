import { writable, get } from 'svelte/store';
import { i18n } from '$lib/i18n';
import { page } from '$app/stores';
import { goto } from '$app/navigation';
import { browser } from '$app/environment';
import type { AvailableLanguageTag } from '$lib/paraglide/runtime';

type Language = 'en' | 'es' | 'fr' | 'de' | 'hi';

// Create a writable store for language
export const language = writable<Language>('en');

// Subscribe to language changes and apply them
language.subscribe((value) => {
    if (browser && typeof document !== 'undefined') {
        document.documentElement.lang = value;
        
        // Update Paraglide's language
        const currentPage = get(page);
        if (currentPage?.url?.pathname) {
            const canonicalPath = i18n.route(currentPage.url.pathname);
            const localisedPath = i18n.resolveRoute(canonicalPath, value as AvailableLanguageTag);
            goto(localisedPath);
        }
    }
}); 