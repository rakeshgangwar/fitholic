<script lang="ts">
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
		await authStore.init();
		initializing = false;
		isInitialized.set(true);
	});

	// Handle protected route navigation
	$: if (!initializing && browser && !publicPaths.includes($page.url.pathname) && !$authStore) {
		goto('/auth/login');
	}
</script>

{#if !initializing}
	<div class="min-h-screen bg-gray-100">
		<slot />
	</div>
{/if}
