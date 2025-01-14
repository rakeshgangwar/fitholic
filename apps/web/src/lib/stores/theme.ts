import { writable } from 'svelte/store';

// Create a writable store for theme
export const theme = writable<'light' | 'dark' | 'system'>('system');

// Subscribe to theme changes and apply them
theme.subscribe((value) => {
    if (typeof window !== 'undefined') {
        // Remove existing theme classes
        document.documentElement.classList.remove('light', 'dark');
        
        if (value === 'system') {
            // Check system preference
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            document.documentElement.classList.add(prefersDark ? 'dark' : 'light');
        } else {
            // Apply theme directly
            document.documentElement.classList.add(value);
        }
    }
}); 