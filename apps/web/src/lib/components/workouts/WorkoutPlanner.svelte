<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';
  import type { Exercise, WorkoutTemplate, TemplateExercise } from '$lib/types';
  import { api } from '$lib/api';
  import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "$lib/components/ui/card";
  import { Input } from "$lib/components/ui/input";
  import { Label } from "$lib/components/ui/label";
  import { Select, SelectTrigger, SelectContent, SelectItem } from "$lib/components/ui/select";
  import { Badge } from "$lib/components/ui/badge";
  import { Alert, AlertDescription } from "$lib/components/ui/alert";
  import { Textarea } from "$lib/components/ui/textarea";

  const dispatch = createEventDispatcher<{
    templateCreated: void;
    templateDeleted: void;
    templateSelected: WorkoutTemplate;
    addToCalendar: WorkoutTemplate;
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
  let selectedExerciseIndex: string | null = null;

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

  $: if (selectedExerciseIndex !== null) {
    const index = parseInt(selectedExerciseIndex);
    if (!isNaN(index)) {
      addExercise(exercises[index]);
      selectedExerciseIndex = null;
    }
  }

  function getDifficultyColor(difficulty: string): string {
    switch (difficulty) {
      case 'beginner':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'intermediate':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case 'advanced':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200';
    }
  }

  async function addToCalendar(session: WorkoutTemplate) {
    console.log('Adding session to calendar:', session);
    dispatch('addToCalendar', session);
  }
</script>

{#if showForm}
  <div class="max-w-3xl mx-auto">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-xl font-semibold">{editingSession ? 'Edit' : 'Create'} Workout Session</h2>
      <button 
        class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2"
        on:click={resetForm}
      >
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
        </svg>
        Back to Sessions
      </button>
    </div>

    {#if error}
      <Alert variant="destructive" class="mb-6">
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    {/if}

    <Card>
      <CardContent class="pt-6">
        <form on:submit|preventDefault={handleSubmit} class="space-y-6">
          <div class="space-y-2">
            <Label for="name">Session Name *</Label>
            <Input
              type="text"
              id="name"
              bind:value={name}
              required
              placeholder="e.g., Full Body Workout"
            />
          </div>

          <div class="space-y-2">
            <Label for="description">Description</Label>
            <Textarea
              id="description"
              bind:value={description}
              rows="3"
              placeholder="Describe your workout session..."
            />
          </div>

          <div class="space-y-2">
            <Label for="difficulty">Difficulty *</Label>
            <Select bind:value={difficulty}>
              <SelectTrigger>
                {difficulty}
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="beginner">Beginner</SelectItem>
                <SelectItem value="intermediate">Intermediate</SelectItem>
                <SelectItem value="advanced">Advanced</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div class="space-y-4">
            <div class="flex justify-between items-center">
              <Label>Exercises</Label>
              <Select value={selectedExerciseIndex} onValueChange={(value) => selectedExerciseIndex = value}>
                <SelectTrigger class="w-[200px]">
                  Add Exercise...
                </SelectTrigger>
                <SelectContent>
                  {#each exercises as exercise, i}
                    <SelectItem value={i.toString()}>{exercise.name}</SelectItem>
                  {/each}
                </SelectContent>
              </Select>
            </div>

            {#if selectedExercises.length > 0}
              <div class="space-y-4">
                {#each selectedExercises as exercise, i}
                  <Card>
                    <CardContent class="pt-6">
                      <div class="flex justify-between items-start mb-4">
                        <h4 class="text-sm font-medium">
                          {exercises.find(e => e.exercise_id === exercise.exercise_id)?.name}
                        </h4>
                        <button
                          type="button"
                          class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 hover:bg-accent hover:text-accent-foreground h-10 w-10 text-destructive"
                          on:click={() => removeExercise(i)}
                        >
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                          </svg>
                        </button>
                      </div>
                      <div class="grid grid-cols-3 gap-4">
                        <div class="space-y-2">
                          <Label>Sets</Label>
                          <Input
                            type="number"
                            min="1"
                            bind:value={exercise.sets}
                          />
                        </div>
                        <div class="space-y-2">
                          <Label>Reps</Label>
                          <Input
                            type="number"
                            min="1"
                            bind:value={exercise.reps}
                          />
                        </div>
                        <div class="space-y-2">
                          <Label>Rest (sec)</Label>
                          <Input
                            type="number"
                            min="0"
                            step="5"
                            bind:value={exercise.rest_time}
                          />
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                {/each}
              </div>
            {:else}
              <Card class="bg-muted">
                <CardContent class="flex flex-col items-center justify-center py-12">
                  <svg class="h-12 w-12 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                  </svg>
                  <p class="mt-2 text-sm text-muted-foreground">No exercises added yet</p>
                </CardContent>
              </Card>
            {/if}
          </div>

          <div class="flex justify-end">
            <button 
              type="submit" 
              class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
              disabled={loading}
            >
              {loading ? 'Saving...' : editingSession ? 'Update Session' : 'Create Session'}
            </button>
          </div>
        </form>
      </CardContent>
    </Card>
  </div>
{:else}
  <div>
    {#if loading}
      <div class="flex justify-center items-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-muted border-t-primary"></div>
        <p class="mt-4 text-muted-foreground text-sm">Loading sessions...</p>
      </div>
    {:else if templates.length === 0}
      <Card class="text-center py-12">
        <CardContent>
          <svg class="mx-auto h-12 w-12 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
          </svg>
          <h3 class="mt-2 text-sm font-medium">No workout sessions</h3>
          <p class="mt-1 text-sm text-muted-foreground">Get started by creating a new workout session.</p>
          <!-- <div class="mt-6">
            <button 
              class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
              on:click={() => showForm = true}
            >
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
              </svg>
              Create Session
            </button>
          </div> -->
        </CardContent>
      </Card>
    {:else}
      <!-- <div class="flex justify-end mb-6">
        <button 
          class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
          on:click={() => showForm = true}
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
          </svg>
          Create Session
        </button>
      </div> -->

      <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {#each templates as session}
          <Card class="group hover:shadow-md transition-all duration-300">
            <CardHeader>
              <div class="flex justify-between items-start">
                <div>
                  <CardTitle>
                    <button 
                      class="text-lg font-semibold group-hover:text-primary transition-colors duration-200"
                      on:click={() => window.location.href = `/dashboard/workouts/${session.template_id}`}
                    >
                      {session.name}
                    </button>
                  </CardTitle>
                  <CardDescription class="mt-1 line-clamp-2">
                    {session.description || 'No description'}
                  </CardDescription>
                </div>
                <Badge variant="outline" class={getDifficultyColor(session.difficulty)}>
                  {session.difficulty}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div class="flex items-center justify-between text-sm">
                <span class="text-muted-foreground">{session.exercises.length} exercises</span>
                <div class="flex space-x-2">
                  <button 
                    class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-9 px-4 py-2"
                    on:click={() => addToCalendar(session)}
                  >
                    Add to Calendar
                  </button>
                </div>
              </div>
            </CardContent>
          </Card>
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