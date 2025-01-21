<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import type { WorkoutLog, WorkoutTemplate } from '$lib/types';
  import { Card, CardContent, CardHeader, CardTitle } from "$lib/components/ui/card";
  import { Alert, AlertDescription } from "$lib/components/ui/alert";
  import { toast } from "svelte-sonner";
  import { 
    format, 
    startOfMonth, 
    endOfMonth, 
    eachDayOfInterval, 
    isToday, 
    isSameDay,
    startOfWeek,
    endOfWeek,
    isSameMonth,
    addDays,
    parseISO
  } from 'date-fns';

  const dispatch = createEventDispatcher<{
    startWorkout: WorkoutLog & { template?: WorkoutTemplate }
  }>();

  let workoutLogs: (WorkoutLog & { template?: WorkoutTemplate })[] = [];
  let loading = false;
  let error: string | null = null;
  let currentMonth = new Date();
  let monthWorkouts: { date: Date; workouts: WorkoutLog[] }[] = [];

  onMount(() => {
    loadWorkoutLogs();
  });

  async function fetchTemplateDetails(templateIds: string[]) {
    try {
      const uniqueTemplateIds = [...new Set(templateIds)];
      const templates = await Promise.all(
        uniqueTemplateIds.map(id => 
          api.get(`/workouts/templates/${id}`)
            .then(response => response.data)
            .catch(() => null)
        )
      );
      
      return templates.reduce((acc, template) => {
        if (template) {
          acc[template.template_id] = template;
        }
        return acc;
      }, {} as Record<string, WorkoutTemplate>);
    } catch (err) {
      console.error('Error fetching template details:', err);
      return {};
    }
  }

  async function loadWorkoutLogs() {
    try {
      loading = true;
      // Get the start of the first week and end of the last week of the month
      const monthStart = startOfMonth(currentMonth);
      const monthEnd = endOfMonth(currentMonth);
      const calendarStart = startOfWeek(monthStart);
      const calendarEnd = endOfWeek(monthEnd);

      const response = await api.get('/workouts/logs', {
        params: {
          start_date: format(calendarStart, 'yyyy-MM-dd'),
          end_date: format(calendarEnd, 'yyyy-MM-dd')
        }
      });

      const logs = response.data;
      
      // Fetch template details for all logs that have a template_id
      const templateIds = logs
        .map(log => log.template_id)
        .filter((id): id is string => !!id);
      
      const templatesMap = await fetchTemplateDetails(templateIds);
      
      // Combine logs with their template details
      workoutLogs = logs.map(log => ({
        ...log,
        template: log.template_id ? templatesMap[log.template_id] : undefined
      }));

    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to load workout logs';
    } finally {
      loading = false;
    }
  }

  function previousMonth() {
    currentMonth = addDays(currentMonth, -30);
    loadWorkoutLogs();
  }

  function nextMonth() {
    currentMonth = addDays(currentMonth, 30);
    loadWorkoutLogs();
  }

  function startWorkoutForToday() {
    const today = new Date();
    const todayStr = format(today, 'yyyy-MM-dd');
    // Find today's workout from monthWorkouts
    const todayWorkouts = monthWorkouts.find(day => 
      format(day.date, 'yyyy-MM-dd') === todayStr
    )?.workouts || [];
    console.log(todayWorkouts);

    if (todayWorkouts.length > 0) {
      // Use the first scheduled workout for today
      console.log("Starting workout for today:", todayWorkouts[0]);
      dispatch('startWorkout', todayWorkouts[0]);
    } else {
      // Show toast message for no scheduled workout
      toast.error("No workout scheduled for today.");
      
      // Create a new workout if none scheduled
      // const newWorkout: WorkoutLog = {
      //   log_id: crypto.randomUUID(),
      //   user_id: '',
      //   template_id: undefined,
      //   date: todayStr,
      //   start_time: today.toISOString(),
      //   exercises: [],
      //   end_time: undefined,
      //   duration: undefined,
      //   notes: undefined
      // };
      // console.log('Starting new workout for today:', newWorkout);
      // onStartWorkout(newWorkout);
    }
  }

  $: monthWorkouts = eachDayOfInterval({
    start: startOfWeek(startOfMonth(currentMonth)),
    end: endOfWeek(endOfMonth(currentMonth))
  }).map(date => {
    const workouts = workoutLogs.filter(log => isSameDay(parseISO(log.date), date));
    return {
      date,
      workouts
    };
  });

  function isWorkoutCompleted(workout: WorkoutLog): boolean {
    return !!workout.end_time;
  }

  function getDayClasses(date: Date, hasWorkouts: boolean) {
    return `
      relative p-2 h-24 border rounded
      ${!isSameMonth(date, currentMonth) ? 'bg-muted/50' : ''}
      ${isToday(date) ? 'border-primary' : 'border-border'}
      ${hasWorkouts ? 'cursor-pointer hover:bg-muted/50' : ''}
      overflow-auto
    `;
  }
</script>

<Card>
  <CardHeader>
    <div class="flex items-center justify-between">
      <CardTitle>Workout Calendar</CardTitle>
      <div class="flex gap-2">
        <button 
          class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-9 px-4 py-2"
          on:click={startWorkoutForToday}
        >
          Start Today's Workout
        </button>
        <button 
          class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-9 px-4 py-2"
          on:click={previousMonth}
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
          </svg>
        </button>
        <span class="text-lg font-semibold">
          {format(currentMonth, 'MMMM yyyy')}
        </span>
        <button 
          class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-9 px-4 py-2"
          on:click={nextMonth}
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
          </svg>
        </button>
      </div>
    </div>
  </CardHeader>

  <CardContent>
    {#if error}
      <Alert variant="destructive" class="mb-4">
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    {/if}

    <div class="grid grid-cols-7 gap-1 mb-2">
      {#each ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'] as day}
        <div class="text-center text-sm font-medium text-muted-foreground p-2">
          {day}
        </div>
      {/each}
    </div>

    <div class="grid grid-cols-7 gap-1">
      {#each monthWorkouts as { date, workouts }}
        <div class={getDayClasses(date, workouts.length > 0)}>
          <span class="text-sm {isToday(date) ? 'font-bold' : ''}">{format(date, 'd')}</span>
          {#if workouts.length > 0}
            <div class="mt-1 space-y-1">
              {#each workouts as workout}
                <button 
                  class="text-xs p-1 rounded cursor-pointer w-full text-left
                    {isWorkoutCompleted(workout) ? 'bg-green-500/20 hover:bg-green-500/30' : 'bg-primary/20 hover:bg-primary/30'}"
                  on:click={() => dispatch('startWorkout', workout)}
                >
                  <div class="truncate">
                    {#if workout.template}
                      {workout.template.name}
                    {:else}
                      Custom Workout
                    {/if}
                  </div>
                </button>
              {/each}
            </div>
          {/if}
        </div>
      {/each}
    </div>
  </CardContent>
</Card>
