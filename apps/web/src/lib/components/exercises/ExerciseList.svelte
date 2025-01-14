<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import type { Exercise } from '$lib/types';
	import { goto } from '$app/navigation';
	import {
		exercises_search,
		exercises_search_placeholder,
		exercises_muscle_group,
		exercises_muscle_group_all,
		exercises_difficulty,
		exercises_difficulty_all,
		exercises_loading,
		exercises_no_results,
		exercises_edit,
		exercises_delete,
		exercises_muscle_groups_chest,
		exercises_muscle_groups_back,
		exercises_muscle_groups_shoulders,
		exercises_muscle_groups_biceps,
		exercises_muscle_groups_triceps,
		exercises_muscle_groups_legs,
		exercises_muscle_groups_core,
		exercises_muscle_groups_full_body,
		exercises_muscle_groups_cardio,
		exercises_difficulty_beginner,
		exercises_difficulty_intermediate,
		exercises_difficulty_advanced
	} from '$lib/paraglide/messages';
	import { cn } from '$lib/utils';
	import * as Card from '$lib/components/ui/card';
	import { Select, SelectContent, SelectItem, SelectTrigger } from '$lib/components/ui/select';
	import { Input } from '$lib/components/ui/input';
	import { Badge, type BadgeVariant } from '$lib/components/ui/badge';
	import * as Dialog from '$lib/components/ui/dialog';
	import { buttonVariants } from '$lib/components/ui/button/button.svelte';

	export let exercises: Exercise[] = [];
	export let loading = false;

	const dispatch = createEventDispatcher<{
		edit: Exercise;
		delete: Exercise;
	}>();

	let searchQuery = '';
	let selectedMuscleGroup: string = '';
	let selectedDifficulty: string = '';
	let viewMode: 'card' | 'list' = 'card';
	let showVideoModal = false;
	let selectedVideoUrl: string | null = null;

	const muscleGroups = [
		{ value: 'chest', label: exercises_muscle_groups_chest() },
		{ value: 'back', label: exercises_muscle_groups_back() },
		{ value: 'shoulders', label: exercises_muscle_groups_shoulders() },
		{ value: 'biceps', label: exercises_muscle_groups_biceps() },
		{ value: 'triceps', label: exercises_muscle_groups_triceps() },
		{ value: 'legs', label: exercises_muscle_groups_legs() },
		{ value: 'core', label: exercises_muscle_groups_core() },
		{ value: 'full_body', label: exercises_muscle_groups_full_body() },
		{ value: 'cardio', label: exercises_muscle_groups_cardio() }
	];

	const difficulties = [
		{ value: 'beginner', label: exercises_difficulty_beginner() },
		{ value: 'intermediate', label: exercises_difficulty_intermediate() },
		{ value: 'advanced', label: exercises_difficulty_advanced() }
	];

	function getLabel(value: string | undefined, options: Array<{ value: string, label: string }>) {
		return options.find(opt => opt.value === value)?.label || value || '';
	}

	$: filteredExercises = exercises.filter((exercise) => {
		const matchesSearch =
			!searchQuery ||
			exercise.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
			exercise.description?.toLowerCase().includes(searchQuery.toLowerCase());

		const matchesMuscleGroup =
			!selectedMuscleGroup || exercise.muscle_groups.includes(selectedMuscleGroup);

		const matchesDifficulty = !selectedDifficulty || exercise.difficulty === selectedDifficulty;

		return matchesSearch && matchesMuscleGroup && matchesDifficulty;
	});

	function getYouTubeId(url: string | undefined): string | null {
		if (!url) return null;
		const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
		const match = url.match(regExp);
		return match && match[2].length === 11 ? match[2] : null;
	}

	function getYouTubeThumbnailUrl(url: string | undefined, quality: 'default' | 'hqdefault' = 'default'): string {
		const id = getYouTubeId(url);
		return id ? `https://img.youtube.com/vi/${id}/${quality}.jpg` : '';
	}

	async function viewExercise(exerciseId: string) {
		await goto(`/dashboard/exercises/${exerciseId}`);
	}

	function openVideoModal(url: string) {
		selectedVideoUrl = url;
		showVideoModal = true;
	}

	function closeVideoModal() {
		showVideoModal = false;
		selectedVideoUrl = null;
	}

	function getDifficultyVariant(difficulty: string | undefined): BadgeVariant {
		switch (difficulty) {
			case 'beginner':
				return 'default';
			case 'intermediate':
				return 'secondary';
			case 'advanced':
				return 'destructive';
			default:
				return 'default';
		}
	}
</script>

<div class="bg-background">
	<div class="exercise-list p-6">
		<div class="filters mb-8">
			<div class="flex items-center justify-between mb-6">
				<div class="view-toggle inline-flex rounded-lg border p-1">
					<button
						type="button"
						class={cn(
							buttonVariants({ variant: viewMode === 'card' ? 'default' : 'ghost', size: 'sm' }),
							'px-3 py-1.5'
						)}
						on:click={() => (viewMode = 'card')}
					>
						<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
							<path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
						</svg>
					</button>
					<button
						type="button"
						class={cn(
							buttonVariants({ variant: viewMode === 'list' ? 'default' : 'ghost', size: 'sm' }),
							'px-3 py-1.5'
						)}
						on:click={() => (viewMode = 'list')}
					>
						<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
							<path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd" />
						</svg>
					</button>
				</div>
			</div>
			<Card.Root>
				<div class="grid grid-cols-1 gap-6 md:grid-cols-3 p-6">
					<div class="search-box">
						<label for="search" class="block text-sm font-medium text-muted-foreground mb-2">{exercises_search()}</label>
						<div class="relative">
							<Input
								type="text"
								id="search"
								bind:value={searchQuery}
								placeholder={exercises_search_placeholder()}
								class="pl-10"
							/>
							<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-muted-foreground absolute left-3 top-1/2 -translate-y-1/2" viewBox="0 0 20 20" fill="currentColor">
								<path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
							</svg>
						</div>
					</div>

					<div class="muscle-group-filter">
						<label for="muscle-group" class="block text-sm font-medium text-muted-foreground mb-2">{exercises_muscle_group()}</label>
						<Select bind:value={selectedMuscleGroup}>
							<SelectTrigger class="w-full" placeholder={exercises_muscle_group_all()}>
								{selectedMuscleGroup ? getLabel(selectedMuscleGroup, muscleGroups) : exercises_muscle_group_all()}
							</SelectTrigger>
							<SelectContent>
								<SelectItem value="">{exercises_muscle_group_all()}</SelectItem>
								{#each muscleGroups as { value, label }}
									<SelectItem {value}>{label}</SelectItem>
								{/each}
							</SelectContent>
						</Select>
					</div>

					<div class="difficulty-filter">
						<label for="difficulty" class="block text-sm font-medium text-muted-foreground mb-2">{exercises_difficulty()}</label>
						<Select bind:value={selectedDifficulty}>
							<SelectTrigger class="w-full" placeholder={exercises_difficulty_all()}>
								{selectedDifficulty ? getLabel(selectedDifficulty, difficulties) : exercises_difficulty_all()}
							</SelectTrigger>
							<SelectContent>
								<SelectItem value="">{exercises_difficulty_all()}</SelectItem>
								{#each difficulties as { value, label }}
									<SelectItem {value}>{label}</SelectItem>
								{/each}
							</SelectContent>
						</Select>
					</div>
				</div>
			</Card.Root>
		</div>

		{#if loading}
			<div class="loading py-12 text-center">
				<div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-muted border-t-primary"></div>
				<p class="mt-4 text-muted-foreground text-sm">{exercises_loading()}</p>
			</div>
		{:else if filteredExercises.length === 0}
			<Card.Root>
				<Card.Content class="py-12 text-center">
					<svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
					<p class="mt-4 text-muted-foreground text-sm">{exercises_no_results()}</p>
				</Card.Content>
			</Card.Root>
		{:else}
			<Dialog.Root bind:open={showVideoModal}>
				<Dialog.Portal>
					<Dialog.Overlay />
					<Dialog.Content class="sm:max-w-4xl">
						<div class="relative" style="padding-top: 56.25%;">
							{#if selectedVideoUrl}
								<iframe
									src={`https://www.youtube.com/embed/${getYouTubeId(selectedVideoUrl)}`}
									title="Exercise Video"
									frameborder="0"
									allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
									allowfullscreen
									class="absolute top-0 left-0 w-full h-full"
								></iframe>
							{/if}
						</div>
						<Dialog.Close />
					</Dialog.Content>
				</Dialog.Portal>
			</Dialog.Root>

			{#if viewMode === 'card'}
				<div class="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3">
					{#each filteredExercises as exercise}
						<Card.Root class="group">
							{#if exercise.video_url && getYouTubeId(exercise.video_url)}
								<div 
									class="relative rounded-t-xl overflow-hidden cursor-pointer" 
									style="padding-top: 56.25%;"
									on:click={() => exercise.video_url && openVideoModal(exercise.video_url)}
									on:keypress={(e) => e.key === 'Enter' && exercise.video_url && openVideoModal(exercise.video_url)}
									tabindex="0"
									role="button"
								>
									{#if exercise.video_url}
										<img
											src={getYouTubeThumbnailUrl(exercise.video_url, 'hqdefault')}
											alt={exercise.name}
											class="absolute top-0 left-0 w-full h-full object-cover"
										/>
									{/if}
									<div class="absolute inset-0 flex items-center justify-center bg-black bg-opacity-30 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
										<svg class="w-16 h-16 text-white" fill="currentColor" viewBox="0 0 24 24">
											<path d="M8 5v14l11-7z"/>
										</svg>
									</div>
								</div>
							{/if}

							<Card.Content class="p-6">
								<div class="flex items-start justify-between mb-4">
									<h3 
										class="text-lg font-semibold text-foreground hover:text-primary transition-colors duration-200 cursor-pointer"
										on:click={() => viewExercise(exercise.exercise_id)}
										on:keypress={(e) => e.key === 'Enter' && viewExercise(exercise.exercise_id)}
										tabindex="0"
										role="link"
									>
										{exercise.name}
									</h3>
									<Badge variant={getDifficultyVariant(exercise.difficulty)} class="ml-2">
										{getLabel(exercise.difficulty || 'beginner', difficulties)}
									</Badge>
								</div>

								{#if exercise.description}
									<p class="text-sm text-muted-foreground line-clamp-2">{exercise.description}</p>
								{/if}

								<div class="mt-4">
									<h4 class="text-xs font-medium text-muted-foreground uppercase tracking-wider">{exercises_muscle_group()}:</h4>
									<div class="mt-2 flex flex-wrap gap-2">
										{#each exercise.muscle_groups as group}
											<Badge variant="outline">
												{getLabel(group, muscleGroups)}
											</Badge>
										{/each}
									</div>
								</div>

								<div class="mt-6 flex justify-end space-x-3">
									<button
										type="button"
										class={cn(buttonVariants({ variant: 'outline', size: 'sm' }))}
										on:click={() => dispatch('edit', exercise)}
									>
										<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1.5" viewBox="0 0 20 20" fill="currentColor">
											<path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
										</svg>
										{exercises_edit()}
									</button>
									<button
										type="button"
										class={cn(buttonVariants({ variant: 'destructive', size: 'sm' }))}
										on:click={() => dispatch('delete', exercise)}
									>
										<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1.5" viewBox="0 0 20 20" fill="currentColor">
											<path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
										</svg>
										{exercises_delete()}
									</button>
								</div>
							</Card.Content>
						</Card.Root>
					{/each}
				</div>
			{:else}
				<Card.Root>
					<div class="overflow-x-auto">
						<table class="w-full">
							<thead class="bg-muted">
								<tr>
									<th class="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Exercise</th>
									<th class="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Muscle Groups</th>
									<th class="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Difficulty</th>
									<th class="h-12 px-4 text-right align-middle font-medium text-muted-foreground">Actions</th>
								</tr>
							</thead>
							<tbody>
								{#each filteredExercises as exercise}
									<tr class="border-t hover:bg-muted/50">
										<td class="p-4">
											<div class="flex items-center">
												{#if exercise.video_url && getYouTubeId(exercise.video_url)}
													<div 
														class="flex-shrink-0 h-10 w-16 relative rounded overflow-hidden cursor-pointer group"
														on:click={() => exercise.video_url && openVideoModal(exercise.video_url)}
														on:keypress={(e) => e.key === 'Enter' && exercise.video_url && openVideoModal(exercise.video_url)}
														tabindex="0"
														role="button"
													>
														{#if exercise.video_url}
															<img
																src={getYouTubeThumbnailUrl(exercise.video_url)}
																alt={exercise.name}
																class="h-full w-full object-cover"
															/>
														{/if}
														<div class="absolute inset-0 flex items-center justify-center bg-black bg-opacity-30 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
															<svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
																<path d="M8 5v14l11-7z"/>
															</svg>
														</div>
													</div>
												{/if}
												<div class="ml-4">
													<div 
														class="text-sm font-medium text-foreground hover:text-primary cursor-pointer"
														on:click={() => viewExercise(exercise.exercise_id)}
														on:keypress={(e) => e.key === 'Enter' && viewExercise(exercise.exercise_id)}
														tabindex="0"
														role="link"
													>
														{exercise.name}
													</div>
													{#if exercise.description}
														<div class="text-sm text-muted-foreground line-clamp-1">{exercise.description}</div>
													{/if}
												</div>
											</div>
										</td>
										<td class="p-4">
											<div class="flex flex-wrap gap-1">
												{#each exercise.muscle_groups as group}
													<Badge variant="outline">
														{getLabel(group, muscleGroups)}
													</Badge>
												{/each}
											</div>
										</td>
										<td class="p-4">
											<Badge variant={getDifficultyVariant(exercise.difficulty)}>
												{getLabel(exercise.difficulty || 'beginner', difficulties)}
											</Badge>
										</td>
										<td class="p-4 text-right">
											<div class="space-x-2">
												<button
													type="button"
													class={cn(buttonVariants({ variant: 'outline', size: 'sm' }))}
													on:click={() => dispatch('edit', exercise)}
												>
													<svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 mr-1" viewBox="0 0 20 20" fill="currentColor">
														<path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
													</svg>
													{exercises_edit()}
												</button>
												<button
													type="button"
													class={cn(buttonVariants({ variant: 'destructive', size: 'sm' }))}
													on:click={() => dispatch('delete', exercise)}
												>
													<svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 mr-1" viewBox="0 0 20 20" fill="currentColor">
														<path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
													</svg>
													{exercises_delete()}
												</button>
											</div>
										</td>
									</tr>
								{/each}
							</tbody>
						</table>
					</div>
				</Card.Root>
			{/if}
		{/if}
	</div>
</div>

<style>
	/* Add line clamp utility if not available in your Tailwind config */
	.line-clamp-2 {
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}
</style>
