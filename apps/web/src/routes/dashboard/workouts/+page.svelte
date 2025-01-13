<script lang="ts">
  import { onMount } from 'svelte';
  import WorkoutPlanner from '$lib/components/workouts/WorkoutPlanner.svelte';
  import WorkoutLogger from '$lib/components/workouts/WorkoutLogger.svelte';
  import WorkoutSummary from '$lib/components/workouts/WorkoutSummary.svelte';
  import type { WorkoutTemplate } from '$lib/types';
  import { api } from '$lib/api';

  let activeTab: 'sessions' | 'log' | 'history' = 'sessions';
  let sessions: WorkoutTemplate[] = [];
  let loading = false;
  let error: string | null = null;
  let selectedSession: WorkoutTemplate | null = null;
  let generating = false;

  onMount(async () => {
    await loadSessions();
  });

  async function loadSessions() {
    try {
      loading = true;
      const response = await api.get('/workouts/templates');
      sessions = response.data;
    } catch (err) {
      error = err instanceof Error ? err.message : 'An error occurred';
    } finally {
      loading = false;
    }
  }

  async function generateWorkout() {
    try {
      generating = true;
      error = null;
      const response = await api.post('/workouts/generate');
      sessions = [...sessions, response.data];
      selectedSession = response.data;
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to generate workout';
    } finally {
      generating = false;
    }
  }

  function handleSessionCreated() {
    loadSessions();
  }

  function handleSessionDeleted() {
    loadSessions();
    selectedSession = null;
  }

  function handleLogSuccess() {
    activeTab = 'history';
  }
</script>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
  <div class="py-10">
    <header class="flex justify-between items-center">
      <h1 class="text-3xl font-bold leading-tight text-gray-900">
        Workout Management
      </h1>
      {#if activeTab === 'sessions'}
        <button
          class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 transition-colors duration-200"
          on:click={generateWorkout}
          disabled={generating}
        >
          {#if generating}
            <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Generating...
          {:else}
            <svg class="w-4 h-4 mr-2 inline-block" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
            </svg>
            Generate Session
          {/if}
        </button>
      {/if}
    </header>

    <div class="mt-4 bg-white rounded-xl p-6 shadow-sm">
      <!-- Navigation Tabs -->
      <div class="flex space-x-8 mb-6">
        <button 
          class="px-3 py-2 text-sm font-medium rounded-md transition-colors duration-200 flex items-center {activeTab === 'sessions' ? 'text-green-700 bg-green-50' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'}"
          on:click={() => activeTab = 'sessions'}
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
          </svg>
          Sessions
        </button>
        <button 
          class="px-3 py-2 text-sm font-medium rounded-md transition-colors duration-200 flex items-center {activeTab === 'log' ? 'text-green-700 bg-green-50' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'}"
          on:click={() => activeTab = 'log'}
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
          </svg>
          Log Workout
        </button>
        <button 
          class="px-3 py-2 text-sm font-medium rounded-md transition-colors duration-200 flex items-center {activeTab === 'history' ? 'text-green-700 bg-green-50' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'}"
          on:click={() => activeTab = 'history'}
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
          </svg>
          History
        </button>
      </div>

      <!-- Error Alert -->
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

      <!-- Content Area -->
      <div>
        {#if activeTab === 'sessions'}
          <WorkoutPlanner
            templates={sessions}
            {loading}
            on:templateCreated={handleSessionCreated}
            on:templateDeleted={handleSessionDeleted}
            on:templateSelected={(e) => selectedSession = e.detail}
          />
        {:else if activeTab === 'log'}
          <WorkoutLogger
            template={selectedSession}
            on:logSuccess={handleLogSuccess}
          />
        {:else}
          <WorkoutSummary />
        {/if}
      </div>
    </div>
  </div>
</div> 