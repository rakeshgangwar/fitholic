<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { buttonVariants } from '$lib/components/ui/button/button.svelte';
	import { Alert, AlertDescription } from '$lib/components/ui/alert';
	import { cn } from '$lib/utils';

	const dispatch = createEventDispatcher<{
		startListening: void;
		stopListening: void;
	}>();

	export let isListening = false;
	export let error: string | null = null;

	function toggleListening() {
		isListening = !isListening;
		dispatch(isListening ? 'startListening' : 'stopListening');
	}
</script>

<div class="voice-controls space-y-4">
	{#if error}
		<Alert variant="destructive">
			<AlertDescription>{error}</AlertDescription>
		</Alert>
	{/if}

	<div class="flex items-center space-x-4">
		<button
			type="button"
			class={cn(
				buttonVariants({ variant: isListening ? 'destructive' : 'default' }),
				'flex items-center space-x-2'
			)}
			on:click={toggleListening}
		>
			<svg
				xmlns="http://www.w3.org/2000/svg"
				viewBox="0 0 24 24"
				fill="none"
				stroke="currentColor"
				stroke-width="2"
				stroke-linecap="round"
				stroke-linejoin="round"
				class="h-5 w-5"
			>
				{#if isListening}
					<path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
					<path d="M19 10v2a7 7 0 0 1-14 0v-2" />
					<line x1="12" x2="12" y1="19" y2="22" />
				{:else}
					<path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
					<path d="M19 10v2a7 7 0 0 1-14 0v-2" />
				{/if}
			</svg>
			<span>{isListening ? 'Stop Listening' : 'Start Voice Assistant'}</span>
		</button>

		{#if isListening}
			<div class="flex items-center space-x-2">
				<span class="h-2 w-2 animate-pulse rounded-full bg-red-500"></span>
				<span class="text-muted-foreground text-sm">Listening...</span>
			</div>
		{/if}
	</div>
</div>

<style>
	.voice-controls {
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: 1rem;
	}

	.animate-pulse {
		animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
	}

	@keyframes pulse {
		0%,
		100% {
			opacity: 1;
		}
		50% {
			opacity: 0.5;
		}
	}
</style>
