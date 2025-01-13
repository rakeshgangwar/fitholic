<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';
  import type { Exercise, WorkoutTemplate, TemplateExercise } from '$lib/types';
  import { api } from '$lib/api';

  const dispatch = createEventDispatcher<{
    templateCreated: void;
    templateDeleted: void;
    templateSelected: WorkoutTemplate;
  }>();

  export let templates: WorkoutTemplate[] = [];
  export let loading = false;
  
  let showForm = false;
  let editingSession: WorkoutTemplate | null = null;
  let exercises: Exercise[] = [];
  let selectedExercises: TemplateExercise[] = [];
  let name = '';
  let description = '';
  let difficulty = 'beginner';
  let error = '';

  onMount(async () => {
    try {
      const response = await api.get('/exercises');
      exercises = response.data;
    } catch (err) {
      error = 'Failed to load exercises';
    }
  });

  function resetForm() {
    name = '';
    description = '';
    difficulty = 'beginner';
    selectedExercises = [];
    editingSession = null;
    showForm = false;
  }

  function startEditing(session: WorkoutTemplate) {
    editingSession = session;
    name = session.name;
    description = session.description || '';
    difficulty = session.difficulty;
    selectedExercises = session.exercises;
    showForm = true;
  }

  async function handleSubmit() {
    if (!name || selectedExercises.length === 0) {
      error = 'Please fill in all required fields';
      return;
    }

    error = '';

    const workoutData = {
      name,
      description,
      difficulty,
      exercises: selectedExercises
    };

    try {
      if (editingSession) {
        await api.put(`/workouts/templates/${editingSession.template_id}`, workoutData);
      } else {
        await api.post('/workouts/templates', workoutData);
      }
      dispatch('templateCreated');
      resetForm();
    } catch (err) {
      error = 'Failed to save workout session';
    }
  }

  async function deleteSession(sessionId: string) {
    if (!confirm('Are you sure you want to delete this session?')) return;

    try {
      await api.delete(`/workouts/templates/${sessionId}`);
      dispatch('templateDeleted');
    } catch (err) {
      error = 'Failed to delete session';
    }
  }

  function addExercise(exercise: Exercise) {
    selectedExercises = [
      ...selectedExercises,
      {
        exercise_id: exercise.exercise_id,
        sets: 3,
        reps: 10,
        rest_time: 60
      }
    ];
  }

  function removeExercise(index: number) {
    selectedExercises = selectedExercises.filter((_, i) => i !== index);
  }

  function updateExercise(index: number, field: string, value: number) {
    selectedExercises = selectedExercises.map((exercise, i) => {
      if (i === index) {
        return { ...exercise, [field]: value };
      }
      return exercise;
    });
  }

  function handleExerciseSelect(event: Event) {
    const select = event.target as HTMLSelectElement;
    const selectedIndex = parseInt(select.value);
    if (!isNaN(selectedIndex)) {
      addExercise(exercises[selectedIndex]);
    }
    select.value = '';
  }

  function getDifficultyColor(difficulty: string): string {
    switch (difficulty) {
      case 'beginner':
        return 'bg-green-100 text-green-800';
      case 'intermediate':
        return 'bg-yellow-100 text-yellow-800';
      case 'advanced':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  }
</script>

{#if showForm}
  <div class="max-w-3xl mx-auto">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-xl font-semibold text-gray-900">
        {editingSession ? 'Edit' : 'Create'} Workout Session
      </h2>
      <button
        type="button"
        class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
        on:click={resetForm}
      >
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
        </svg>
        Back to Sessions
      </button>
    </div>

    {#if error}
      <div class="mb-6 rounded-md bg-red-50 p-4">
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

    <form on:submit|preventDefault={handleSubmit} class="space-y-6 bg-white rounded-xl shadow-sm px-6 py-8">
      <div>
        <label for="name" class="block text-sm font-medium text-gray-700">Session Name *</label>
        <input
          type="text"
          id="name"
          bind:value={name}
          required
          class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          placeholder="e.g., Full Body Workout"
        />
      </div>

      <div>
        <label for="description" class="block text-sm font-medium text-gray-700">Description</label>
        <textarea
          id="description"
          bind:value={description}
          rows="3"
          class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          placeholder="Describe your workout session..."
        />
      </div>

      <div>
        <label for="difficulty" class="block text-sm font-medium text-gray-700">Difficulty *</label>
        <select
          id="difficulty"
          bind:value={difficulty}
          class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
        >
          <option value="beginner">Beginner</option>
          <option value="intermediate">Intermediate</option>
          <option value="advanced">Advanced</option>
        </select>
      </div>

      <div>
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-medium text-gray-900">Exercises</h3>
          <div class="relative">
            <select
              on:change={handleExerciseSelect}
              class="block w-64 border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            >
              <option value="">Add Exercise...</option>
              {#each exercises as exercise, i}
                <option value={i}>{exercise.name}</option>
              {/each}
            </select>
          </div>
        </div>

        {#if selectedExercises.length > 0}
          <div class="space-y-4">
            {#each selectedExercises as exercise, i}
              <div class="bg-gray-50 rounded-lg p-4">
                <div class="flex justify-between items-start mb-4">
                  <h4 class="text-sm font-medium text-gray-900">
                    {exercises.find(e => e.exercise_id === exercise.exercise_id)?.name}
                  </h4>
                  <button
                    type="button"
                    class="inline-flex items-center p-1.5 border border-transparent rounded-full text-red-600 hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                    on:click={() => removeExercise(i)}
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                  </button>
                </div>
                <div class="grid grid-cols-3 gap-4">
                  <div>
                    <label class="block text-xs font-medium text-gray-500">Sets</label>
                    <input
                      type="number"
                      min="1"
                      bind:value={exercise.sets}
                      class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-1.5 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    />
                  </div>
                  <div>
                    <label class="block text-xs font-medium text-gray-500">Reps</label>
                    <input
                      type="number"
                      min="1"
                      bind:value={exercise.reps}
                      class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-1.5 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    />
                  </div>
                  <div>
                    <label class="block text-xs font-medium text-gray-500">Rest (sec)</label>
                    <input
                      type="number"
                      min="0"
                      step="5"
                      bind:value={exercise.rest_time}
                      class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-1.5 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    />
                  </div>
                </div>
              </div>
            {/each}
          </div>
        {:else}
          <div class="text-center py-12 bg-gray-50 rounded-lg">
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
            </svg>
            <p class="mt-2 text-sm text-gray-500">No exercises added yet</p>
          </div>
        {/if}
      </div>

      <div class="flex justify-end">
        <button
          type="submit"
          disabled={loading}
          class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
        >
          {loading ? 'Saving...' : editingSession ? 'Update Session' : 'Create Session'}
        </button>
      </div>
    </form>
  </div>
{:else}
  <div>
    {#if loading}
      <div class="flex justify-center items-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-gray-200 border-t-green-500"></div>
        <p class="mt-4 text-gray-500 text-sm">Loading sessions...</p>
      </div>
    {:else if templates.length === 0}
      <div class="text-center py-12 bg-white rounded-xl shadow-sm">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900">No workout sessions</h3>
        <p class="mt-1 text-sm text-gray-500">Get started by creating a new workout session.</p>
        <div class="mt-6">
          <button
            type="button"
            class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            on:click={() => showForm = true}
          >
            <svg class="w-5 h-5 mr-2 inline-block" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
            </svg>
            Create Session
          </button>
        </div>
      </div>
    {:else}
      <div class="flex justify-end mb-6">
        <button
          type="button"
          class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
          on:click={() => showForm = true}
        >
          <svg class="w-5 h-5 mr-2 inline-block" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
          </svg>
          Create Session
        </button>
      </div>

      <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {#each templates as session}
          <div class="bg-white overflow-hidden rounded-xl shadow-sm divide-y divide-gray-200 group hover:shadow-md transition-all duration-300">
            <div class="px-6 py-5">
              <div class="flex justify-between items-start">
                <div>
                  <h3 
                    class="text-lg font-semibold text-gray-900 group-hover:text-green-600 transition-colors duration-200 cursor-pointer"
                    on:click={() => window.location.href = `/dashboard/workouts/${session.template_id}`}
                    on:keypress={(e) => e.key === 'Enter' && (window.location.href = `/dashboard/workouts/${session.template_id}`)}
                    tabindex="0"
                    role="link"
                  >
                    {session.name}
                  </h3>
                  <p class="mt-1 text-sm text-gray-500 line-clamp-2">{session.description || 'No description'}</p>
                </div>
                <span class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium {getDifficultyColor(session.difficulty)}">
                  {session.difficulty}
                </span>
              </div>
            </div>
            <div class="px-6 py-4">
              <div class="flex items-center justify-between text-sm">
                <span class="text-gray-500">{session.exercises.length} exercises</span>
                <div class="flex space-x-2">
                  <button
                    type="button"
                    class="inline-flex items-center rounded-lg bg-gray-50 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-100 transition-colors duration-200"
                    on:click={() => startEditing(session)}
                  >
                    <svg class="w-3.5 h-3.5 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                    </svg>
                    Edit
                  </button>
                  <button
                    type="button"
                    class="inline-flex items-center rounded-lg bg-red-50 px-3 py-1.5 text-sm font-medium text-red-700 hover:bg-red-100 transition-colors duration-200"
                    on:click={() => deleteSession(session.template_id)}
                  >
                    <svg class="w-3.5 h-3.5 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                    </svg>
                    Delete
                  </button>
                </div>
              </div>
              <button
                class="mt-4 w-full inline-flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors duration-200"
                on:click={() => dispatch('templateSelected', session)}
              >
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"></path>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                Start Session
              </button>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </div>
{/if}

<style>
  .line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
</style> 