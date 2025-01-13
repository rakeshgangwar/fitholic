<script lang="ts">
  import { onMount } from 'svelte';
  import { authStore } from '$lib/stores/auth';
  import { api } from '$lib/api';
  import { nav_welcome } from '$lib/paraglide/messages';
  import type { WorkoutLog, WorkoutTemplate, Exercise } from '$lib/types';

  let loading = {
    workouts: false,
    exercises: false,
    measurements: false
  };
  let error: string | null = null;
  let latestWorkout: WorkoutLog | null = null;
  let upcomingWorkout: WorkoutTemplate | null = null;
  let exerciseCount = 0;
  let measurements = {
    current: { weight: 0, body_fat: 0 },
    previous: { weight: 0, body_fat: 0 }
  };

  onMount(async () => {
    await Promise.all([
      loadLatestWorkout(),
      loadUpcomingWorkout(),
      loadExerciseCount(),
      loadMeasurements()
    ]);
  });

  async function loadLatestWorkout() {
    try {
      loading.workouts = true;
      const response = await api.get('/workouts/logs?limit=1');
      if (response.data.length > 0) {
        latestWorkout = response.data[0];
      }
    } catch (err) {
      console.error('Failed to load latest workout:', err);
    } finally {
      loading.workouts = false;
    }
  }

  async function loadUpcomingWorkout() {
    try {
      const response = await api.get('/workouts/templates?limit=1');
      if (response.data.length > 0) {
        upcomingWorkout = response.data[0];
      }
    } catch (err) {
      console.error('Failed to load upcoming workout:', err);
    }
  }

  async function loadExerciseCount() {
    try {
      loading.exercises = true;
      const response = await api.get('/exercises');
      exerciseCount = response.data.length;
    } catch (err) {
      console.error('Failed to load exercises:', err);
    } finally {
      loading.exercises = false;
    }
  }

  async function loadMeasurements() {
    try {
      loading.measurements = true;
      const response = await api.get('/measurements/me?limit=2');
      if (response.data.length > 0) {
        measurements.current = response.data[0];
        if (response.data.length > 1) {
          measurements.previous = response.data[1];
        }
      }
    } catch (err) {
      console.error('Failed to load measurements:', err);
    } finally {
      loading.measurements = false;
    }
  }

  function getProgressIndicator(current: number, previous: number): string {
    const diff = current - previous;
    if (diff > 0) return '↑';
    if (diff < 0) return '↓';
    return '→';
  }

  function formatDate(date: string): string {
    return new Date(date).toLocaleDateString();
  }
</script>

<div class="py-10">
  <header>
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <h1 class="text-3xl font-bold leading-tight text-gray-900">
        {nav_welcome({ name: $authStore?.first_name || 'User' })}
      </h1>
    </div>
  </header>
  <main>
    <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
      <div class="px-4 py-8 sm:px-0">
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-2">

          <!-- Next Workout Card -->
          <div class="bg-white overflow-hidden rounded-xl shadow-sm hover:shadow-md transition-all duration-300">
            <div class="p-5">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <svg class="h-6 w-6 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dl>
                    <dt class="text-sm font-medium text-gray-500 truncate">
                      Next Workout
                    </dt>
                    <dd class="flex items-baseline">
                      {#if loading.workouts}
                        <div class="text-sm text-gray-500">Loading...</div>
                      {:else if upcomingWorkout}
                        <div>
                          <div class="text-2xl font-semibold text-gray-900">
                            {upcomingWorkout.name}
                          </div>
                          <div class="text-sm text-gray-500">
                            {upcomingWorkout.exercises.length} exercises
                          </div>
                        </div>
                      {:else}
                        <div class="text-sm text-gray-500">No workouts planned</div>
                      {/if}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
            <div class="bg-gray-50 px-5 py-3">
              <div class="text-sm">
                <button 
                  class="font-medium text-green-600 hover:text-green-500 transition-colors duration-200"
                  on:click={() => window.location.href = '/dashboard/workouts?tab=sessions'}
                >
                  Plan next workout
                </button>
              </div>
            </div>
          </div>

          <!-- Exercise Library Card -->
          <div class="bg-white overflow-hidden rounded-xl shadow-sm hover:shadow-md transition-all duration-300">
            <div class="p-5">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <svg class="h-6 w-6 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dl>
                    <dt class="text-sm font-medium text-gray-500 truncate">
                      Exercise Library
                    </dt>
                    <dd class="flex items-baseline">
                      {#if loading.exercises}
                        <div class="text-sm text-gray-500">Loading...</div>
                      {:else}
                        <div>
                          <div class="text-2xl font-semibold text-gray-900">
                            {exerciseCount} exercises
                          </div>
                          <div class="text-sm text-gray-500">
                            Available in library
                          </div>
                        </div>
                      {/if}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
            <div class="bg-gray-50 px-5 py-3">
              <div class="text-sm">
                <button 
                  class="font-medium text-green-600 hover:text-green-500 transition-colors duration-200"
                  on:click={() => window.location.href = '/dashboard/exercises'}
                >
                  Browse exercises
                </button>
              </div>
            </div>
          </div>

          <!-- Latest Workout Card -->
          <div class="bg-white overflow-hidden rounded-xl shadow-sm hover:shadow-md transition-all duration-300">
            <div class="p-5">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <svg class="h-6 w-6 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dl>
                    <dt class="text-sm font-medium text-gray-500 truncate">
                      Latest Workout
                    </dt>
                    <dd class="flex items-baseline">
                      {#if loading.workouts}
                        <div class="text-sm text-gray-500">Loading...</div>
                      {:else if latestWorkout}
                        <div>
                          <div class="text-2xl font-semibold text-gray-900">
                            {latestWorkout.template?.name || 'Unknown Workout'}
                          </div>
                          <div class="text-sm text-gray-500">
                            Completed on {formatDate(latestWorkout.created_at)}
                          </div>
                        </div>
                      {:else}
                        <div class="text-sm text-gray-500">No workouts logged yet</div>
                      {/if}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
            <div class="bg-gray-50 px-5 py-3">
              <div class="text-sm">
                <button 
                  class="font-medium text-green-600 hover:text-green-500 transition-colors duration-200"
                  on:click={() => window.location.href = '/dashboard/workouts'}
                >
                  View workout history
                </button>
              </div>
            </div>
          </div>

          <!-- Body Measurements Card -->
          <div class="bg-white overflow-hidden rounded-xl shadow-sm hover:shadow-md transition-all duration-300">
            <div class="p-5">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <svg class="h-6 w-6 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dl>
                    <dt class="text-sm font-medium text-gray-500 truncate">
                      Body Measurements
                    </dt>
                    <dd class="flex items-baseline">
                      {#if loading.measurements}
                        <div class="text-sm text-gray-500">Loading...</div>
                      {:else if measurements.current.weight}
                        <div>
                          <div class="text-2xl font-semibold text-gray-900">
                            {measurements.current.weight} kg
                            <span class="text-sm font-normal text-gray-500">
                              {getProgressIndicator(measurements.current.weight, measurements.previous.weight)}
                            </span>
                          </div>
                          <div class="text-sm text-gray-500">
                            Body fat: {measurements.current.body_fat}%
                            <span>
                              {getProgressIndicator(measurements.current.body_fat, measurements.previous.body_fat)}
                            </span>
                          </div>
                        </div>
                      {:else}
                        <div class="text-sm text-gray-500">No measurements recorded</div>
                      {/if}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
            <div class="bg-gray-50 px-5 py-3">
              <div class="text-sm">
                <button 
                  class="font-medium text-green-600 hover:text-green-500 transition-colors duration-200"
                  on:click={() => window.location.href = '/dashboard/measurements'}
                >
                  Update measurements
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>
</div> 