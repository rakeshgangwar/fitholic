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

	function getLabel(value: string, options: Array<{ value: string, label: string }>) {
		return options.find(opt => opt.value === value)?.label || value;
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

	async function viewExercise(exerciseId: string) {
		await goto(`/dashboard/exercises/${exerciseId}`);
	}
</script>

<div class="exercise-list p-6 bg-gray-50">
	<div class="filters mb-8">
		<div class="flex items-center justify-between mb-6">
			<div class="view-toggle inline-flex rounded-lg border border-gray-200 p-1">
				<button
					class="px-3 py-1.5 text-sm font-medium rounded-md transition-colors duration-200 {viewMode === 'card' ? 'bg-green-500 text-white' : 'text-gray-600 hover:text-gray-900'}"
					on:click={() => (viewMode = 'card')}
				>
					<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
						<path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
					</svg>
				</button>
				<button
					class="px-3 py-1.5 text-sm font-medium rounded-md transition-colors duration-200 {viewMode === 'list' ? 'bg-green-500 text-white' : 'text-gray-600 hover:text-gray-900'}"
					on:click={() => (viewMode = 'list')}
				>
					<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
						<path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd" />
					</svg>
				</button>
			</div>
		</div>
		<div class="grid grid-cols-1 gap-6 md:grid-cols-3 bg-white rounded-xl p-6 shadow-sm">
			<div class="search-box">
				<label for="search" class="block text-sm font-medium text-gray-700 mb-2">{exercises_search()}</label>
				<div class="relative">
					<input
						type="text"
						id="search"
						bind:value={searchQuery}
						placeholder={exercises_search_placeholder()}
						class="block w-full rounded-lg border-gray-200 pl-10 pr-4 py-3 text-sm focus:border-green-500 focus:ring-green-500 transition-colors duration-200"
					/>
					<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" viewBox="0 0 20 20" fill="currentColor">
						<path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
					</svg>
				</div>
			</div>

			<div class="muscle-group-filter">
				<label for="muscle-group" class="block text-sm font-medium text-gray-700 mb-2">{exercises_muscle_group()}</label>
				<div class="relative">
					<select
						id="muscle-group"
						bind:value={selectedMuscleGroup}
						class="block w-full rounded-lg border-gray-200 pl-4 pr-10 py-3 text-sm focus:border-green-500 focus:ring-green-500 appearance-none transition-colors duration-200"
					>
						<option value="">{exercises_muscle_group_all()}</option>
						{#each muscleGroups as { value, label }}
							<option {value}>{label}</option>
						{/each}
					</select>
					<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" viewBox="0 0 20 20" fill="currentColor">
						<path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
					</svg>
				</div>
			</div>

			<div class="difficulty-filter">
				<label for="difficulty" class="block text-sm font-medium text-gray-700 mb-2">{exercises_difficulty()}</label>
				<div class="relative">
					<select
						id="difficulty"
						bind:value={selectedDifficulty}
						class="block w-full rounded-lg border-gray-200 pl-4 pr-10 py-3 text-sm focus:border-green-500 focus:ring-green-500 appearance-none transition-colors duration-200"
					>
						<option value="">{exercises_difficulty_all()}</option>
						{#each difficulties as { value, label }}
							<option {value}>{label}</option>
						{/each}
					</select>
					<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" viewBox="0 0 20 20" fill="currentColor">
						<path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
					</svg>
				</div>
			</div>
		</div>
	</div>

	{#if loading}
		<div class="loading py-12 text-center">
			<div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-gray-200 border-t-green-500"></div>
			<p class="mt-4 text-gray-500 text-sm">{exercises_loading()}</p>
		</div>
	{:else if filteredExercises.length === 0}
		<div class="no-exercises py-12 text-center bg-white rounded-xl shadow-sm">
			<svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
			</svg>
			<p class="mt-4 text-gray-500 text-sm">{exercises_no_results()}</p>
		</div>
	{:else}
		{#if viewMode === 'card'}
			<div class="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3">
				{#each filteredExercises as exercise}
					<div class="exercise-card group bg-white rounded-xl shadow-sm hover:shadow-md transition-all duration-300">
						{#if exercise.video_url && getYouTubeId(exercise.video_url)}
							<div class="relative rounded-t-xl overflow-hidden" style="padding-top: 56.25%;">
								<iframe
									src={`https://www.youtube.com/embed/${getYouTubeId(exercise.video_url)}`}
									title={exercise.name}
									frameborder="0"
									allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
									allowfullscreen
									class="absolute top-0 left-0 w-full h-full"
								></iframe>
							</div>
						{/if}

						<div class="p-6">
							<div class="flex items-start justify-between mb-4">
								<h3 
									class="text-lg font-semibold text-gray-900 group-hover:text-green-600 transition-colors duration-200 cursor-pointer"
									on:click={() => viewExercise(exercise.exercise_id)}
									on:keypress={(e) => e.key === 'Enter' && viewExercise(exercise.exercise_id)}
									tabindex="0"
									role="link"
								>
									{exercise.name}
								</h3>
								<span class="difficulty-badge {exercise.difficulty || 'beginner'} ml-2">
									{getLabel(exercise.difficulty || 'beginner', difficulties)}
								</span>
							</div>

							{#if exercise.description}
								<p class="text-sm text-gray-600 line-clamp-2">{exercise.description}</p>
							{/if}

							<div class="mt-4">
								<h4 class="text-xs font-medium text-gray-500 uppercase tracking-wider">{exercises_muscle_group()}:</h4>
								<div class="mt-2 flex flex-wrap gap-2">
									{#each exercise.muscle_groups as group}
										<span class="inline-flex items-center rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-700">
											{getLabel(group, muscleGroups)}
										</span>
									{/each}
								</div>
							</div>

							<div class="mt-6 flex justify-end space-x-3">
								<button
									class="inline-flex items-center rounded-lg bg-gray-50 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 transition-colors duration-200"
									on:click={() => dispatch('edit', exercise)}
								>
									<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1.5" viewBox="0 0 20 20" fill="currentColor">
										<path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
									</svg>
									{exercises_edit()}
								</button>
								<button
									class="inline-flex items-center rounded-lg bg-red-50 px-4 py-2 text-sm font-medium text-red-700 hover:bg-red-100 transition-colors duration-200"
									on:click={() => dispatch('delete', exercise)}
								>
									<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1.5" viewBox="0 0 20 20" fill="currentColor">
										<path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
									</svg>
									{exercises_delete()}
								</button>
							</div>
						</div>
					</div>
				{/each}
			</div>
		{:else}
			<div class="bg-white rounded-xl shadow-sm overflow-hidden">
				<div class="overflow-x-auto">
					<table class="min-w-full divide-y divide-gray-200">
						<thead class="bg-gray-50">
							<tr>
								<th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Exercise</th>
								<th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Muscle Groups</th>
								<th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Difficulty</th>
								<th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
							</tr>
						</thead>
						<tbody class="bg-white divide-y divide-gray-200">
							{#each filteredExercises as exercise}
								<tr class="hover:bg-gray-50 transition-colors duration-200">
									<td class="px-6 py-4">
										<div class="flex items-center">
											{#if exercise.video_url && getYouTubeId(exercise.video_url)}
												<div class="flex-shrink-0 h-10 w-16 relative rounded overflow-hidden">
													<img
														src={`https://img.youtube.com/vi/${getYouTubeId(exercise.video_url)}/default.jpg`}
														alt={exercise.name}
														class="h-full w-full object-cover"
													/>
												</div>
											{/if}
											<div class="ml-4">
												<div 
													class="text-sm font-medium text-gray-900 hover:text-green-600 transition-colors duration-200 cursor-pointer"
													on:click={() => viewExercise(exercise.exercise_id)}
													on:keypress={(e) => e.key === 'Enter' && viewExercise(exercise.exercise_id)}
													tabindex="0"
													role="link"
												>
													{exercise.name}
												</div>
												{#if exercise.description}
													<div class="text-sm text-gray-500 line-clamp-1">{exercise.description}</div>
												{/if}
											</div>
										</div>
									</td>
									<td class="px-6 py-4">
										<div class="flex flex-wrap gap-1">
											{#each exercise.muscle_groups as group}
												<span class="inline-flex items-center rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-700">
													{getLabel(group, muscleGroups)}
												</span>
											{/each}
										</div>
									</td>
									<td class="px-6 py-4">
										<span class="difficulty-badge {exercise.difficulty || 'beginner'}">
											{getLabel(exercise.difficulty || 'beginner', difficulties)}
										</span>
									</td>
									<td class="px-6 py-4 text-right">
										<div class="space-x-2">
											<button
												class="inline-flex items-center rounded-lg bg-gray-50 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-100 transition-colors duration-200"
												on:click={() => dispatch('edit', exercise)}
											>
												<svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 mr-1" viewBox="0 0 20 20" fill="currentColor">
													<path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
												</svg>
												{exercises_edit()}
											</button>
											<button
												class="inline-flex items-center rounded-lg bg-red-50 px-3 py-1.5 text-sm font-medium text-red-700 hover:bg-red-100 transition-colors duration-200"
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
			</div>
		{/if}
	{/if}
</div>

<style>
	.difficulty-badge {
		@apply rounded-full px-3 py-1 text-xs font-medium;
	}

	.difficulty-badge.beginner {
		@apply bg-green-50 text-green-700;
	}

	.difficulty-badge.intermediate {
		@apply bg-yellow-50 text-yellow-700;
	}

	.difficulty-badge.advanced {
		@apply bg-red-50 text-red-700;
	}

	/* Add line clamp utility if not available in your Tailwind config */
	.line-clamp-2 {
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}

	/* Add styles for table view */
	:global(.exercise-list table) {
		border-collapse: separate;
		border-spacing: 0;
	}
</style>
