<script lang="ts">
  import { onMount } from 'svelte';
  import WorkoutPlanner from '$lib/components/workouts/WorkoutPlanner.svelte';
  import WorkoutLogger from '$lib/components/workouts/WorkoutLogger.svelte';
  import WorkoutSummary from '$lib/components/workouts/WorkoutSummary.svelte';
  import WorkoutGenerator from '$lib/components/workouts/WorkoutGenerator.svelte';
  import VoiceWorkoutLogger from '$lib/components/workouts/VoiceWorkoutLogger.svelte';
  import type { WorkoutTemplate } from '$lib/types';
  import { api } from '$lib/api';
  import { Tabs, TabsList, TabsTrigger, TabsContent } from "$lib/components/ui/tabs";
  import { Alert, AlertDescription } from "$lib/components/ui/alert";
  import { format } from 'date-fns';
  import { Popover, PopoverTrigger, PopoverContent } from "$lib/components/ui/popover";
  import { Calendar } from "$lib/components/ui/calendar";
  import type { DateValue } from "$lib/components/ui/calendar";
  import WorkoutCalendar from '$lib/components/workouts/WorkoutCalendar.svelte';
  import { CalendarDate, getLocalTimeZone, today } from "@internationalized/date";

  let activeTab = 'sessions';
  let sessions: WorkoutTemplate[] = [];
  let loading = false;
  let error: string | null = null;
  let selectedSession: WorkoutTemplate | null = null;
  let generating = false;
  let showGenerator = false;
  let selectedTemplate: WorkoutTemplate | null = null;
  let showDatePicker = false;
  let selectedDate = today(getLocalTimeZone());

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

  async function addToCalendar(event: CustomEvent<WorkoutTemplate>) {
    selectedTemplate = event.detail;
    showDatePicker = true;
  }

  async function handleDateSelect(date: CalendarDate) {
    console.log('Selected date:', date);
    if (!selectedTemplate || !date) return;
    console.log('Adding session to calendar:', selectedTemplate);

    try {
      error = null;
      const jsDate = new Date(date.year, date.month - 1, date.day);
      console.log('JavaScript date:', jsDate);
      console.log(selectedTemplate.template_id, format(jsDate, 'yyyy-MM-dd'));
      selectedTemplate.exercises.map(ex => (console.log(ex)))
      const workoutLog = {
        template_id: selectedTemplate.template_id,
        date: format(jsDate, 'yyyy-MM-dd'),
        start_time: new Date().toISOString(),
        exercises: selectedTemplate.exercises.map(ex => ({
          exercise_id: ex.exercise_id,
          sets: Array(ex.sets).fill(null).map(() => ({
            reps: ex.reps,
            weight: 0,
            completed: false
          })),
          completed: false
        }))
      };

      console.log('Workout log:', workoutLog);

      await api.post('/workouts/logs', workoutLog);
      showDatePicker = false;
      selectedTemplate = null;
      selectedDate = null;
      activeTab = 'calendar';
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to add workout to calendar';
    }
  }

  function handleStartWorkout(event: CustomEvent<WorkoutLog & { template?: WorkoutTemplate }>) {
    const workoutLog = event.detail;
    if (workoutLog.template_id && workoutLog.template) {
      selectedSession = workoutLog.template;
      activeTab = 'log';
    } else {
      error = 'Template not found for this workout';
    }
  }
</script>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
  <header class="flex justify-between items-center mb-6">
    <h1 class="text-3xl font-bold tracking-tight">
      Workout Management
    </h1>
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
  </header>

  {#if error}
    <Alert variant="destructive" class="mb-6">
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
        <TabsList class="grid w-full grid-cols-5">
          <TabsTrigger value="sessions" class="flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
            </svg>
            Sessions
          </TabsTrigger>
          <TabsTrigger value="calendar" class="flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
            </svg>
            Calendar
          </TabsTrigger>
          <TabsTrigger value="log" class="flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
            </svg>
            Log Workout
          </TabsTrigger>
          <TabsTrigger value="voice" class="flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path>
            </svg>
            Voice Assistant
          </TabsTrigger>
          <TabsTrigger value="history" class="flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
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
            on:addToCalendar={addToCalendar}
          />
        </TabsContent>

        <TabsContent value="calendar" class="p-6">
          <WorkoutCalendar onStartWorkout={handleStartWorkout} />
        </TabsContent>

        <TabsContent value="log" class="p-6">
          <WorkoutLogger
            template={selectedSession}
            on:logSuccess={handleLogSuccess}
          />
        </TabsContent>

        <TabsContent value="voice" class="p-6">
          <VoiceWorkoutLogger
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

{#if showDatePicker}
  <div class="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center">
    <div class="bg-card text-card-foreground rounded-lg shadow-lg p-6 max-w-md w-full mx-4">
      <h2 class="text-lg font-semibold mb-4">Select Date for Workout</h2>
      <Calendar
        type="single"
        bind:value={selectedDate}
        class="rounded-md border mb-4"
      />
      <div class="flex justify-end gap-2">
        <!-- <button 
          class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2"
          on:click={() => {
            showDatePicker = false;
            selectedTemplate = null;
            selectedDate = null;
          }}
        >
          Cancel
        </button> -->
        <button 
          class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
          on:click={() => handleDateSelect(selectedDate)}
          disabled={!selectedDate}
        >
          Add to Calendar
        </button>
      </div>
    </div>
  </div>
{/if}