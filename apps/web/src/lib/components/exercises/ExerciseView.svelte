<script lang="ts">
	import type { Exercise } from '$lib/types';
	import {
		exercises_muscle_group,
		exercises_difficulty,
		exercises_form_instructions,
		exercises_form_equipment,
		exercises_form_video_url,
		exercises_form_description,
		exercises_edit,
		exercises_delete
	} from '$lib/paraglide/messages';

	export let exercise: Exercise;
	export let onEdit: () => void;
	export let onDelete: () => void;

	function getYouTubeId(url: string | undefined): string | null {
		if (!url) return null;
		const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
		const match = url.match(regExp);
		return match && match[2].length === 11 ? match[2] : null;
	}
</script>

<div class="bg-white rounded-xl shadow-sm overflow-hidden">
	<div class="p-6 md:p-8">
		<!-- Header Section -->
		<div class="flex items-start justify-between mb-6">
			<div>
				<h1 class="text-2xl font-bold text-gray-900 mb-2">{exercise.name}</h1>
				{#if exercise.description}
					<p class="text-gray-600">{exercise.description}</p>
				{/if}
			</div>
			<div class="flex space-x-3">
				<button
					class="inline-flex items-center rounded-lg bg-gray-50 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 transition-colors duration-200"
					on:click={onEdit}
				>
					<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1.5" viewBox="0 0 20 20" fill="currentColor">
						<path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
					</svg>
					{exercises_edit()}
				</button>
				<button
					class="inline-flex items-center rounded-lg bg-red-50 px-4 py-2 text-sm font-medium text-red-700 hover:bg-red-100 transition-colors duration-200"
					on:click={onDelete}
				>
					<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1.5" viewBox="0 0 20 20" fill="currentColor">
						<path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
					</svg>
					{exercises_delete()}
				</button>
			</div>
		</div>

		<!-- Info Grid -->
		<div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
			<!-- Muscle Groups -->
			<div class="bg-gray-50 rounded-lg p-4">
				<h2 class="text-sm font-medium text-gray-500 uppercase tracking-wider mb-3">
					{exercises_muscle_group()}
				</h2>
				<div class="flex flex-wrap gap-2">
					{#each exercise.muscle_groups as group}
						<span class="inline-flex items-center rounded-full bg-white px-3 py-1 text-sm font-medium text-gray-700 shadow-sm">
							{group}
						</span>
					{/each}
				</div>
			</div>

			<!-- Equipment -->
			<div class="bg-gray-50 rounded-lg p-4">
				<h2 class="text-sm font-medium text-gray-500 uppercase tracking-wider mb-3">
					{exercises_form_equipment()}
				</h2>
				<div class="flex flex-wrap gap-2">
					{#each exercise.equipment || [] as item}
						<span class="inline-flex items-center rounded-full bg-white px-3 py-1 text-sm font-medium text-gray-700 shadow-sm">
							{item}
						</span>
					{/each}
				</div>
			</div>
		</div>

		<!-- Instructions -->
		{#if exercise.instructions}
			<div class="mb-8">
				<h2 class="text-lg font-semibold text-gray-900 mb-4">{exercises_form_instructions()}</h2>
				<div class="prose prose-green max-w-none">
					<ol class="list-decimal list-inside space-y-3">
						{#each exercise.instructions.split('\n') as instruction}
							<li class="text-gray-600">{instruction}</li>
						{/each}
					</ol>
				</div>
			</div>
		{/if}

		<!-- Additional Info -->
		<div class="border-t border-gray-200 pt-6">
			<dl class="grid grid-cols-1 md:grid-cols-2 gap-4">
				<!-- Difficulty -->
				<div>
					<dt class="text-sm font-medium text-gray-500">{exercises_difficulty()}</dt>
					<dd class="mt-1">
						<span class="difficulty-badge {exercise.difficulty || 'beginner'}">
							{exercise.difficulty || 'beginner'}
						</span>
					</dd>
				</div>

				<!-- Video Link -->
				{#if exercise.video_url}
					<div>
						<dt class="text-sm font-medium text-gray-500">{exercises_form_video_url()}</dt>
						<dd class="mt-1">
							<a
								href={exercise.video_url}
								target="_blank"
								rel="noopener noreferrer"
								class="text-green-600 hover:text-green-700 hover:underline"
							>
								{exercises_form_video_url()}
							</a>
						</dd>
					</div>
				{/if}
			</dl>
		</div>
	</div>

	<!-- Video Section (Moved to bottom) -->
	{#if exercise.video_url && getYouTubeId(exercise.video_url)}
		<div class="relative w-full border-t border-gray-200" style="padding-top: 56.25%;">
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
</div>

<style>
	.difficulty-badge {
		@apply inline-flex items-center rounded-full px-3 py-1 text-sm font-medium;
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
</style> 