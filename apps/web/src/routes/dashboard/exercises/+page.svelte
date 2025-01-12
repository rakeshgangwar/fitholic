<script lang="ts">
  import { onMount } from 'svelte';
  import ExerciseList from '$lib/components/exercises/ExerciseList.svelte';
  import ExerciseForm from '$lib/components/exercises/ExerciseForm.svelte';
  import type { Exercise } from '$lib/types';
  import { api } from '$lib/api';
  import { 
    exercises_title,
    exercises_add,
    common_error_generic
  } from '$lib/paraglide/messages';

  let exercises: Exercise[] = [];
  let loading = false;
  let error: string | null = null;
  let showForm = false;
  let editingExercise: Exercise | null = null;

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

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
  <div class="py-10">
    <header class="flex justify-between items-center">
      <h1 class="text-3xl font-bold leading-tight text-gray-900">
        {exercises_title()}
      </h1>
      <button
        class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
        on:click={() => {
          editingExercise = null;
          showForm = true;
        }}
      >
        {exercises_add()}
      </button>
    </header>

    {#if error}
      <div class="mt-6 rounded-md bg-red-50 p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <p class="text-sm font-medium text-red-800">{error}</p>
          </div>
        </div>
      </div>
    {/if}

    <div class="mt-6">
      {#if showForm}
        <ExerciseForm
          exercise={editingExercise}
          on:exerciseCreated={handleExerciseCreated}
          on:cancel={() => {
            showForm = false;
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
</div> 