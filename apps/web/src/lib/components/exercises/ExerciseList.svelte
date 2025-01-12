<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import type { Exercise } from '$lib/types';
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

	function getYouTubeId(url: string) {
		const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
		const match = url.match(regExp);
		return match && match[2].length === 11 ? match[2] : null;
	}
</script>

<div class="exercise-list">
	<div class="filters mb-6 grid grid-cols-1 gap-4 md:grid-cols-3">
		<div class="search-box">
			<label for="search" class="block text-sm font-medium text-gray-700">{exercises_search()}</label>
			<input
				type="text"
				id="search"
				bind:value={searchQuery}
				placeholder={exercises_search_placeholder()}
				class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
			/>
		</div>

		<div class="muscle-group-filter">
			<label for="muscle-group" class="block text-sm font-medium text-gray-700">{exercises_muscle_group()}</label>
			<select
				id="muscle-group"
				bind:value={selectedMuscleGroup}
				class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
			>
				<option value="">{exercises_muscle_group_all()}</option>
				{#each muscleGroups as { value, label }}
					<option {value}>{label}</option>
				{/each}
			</select>
		</div>

		<div class="difficulty-filter">
			<label for="difficulty" class="block text-sm font-medium text-gray-700">{exercises_difficulty()}</label>
			<select
				id="difficulty"
				bind:value={selectedDifficulty}
				class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
			>
				<option value="">{exercises_difficulty_all()}</option>
				{#each difficulties as { value, label }}
					<option {value}>{label}</option>
				{/each}
			</select>
		</div>
	</div>

	{#if loading}
		<div class="loading py-8 text-center">
			<p class="text-gray-500">{exercises_loading()}</p>
		</div>
	{:else if filteredExercises.length === 0}
		<div class="no-exercises py-8 text-center">
			<p class="text-gray-500">{exercises_no_results()}</p>
		</div>
	{:else}
		<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
			{#each filteredExercises as exercise}
				<div class="exercise-card overflow-hidden rounded-lg bg-white shadow-md">
					{#if exercise.video_url}
						<div class="relative" style="padding-top: 75%;">
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

					<div class="p-4">
						<div class="flex items-start justify-between">
							<h3 class="text-lg font-semibold text-gray-900">{exercise.name}</h3>
							<span class="difficulty-badge {exercise.difficulty}">
								{getLabel(exercise.difficulty, difficulties)}
							</span>
						</div>

						{#if exercise.description}
							<p class="mt-2 text-sm text-gray-600">{exercise.description}</p>
						{/if}

						<div class="mt-3">
							<h4 class="text-sm font-medium text-gray-700">{exercises_muscle_group()}:</h4>
							<div class="mt-1 flex flex-wrap gap-1">
								{#each exercise.muscle_groups as group}
									<span class="inline-flex items-center rounded bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-800">
										{getLabel(group, muscleGroups)}
									</span>
								{/each}
							</div>
						</div>

						<div class="mt-4 flex justify-end space-x-2">
							<button
								class="rounded bg-gray-100 px-3 py-1 text-sm text-gray-700 hover:bg-gray-200"
								on:click={() => dispatch('edit', exercise)}
							>
								{exercises_edit()}
							</button>
							<button
								class="rounded bg-red-100 px-3 py-1 text-sm text-red-700 hover:bg-red-200"
								on:click={() => dispatch('delete', exercise)}
							>
								{exercises_delete()}
							</button>
						</div>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>

<style>
	.difficulty-badge {
		@apply rounded px-2 py-0.5 text-xs font-medium;
	}

	.difficulty-badge.beginner {
		@apply bg-green-100 text-green-800;
	}

	.difficulty-badge.intermediate {
		@apply bg-yellow-100 text-yellow-800;
	}

	.difficulty-badge.advanced {
		@apply bg-red-100 text-red-800;
	}
</style>
