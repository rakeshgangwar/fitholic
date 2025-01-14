<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import ExerciseView from '$lib/components/exercises/ExerciseView.svelte';
	import type { Exercise } from '$lib/types';
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import { buttonVariants } from '$lib/components/ui/button';
	import { ArrowLeft, AlertCircle, Loader2 } from 'lucide-svelte';
	import { Alert, AlertDescription, AlertTitle } from '$lib/components/ui/alert';
	import { cn } from '$lib/utils';

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

	function handleBack() {
		goto('/dashboard/exercises');
	}
</script>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
	<div class="mb-6">
		<button 
			type="button"
			class={cn(buttonVariants({ variant: 'ghost', size: 'sm' }), 'gap-2')}
			on:click={handleBack}
		>
			<ArrowLeft class="h-4 w-4" />
			Back to Exercises
		</button>
	</div>

	{#if loading}
		<div class="flex justify-center items-center min-h-[400px]">
			<Loader2 class="h-8 w-8 animate-spin text-primary" />
		</div>
	{:else if error}
		<Alert variant="destructive">
			<AlertCircle class="h-4 w-4" />
			<AlertTitle>Error Loading Exercise</AlertTitle>
			<AlertDescription>
				{error}
				<div class="mt-4">
					<button 
						type="button"
						class={buttonVariants({ variant: 'outline' })}
						on:click={handleBack}
					>
						Return to Exercise List
					</button>
				</div>
			</AlertDescription>
		</Alert>
	{:else if exercise}
		<ExerciseView {exercise} onEdit={handleEdit} onDelete={handleDelete} />
	{/if}
</div> 