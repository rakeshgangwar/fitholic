<script lang="ts">
  import { onMount } from 'svelte';
  import WorkoutPlanner from '$lib/components/workouts/WorkoutPlanner.svelte';
  import WorkoutLogger from '$lib/components/workouts/WorkoutLogger.svelte';
  import WorkoutSummary from '$lib/components/workouts/WorkoutSummary.svelte';
  import WorkoutGenerator from '$lib/components/workouts/WorkoutGenerator.svelte';
  import type { WorkoutTemplate } from '$lib/types';
  import { api } from '$lib/api';
  import { Tabs, TabsList, TabsTrigger, TabsContent } from "$lib/components/ui/tabs";
  import { Alert, AlertDescription } from "$lib/components/ui/alert";

  let activeTab = 'sessions';
  let sessions: WorkoutTemplate[] = [];
  let loading = false;
  let error: string | null = null;
  let selectedSession: WorkoutTemplate | null = null;
  let generating = false;
  let showGenerator = false;

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

  async function generateWorkout(event: CustomEvent<{
    duration: number;
    location: 'anywhere' | 'home' | 'gym' | 'outdoor';
    equipment: string[];
    intensity: 'light' | 'moderate' | 'intense';
    focusAreas: string[];
  }>) {
    try {
      generating = true;
      error = null;
      const response = await api.post('/workouts/generate', event.detail);
      sessions = [...sessions, response.data];
      selectedSession = response.data;
      showGenerator = false;
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

<div class="container mx-auto p-4 space-y-6">
  <div class="flex justify-between items-center">
    <h1 class="text-3xl font-bold">Workout Management</h1>
    {#if activeTab === 'sessions' && !showGenerator}
      <button 
        class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
        on:click={() => showGenerator = true}
      >
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
        </svg>
        Generate Workout
      </button>
    {/if}
  </div>

  {#if error}
    <Alert variant="destructive">
      <AlertDescription>{error}</AlertDescription>
    </Alert>
  {/if}

  {#if showGenerator}
    <WorkoutGenerator
      {generating}
      {error}
      on:generate={generateWorkout}
      on:cancel={() => showGenerator = false}
    />
  {:else}
    <div class="bg-card text-card-foreground rounded-lg shadow">
      <Tabs value={activeTab} onValueChange={(value: string) => activeTab = value} class="w-full">
        <TabsList class="grid w-full grid-cols-3">
          <TabsTrigger value="sessions" class="flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
            </svg>
            Sessions
          </TabsTrigger>
          <TabsTrigger value="log" class="flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
            </svg>
            Log Workout
          </TabsTrigger>
          <TabsTrigger value="history" class="flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
            </svg>
            History
          </TabsTrigger>
        </TabsList>

        <TabsContent value="sessions" class="p-6">
          <WorkoutPlanner
            templates={sessions}
            {loading}
            on:templateCreated={handleSessionCreated}
            on:templateDeleted={handleSessionDeleted}
            on:templateSelected={(e) => selectedSession = e.detail}
          />
        </TabsContent>

        <TabsContent value="log" class="p-6">
          <WorkoutLogger
            template={selectedSession}
            on:logSuccess={handleLogSuccess}
          />
        </TabsContent>

        <TabsContent value="history" class="p-6">
          <WorkoutSummary />
        </TabsContent>
      </Tabs>
    </div>
  {/if}
</div> 