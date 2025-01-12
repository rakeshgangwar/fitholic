<script lang="ts">
	import { i18n } from '$lib/i18n';
	import { ParaglideJS } from '@inlang/paraglide-sveltekit';
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/auth';
	import { page } from '$app/stores';
	import { writable } from 'svelte/store';
	import '../app.css';

	const publicPaths = ['/auth/login', '/auth/register'];
	const isInitialized = writable(false);
	let initializing = true;

	// Initialize auth state on mount
	onMount(async () => {
		try {
			if (browser) {
				const token = localStorage.getItem('token');
				if (!token) {
					authStore.clear();
					if (!publicPaths.includes($page.url.pathname)) {
						await goto('/auth/login');
					}
				} else {
					await authStore.init();
				}
			}
		} catch (error) {
			console.error('Auth initialization error:', error);
			authStore.clear();
			if (browser && !publicPaths.includes($page.url.pathname)) {
				await goto('/auth/login');
			}
		} finally {
			initializing = false;
			isInitialized.set(true);
		}
	});

	// Handle protected route navigation only after initialization
	$: if (!initializing && browser && !publicPaths.includes($page.url.pathname)) {
		if (!$authStore || !localStorage.getItem('token')) {
			goto('/auth/login');
		}
	}
</script>

<ParaglideJS {i18n}>
	{#if !initializing}
		<div class="min-h-screen bg-gray-100">
			<slot></slot>
		</div>
	{/if}
</ParaglideJS>
