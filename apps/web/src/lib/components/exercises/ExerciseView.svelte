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
	import { Pencil, Trash2 } from 'lucide-svelte';
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import { Badge } from '$lib/components/ui/badge';
	import { Separator } from '$lib/components/ui/separator';
	import { cn } from '$lib/utils';
	import { marked } from 'marked';

	export let exercise: Exercise;
	export let onEdit: () => void;
	export let onDelete: () => void;

	function getYouTubeId(url: string | undefined): string | null {
		if (!url) return null;
		const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
		const match = url.match(regExp);
		return match && match[2].length === 11 ? match[2] : null;
	}

	const difficultyVariants = {
		beginner: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
		intermediate: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300',
		advanced: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
	} as const;

	marked.setOptions({
		breaks: true,
		gfm: true,
		pedantic: false
	});

	$: instructionsHtml = exercise.instructions
		? marked.parse(
				exercise.instructions
					.replace(/\\n/g, '\n')
					.replace(/^(#+)\s*/gm, '$1 ')
					.replace(/\\r\\n|\\r|\\n/g, '\n')
			)
		: '';
</script>

<Card.Root class="overflow-hidden">
	<Card.Header class="p-6 md:p-8">
		<div class="flex items-start justify-between">
			<div>
				<Card.Title class="mb-2 text-2xl">{exercise.name}</Card.Title>
				{#if exercise.description}
					<Card.Description>{exercise.description}</Card.Description>
				{/if}
			</div>
			<div class="flex space-x-3">
				<Button variant="outline" size="sm" on:click={onEdit}>
					<Pencil class="mr-1.5 h-4 w-4" />
					{exercises_edit()}
				</Button>
				<Button variant="destructive" size="sm" on:click={onDelete}>
					<Trash2 class="mr-1.5 h-4 w-4" />
					{exercises_delete()}
				</Button>
			</div>
		</div>
	</Card.Header>

	<Card.Content class="p-6 pt-0 md:p-8">
		<!-- Video and Info Grid -->
		<div class="mb-8 grid grid-cols-1 gap-6 md:grid-cols-2">
			<!-- Video Section -->
			{#if exercise.video_url && getYouTubeId(exercise.video_url)}
				<div class="relative w-full" style="padding-top: 56.25%;">
					<iframe
						src={`https://www.youtube.com/embed/${getYouTubeId(exercise.video_url)}`}
						title={exercise.name}
						frameborder="0"
						allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
						allowfullscreen
						class="absolute left-0 top-0 h-full w-full rounded-lg"
					></iframe>
				</div>
			{:else}
				<div class="bg-muted flex h-full min-h-[200px] items-center justify-center rounded-lg">
					<p class="text-muted-foreground">No video available</p>
				</div>
			{/if}

			<!-- Info Section -->
			<div class="space-y-6">
				<!-- Muscle Groups -->
				<div class="bg-muted rounded-lg p-4">
					<h2 class="text-muted-foreground mb-3 text-sm font-medium uppercase tracking-wider">
						{exercises_muscle_group()}
					</h2>
					<div class="flex flex-wrap gap-2">
						{#each exercise.muscle_groups as group}
							<Badge variant="secondary">{group}</Badge>
						{/each}
					</div>
				</div>

				<!-- Equipment -->
				{#if exercise.equipment && exercise.equipment.length > 0}
					<div class="bg-muted rounded-lg p-4">
						<h2 class="text-muted-foreground mb-3 text-sm font-medium uppercase tracking-wider">
							{exercises_form_equipment()}
						</h2>
						<div class="flex flex-wrap gap-2">
							{#each exercise.equipment || [] as item}
								<Badge variant="secondary">{item}</Badge>
							{/each}
						</div>
					</div>
				{/if}

				<!-- Difficulty -->
				<div class="bg-muted rounded-lg p-4">
					<h2 class="text-muted-foreground mb-3 text-sm font-medium uppercase tracking-wider">
						{exercises_difficulty()}
					</h2>
					<Badge
						class={cn(
							difficultyVariants[
								exercise.difficulty || ('beginner' as keyof typeof difficultyVariants)
							]
						)}
					>
						{exercise.difficulty || 'beginner'}
					</Badge>
				</div>
			</div>
		</div>

		<Separator class="my-6" />

		<!-- Instructions -->
		{#if exercise.instructions}
			<div class="mb-8">
				<h2 class="mb-4 text-lg font-semibold">{exercises_form_instructions()}</h2>
				<div
					class="prose prose-green dark:prose-invert prose-headings:font-semibold prose-h1:text-2xl prose-h2:text-xl prose-h3:text-lg prose-p:my-3 prose-ul:my-3 prose-ol:my-3 max-w-none"
				>
					{@html instructionsHtml}
				</div>
			</div>
		{/if}
	</Card.Content>
</Card.Root>
