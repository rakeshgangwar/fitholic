<script lang="ts">
  import { onMount } from 'svelte';
  import ExerciseList from '$lib/components/exercises/ExerciseList.svelte';
  import ExerciseForm from '$lib/components/exercises/ExerciseForm.svelte';
  import type { Exercise } from '$lib/types';
  import { api } from '$lib/api';
  import { 
    exercises_title,
    exercises_add,
    exercises_generate_ai,
    common_error_generic
  } from '$lib/paraglide/messages';
  import { Alert, AlertDescription } from '$lib/components/ui/alert';
  import AlertCircle from 'lucide-svelte/icons/alert-circle';
  import Brain from 'lucide-svelte/icons/brain';
  import Plus from 'lucide-svelte/icons/plus';
  import { cn } from '$lib/utils';
  import { buttonVariants } from '$lib/components/ui/button/button.svelte';

  let exercises: Exercise[] = [];
  let loading = false;
  let error: string | null = null;
  let showForm = false;
  let editingExercise: Exercise | null = null;
  let showAIForm = false;

  onMount(async () => {
    await loadExercises();
  });

  async function loadExercises() {
    try {
      loading = true;
      const response = await api.get('/exercises');
      exercises = response.data;
    } catch (err) {
      error = err instanceof Error ? err.message : common_error_generic();
    } finally {
      loading = false;
    }
  }

  function handleExerciseCreated() {
    loadExercises();
    showForm = false;
    editingExercise = null;
  }

  function handleExerciseDeleted() {
    loadExercises();
  }

  function startEditing(exercise: Exercise) {
    editingExercise = exercise;
    showForm = true;
  }
</script>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
  <header class="flex justify-between items-center mb-6">
    <h1 class="text-3xl font-bold tracking-tight">
      {exercises_title()}
    </h1>
    <div class="flex gap-4">
      <button
        type="button"
        class={cn(buttonVariants({ variant: "default" }))}
        on:click={() => {
          editingExercise = null;
          showForm = true;
          showAIForm = true;
        }}
      >
        <Brain class="h-4 w-4 mr-2" />
        {exercises_generate_ai()}
      </button>
      <!-- <button
        type="button"
        class={cn(buttonVariants({ variant: "default" }))}
        on:click={() => {
          editingExercise = null;
          showForm = true;
          showAIForm = false;
        }}
      >
        <Plus class="h-4 w-4 mr-2" />
        {exercises_add()}
      </button> -->
    </div>
  </header>

  {#if error}
    <Alert variant="destructive">
      <AlertCircle class="h-4 w-4" />
      <AlertDescription>{error}</AlertDescription>
    </Alert>
  {/if}

  <div class="mt-6">
    {#if showForm}
      <ExerciseForm
        exercise={editingExercise}
        showAIForm={showAIForm}
        on:exerciseCreated={handleExerciseCreated}
        on:cancel={() => {
          showForm = false;
          showAIForm = false;
          editingExercise = null;
        }}
      />
    {:else}
      <ExerciseList
        {exercises}
        {loading}
        on:edit={e => startEditing(e.detail)}
        on:delete={handleExerciseDeleted}
      />
    {/if}
  </div>
</div> 