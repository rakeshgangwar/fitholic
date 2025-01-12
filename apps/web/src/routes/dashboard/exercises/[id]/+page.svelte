<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import ExerciseView from '$lib/components/exercises/ExerciseView.svelte';
	import type { Exercise } from '$lib/types';
	import { onMount } from 'svelte';
	import { api } from '$lib/api';

	let exercise: Exercise | null = null;
	let loading = true;
	let error: string | null = null;

	onMount(async () => {
		try {
			const { data } = await api.get(`/exercises/${$page.params.id}`);
			exercise = data;
		} catch (e) {
			error = e instanceof Error ? e.message : 'An error occurred';
		} finally {
			loading = false;
		}
	});

	async function handleEdit() {
		await goto(`/dashboard/exercises/${$page.params.id}/edit`);
	}

	async function handleDelete() {
		if (!confirm('Are you sure you want to delete this exercise?')) return;

		try {
			await api.delete(`/exercises/${$page.params.id}`);
			await goto('/dashboard/exercises');
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to delete exercise';
		}
	}
</script>

<div class="container mx-auto px-4 py-8">
	{#if loading}
		<div class="flex justify-center items-center min-h-[400px]">
			<div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-gray-200 border-t-green-500"></div>
		</div>
	{:else if error}
		<div class="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
			<svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
			</svg>
			<h2 class="mt-4 text-lg font-medium text-red-800">Error Loading Exercise</h2>
			<p class="mt-2 text-sm text-red-600">{error}</p>
			<button
				class="mt-4 inline-flex items-center rounded-lg bg-red-100 px-4 py-2 text-sm font-medium text-red-700 hover:bg-red-200 transition-colors duration-200"
				on:click={() => goto('/dashboard/exercises')}
			>
				Return to Exercise List
			</button>
		</div>
	{:else if exercise}
		<ExerciseView {exercise} onEdit={handleEdit} onDelete={handleDelete} />
	{/if}
</div> 