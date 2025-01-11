<script lang="ts">
  import { onMount } from 'svelte';
  import WorkoutPlanner from '$lib/components/workouts/WorkoutPlanner.svelte';
  import WorkoutLogger from '$lib/components/workouts/WorkoutLogger.svelte';
  import WorkoutSummary from '$lib/components/workouts/WorkoutSummary.svelte';
  import type { WorkoutTemplate } from '$lib/types';
  import { api } from '$lib/api';

  let activeTab: 'templates' | 'log' | 'history' = 'templates';
  let templates: WorkoutTemplate[] = [];
  let loading = false;
  let error: string | null = null;
  let selectedTemplate: WorkoutTemplate | null = null;

  onMount(async () => {
    await loadTemplates();
  });

  async function loadTemplates() {
    try {
      loading = true;
      const response = await api.get('/workouts/templates');
      templates = response.data;
    } catch (err) {
      error = err instanceof Error ? err.message : 'An error occurred';
    } finally {
      loading = false;
    }
  }

  function handleTemplateCreated() {
    loadTemplates();
  }

  function handleTemplateDeleted() {
    loadTemplates();
    selectedTemplate = null;
  }

  function handleLogSuccess() {
    activeTab = 'history';
  }
</script>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
  <div class="py-10">
    <header>
      <h1 class="text-3xl font-bold leading-tight text-gray-900">
        Workout Management
      </h1>
    </header>

    <div class="mt-6 border-b border-gray-200">
      <nav class="-mb-px flex space-x-8">
        <button 
          class="whitespace-nowrap pb-4 px-1 border-b-2 font-medium text-sm {activeTab === 'templates' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
          on:click={() => activeTab = 'templates'}
        >
          Templates
        </button>
        <button 
          class="whitespace-nowrap pb-4 px-1 border-b-2 font-medium text-sm {activeTab === 'log' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
          on:click={() => activeTab = 'log'}
        >
          Log Workout
        </button>
        <button 
          class="whitespace-nowrap pb-4 px-1 border-b-2 font-medium text-sm {activeTab === 'history' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
          on:click={() => activeTab = 'history'}
        >
          History
        </button>
      </nav>
    </div>

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
      {#if activeTab === 'templates'}
        <WorkoutPlanner
          {templates}
          {loading}
          on:templateCreated={handleTemplateCreated}
          on:templateDeleted={handleTemplateDeleted}
          on:templateSelected={(e: CustomEvent<WorkoutTemplate>) => selectedTemplate = e.detail}
        />
      {:else if activeTab === 'log'}
        <WorkoutLogger
          template={selectedTemplate}
          on:logSuccess={handleLogSuccess}
        />
      {:else}
        <WorkoutSummary />
      {/if}
    </div>
  </div>
</div> 