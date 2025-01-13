<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { api } from '$lib/api';
  import type { WorkoutTemplate, WorkoutLog, Exercise } from '$lib/types';

  let loading = {
    template: false,
    history: false,
    exercises: false
  };
  let error: string | null = null;
  let template: WorkoutTemplate | null = null;
  let history: WorkoutLog[] = [];
  let exercises: Record<string, Exercise> = {};
  let activeVideo: { url: string; title: string } | null = null;

  function getYouTubeId(url: string | undefined): string | null {
    if (!url) return null;
    const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
    const match = url.match(regExp);
    return match && match[2].length === 11 ? match[2] : null;
  }

  function openVideoPopup(url: string | undefined, title: string | undefined) {
    if (!url || !title) return;
    const videoId = getYouTubeId(url);
    if (videoId) {
      activeVideo = { 
        url: `https://www.youtube.com/embed/${videoId}?autoplay=1`, 
        title 
      };
    }
  }

  function closeVideoPopup() {
    activeVideo = null;
  }

  onMount(async () => {
    const workoutId = $page.params.id;
    await Promise.all([
      loadWorkoutTemplate(workoutId),
      loadWorkoutHistory(workoutId),
      loadExercises()
    ]);
  });

  async function loadWorkoutTemplate(id: string) {
    try {
      loading.template = true;
      const response = await api.get(`/workouts/templates/${id}`);
      template = response.data;
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to load workout';
    } finally {
      loading.template = false;
    }
  }

  async function loadWorkoutHistory(id: string) {
    try {
      loading.history = true;
      const response = await api.get(`/workouts/logs?template_id=${id}`);
      history = response.data;
    } catch (err) {
      console.error('Failed to load workout history:', err);
    } finally {
      loading.history = false;
    }
  }

  async function loadExercises() {
    try {
      loading.exercises = true;
      const response = await api.get('/exercises');
      exercises = response.data.reduce((acc: Record<string, Exercise>, exercise: Exercise) => {
        acc[exercise.exercise_id] = exercise;
        return acc;
      }, {});
    } catch (err) {
      console.error('Failed to load exercises:', err);
    } finally {
      loading.exercises = false;
    }
  }

  async function deleteWorkout() {
    if (!template || !confirm('Are you sure you want to delete this workout?')) return;

    try {
      await api.delete(`/workouts/templates/${template.template_id}`);
      window.location.href = '/dashboard/workouts';
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to delete workout';
    }
  }

  async function cloneWorkout() {
    if (!template) return;

    try {
      const response = await api.post('/workouts/templates', {
        ...template,
        name: `${template.name} (Copy)`,
        template_id: undefined
      });
      window.location.href = `/dashboard/workouts/${response.data.template_id}`;
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to clone workout';
    }
  }

  function startWorkout() {
    if (!template) return;
    window.location.href = `/dashboard/workouts?tab=log&template=${template.template_id}`;
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

  function formatDate(date: string): string {
    return new Date(date).toLocaleDateString();
  }

  function getLastCompletedDate(): string | null {
    if (history.length === 0) return null;
    return formatDate(history[0].created_at);
  }

  function getEstimatedDuration(): string {
    if (!template) return '0 min';
    const totalRestTime = template.exercises.reduce((acc, ex) => acc + (ex.rest_time || 0), 0);
    const totalExerciseTime = template.exercises.length * 2 * 60; // Assume 2 min per exercise
    const totalTime = Math.round((totalRestTime + totalExerciseTime) / 60);
    return `${totalTime} min`;
  }
</script>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
  {#if loading.template}
    <div class="flex justify-center items-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-gray-200 border-t-green-500"></div>
    </div>
  {:else if error}
    <div class="rounded-md bg-red-50 p-4">
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
  {:else if template}
    <!-- Header Section -->
    <div class="bg-white rounded-xl shadow-sm overflow-hidden">
      <div class="px-6 py-5">
        <div class="flex justify-between items-start">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">{template.name}</h1>
            {#if template.description}
              <p class="mt-2 text-gray-500">{template.description}</p>
            {/if}
          </div>
          <span class="inline-flex items-center rounded-full px-3 py-1 text-sm font-medium {getDifficultyColor(template.difficulty)}">
            {template.difficulty}
          </span>
        </div>

        <!-- Quick Stats -->
        <div class="mt-6 grid grid-cols-1 gap-5 sm:grid-cols-3">
          <div class="bg-gray-50 rounded-lg px-4 py-3">
            <dt class="text-sm font-medium text-gray-500">Exercises</dt>
            <dd class="mt-1 text-xl font-semibold text-gray-900">{template.exercises.length}</dd>
          </div>
          <div class="bg-gray-50 rounded-lg px-4 py-3">
            <dt class="text-sm font-medium text-gray-500">Estimated Duration</dt>
            <dd class="mt-1 text-xl font-semibold text-gray-900">{getEstimatedDuration()}</dd>
          </div>
          <div class="bg-gray-50 rounded-lg px-4 py-3">
            <dt class="text-sm font-medium text-gray-500">Last Completed</dt>
            <dd class="mt-1 text-xl font-semibold text-gray-900">{getLastCompletedDate() || 'Never'}</dd>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="mt-6 flex space-x-3">
          <button
            class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            on:click={startWorkout}
          >
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            Start Workout
          </button>
          <button
            class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            on:click={() => window.location.href = `/dashboard/workouts/edit/${template?.template_id}`}
          >
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
            </svg>
            Edit
          </button>
          <button
            class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            on:click={cloneWorkout}
          >
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7v8a2 2 0 002 2h6M8 7V5a2 2 0 012-2h4.586a1 1 0 01.707.293l4.414 4.414a1 1 0 01.293.707V15a2 2 0 01-2 2h-2M8 7H6a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2v-2"></path>
            </svg>
            Clone
          </button>
          <button
            class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            on:click={deleteWorkout}
          >
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
            </svg>
            Delete
          </button>
        </div>
      </div>
    </div>

    <!-- Exercise List -->
    <div class="mt-8">
      <h2 class="text-xl font-bold text-gray-900 mb-6">Exercises</h2>
      <div class="bg-white rounded-xl shadow-sm divide-y divide-gray-200">
        {#each template.exercises as exercise, index}
          {@const exerciseDetails = exercises[exercise.exercise_id]}
          <div class="p-6">
            <div class="flex items-start">
              {#if exerciseDetails?.video_url}
                {@const videoId = getYouTubeId(exerciseDetails.video_url)}
                {#if videoId}
                  <div class="flex-shrink-0 w-48 h-32 rounded-lg overflow-hidden mr-6 relative group cursor-pointer"
                       on:click={() => openVideoPopup(exerciseDetails.video_url, exerciseDetails.name)}
                       on:keypress={(e) => e.key === 'Enter' && openVideoPopup(exerciseDetails.video_url, exerciseDetails.name)}
                       tabindex="0"
                       role="button">
                    <img
                      src={`https://img.youtube.com/vi/${videoId}/hqdefault.jpg`}
                      alt={exerciseDetails.name}
                      class="w-full h-full object-cover"
                    />
                    <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-all duration-200 flex items-center justify-center">
                      <svg class="w-12 h-12 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"></path>
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                      </svg>
                    </div>
                  </div>
                {/if}
              {/if}
              <div class="flex-1">
                <div class="flex justify-between">
                  <h3 class="text-lg font-medium text-gray-900">
                    {index + 1}. {exerciseDetails?.name || 'Unknown Exercise'}
                  </h3>
                  <div class="flex space-x-2">
                    {#if exerciseDetails?.muscle_groups}
                      {#each exerciseDetails.muscle_groups as group}
                        <span class="inline-flex items-center rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-800">
                          {group}
                        </span>
                      {/each}
                    {/if}
                  </div>
                </div>
                {#if exerciseDetails?.description}
                  <p class="mt-1 text-sm text-gray-500">{exerciseDetails.description}</p>
                {/if}
                <div class="mt-2 grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <span class="font-medium text-gray-500">Sets:</span>
                    <span class="ml-1 text-gray-900">{exercise.sets}</span>
                  </div>
                  <div>
                    <span class="font-medium text-gray-500">Reps:</span>
                    <span class="ml-1 text-gray-900">{exercise.reps}</span>
                  </div>
                  <div>
                    <span class="font-medium text-gray-500">Rest:</span>
                    <span class="ml-1 text-gray-900">{exercise.rest_time}s</span>
                  </div>
                </div>
                {#if exerciseDetails?.equipment}
                  <div class="mt-2 text-sm">
                    <span class="font-medium text-gray-500">Equipment:</span>
                    <span class="ml-2 text-gray-900">{exerciseDetails.equipment}</span>
                  </div>
                {/if}
              </div>
            </div>
          </div>
        {/each}
      </div>
    </div>

    <!-- Workout History -->
    {#if history.length > 0}
      <div class="mt-8">
        <h2 class="text-xl font-bold text-gray-900 mb-6">History</h2>
        <div class="bg-white rounded-xl shadow-sm overflow-hidden">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Duration</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Notes</th>
                  <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                {#each history as log}
                  <tr>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{formatDate(log.created_at)}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(log.end_time).getTime() - new Date(log.start_time).getTime()} min
                    </td>
                    <td class="px-6 py-4 text-sm text-gray-500">{log.notes || '-'}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        class="text-green-600 hover:text-green-900"
                        on:click={() => window.location.href = `/dashboard/workouts/logs/${log.log_id}`}
                      >
                        View details
                      </button>
                    </td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    {/if}
  {/if}
</div>

<!-- Video Popup -->
{#if activeVideo}
  <div class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4" on:click={closeVideoPopup}>
    <div class="bg-white rounded-xl overflow-hidden max-w-4xl w-full" on:click|stopPropagation>
      <div class="p-4 flex justify-between items-center border-b">
        <h3 class="text-lg font-medium text-gray-900">{activeVideo.title}</h3>
        <button
          class="text-gray-400 hover:text-gray-500 transition-colors duration-200"
          on:click={closeVideoPopup}
        >
          <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      <div class="relative" style="padding-top: 56.25%;">
        <iframe
          src={activeVideo.url}
          title={activeVideo.title}
          class="absolute inset-0 w-full h-full"
          frameborder="0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowfullscreen
        ></iframe>
      </div>
    </div>
  </div>
{/if}

<style>
  /* Add to existing styles */
  .group:focus-visible {
    outline: 2px solid #4f46e5;
    outline-offset: 2px;
  }
</style> 