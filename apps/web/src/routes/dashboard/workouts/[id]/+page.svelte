<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { api } from '$lib/api';
  import type { WorkoutTemplate, WorkoutLog, Exercise } from '$lib/types';
  import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "$lib/components/ui/card";
  import { Button } from "$lib/components/ui/button";
  import { Alert, AlertDescription } from "$lib/components/ui/alert";
  import { Badge } from "$lib/components/ui/badge";
  import { Skeleton } from "$lib/components/ui/skeleton";
  import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "$lib/components/ui/table";
  import { Dialog, DialogContent, DialogHeader, DialogTitle } from "$lib/components/ui/dialog";
  import { goto } from '$app/navigation';
  import { buttonVariants } from "$lib/components/ui/button";
  import { ArrowLeft } from "lucide-svelte";
  import { cn } from "$lib/utils";

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
    switch (difficulty.toLowerCase()) {
      case 'beginner':
        return 'bg-green-500';
      case 'intermediate':
        return 'bg-yellow-500';
      case 'advanced':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
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

  function handleBack() {
    goto('/dashboard/workouts');
  }
</script>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
  <div class="mb-6">
    <button 
      type="button"
      class={cn(buttonVariants({ variant: 'ghost', size: 'sm' }), 'gap-2')}
      on:click={handleBack}
    >
      <ArrowLeft class="h-4 w-4" />
      Back to Workouts
    </button>
  </div>

  {#if loading.template}
    <div class="space-y-4">
      <Skeleton class="h-12 w-2/3" />
      <Skeleton class="h-24 w-full" />
    </div>
  {:else if error}
    <Alert variant="destructive">
      <AlertDescription>{error}</AlertDescription>
    </Alert>
  {:else if template}
    <Card>
      <CardHeader>
        <div class="flex justify-between items-start">
          <div>
            <CardTitle>{template.name}</CardTitle>
            {#if template.description}
              <CardDescription>{template.description}</CardDescription>
            {/if}
          </div>
          <Badge variant="outline" class={getDifficultyColor(template.difficulty)}>
            {template.difficulty}
          </Badge>
        </div>

        <!-- Quick Stats -->
        <div class="mt-6 grid grid-cols-1 gap-5 sm:grid-cols-3">
          <Card>
            <CardContent class="pt-6">
              <div class="text-sm font-medium text-muted-foreground">Exercises</div>
              <div class="text-2xl font-bold">{template.exercises.length}</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent class="pt-6">
              <div class="text-sm font-medium text-muted-foreground">Estimated Duration</div>
              <div class="text-2xl font-bold">{getEstimatedDuration()}</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent class="pt-6">
              <div class="text-sm font-medium text-muted-foreground">Last Completed</div>
              <div class="text-2xl font-bold">{getLastCompletedDate() || 'Never'}</div>
            </CardContent>
          </Card>
        </div>
      </CardHeader>
      <CardFooter class="pt-6">
        <div class="flex space-x-3 ml-auto">
          <Button variant="default" on:click={startWorkout}>
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            Start Workout
          </Button>
          <Button variant="outline" on:click={() => window.location.href = `/dashboard/workouts/edit/${template?.template_id}`}>
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
            </svg>
            Edit
          </Button>
          <Button variant="outline" on:click={cloneWorkout}>
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7v8a2 2 0 002 2h6M8 7V5a2 2 0 012-2h4.586a1 1 0 01.707.293l4.414 4.414a1 1 0 01.293.707V15a2 2 0 01-2 2h-2M8 7H6a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2v-2"></path>
            </svg>
            Clone
          </Button>
          <Button variant="destructive" on:click={deleteWorkout}>
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
            </svg>
          </Button>
        </div>
      </CardFooter>
    </Card>

    <!-- Exercise List -->
    <Card class="mt-8">
      <CardHeader>
        <CardTitle>Exercises</CardTitle>
      </CardHeader>
      <CardContent>
        <div class="divide-y divide-border">
          {#each template.exercises as exercise, index}
            {@const exerciseDetails = exercises[exercise.exercise_id]}
            <div class="py-6">
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
                      <div class="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-all duration-200 flex items-center justify-center">
                        <svg class="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"></path>
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                      </div>
                    </div>
                  {/if}
                {/if}
                <div class="flex-1">
                  <div class="flex justify-between">
                    <h3 class="text-lg font-medium">
                      {index + 1}. {exerciseDetails?.name || 'Unknown Exercise'}
                    </h3>
                    <div class="flex space-x-2">
                      {#if exerciseDetails?.muscle_groups}
                        {#each exerciseDetails.muscle_groups as group}
                          <Badge variant="secondary">{group}</Badge>
                        {/each}
                      {/if}
                    </div>
                  </div>
                  {#if exerciseDetails?.description}
                    <p class="mt-1 text-sm text-muted-foreground">{exerciseDetails.description}</p>
                  {/if}
                  <div class="mt-2 grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <span class="font-medium text-muted-foreground">Sets:</span>
                      <span class="ml-1">{exercise.sets}</span>
                    </div>
                    <div>
                      <span class="font-medium text-muted-foreground">Reps:</span>
                      <span class="ml-1">{exercise.reps}</span>
                    </div>
                    <div>
                      <span class="font-medium text-muted-foreground">Rest:</span>
                      <span class="ml-1">{exercise.rest_time}s</span>
                    </div>
                  </div>
                  {#if exerciseDetails?.equipment}
                    <div class="mt-2 text-sm">
                      <span class="font-medium text-muted-foreground">Equipment:</span>
                      <Badge variant="outline" class="ml-2">{exerciseDetails.equipment}</Badge>
                    </div>
                  {/if}
                </div>
              </div>
            </div>
          {/each}
        </div>
      </CardContent>
    </Card>

    <!-- Workout History -->
    {#if history.length > 0}
      <Card class="mt-8">
        <CardHeader>
          <CardTitle>History</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Date</TableHead>
                <TableHead>Duration</TableHead>
                <TableHead>Notes</TableHead>
                <TableHead class="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {#each history as log}
                <TableRow>
                  <TableCell>{formatDate(log.created_at)}</TableCell>
                  <TableCell>
                    {Math.round((new Date(log.end_time).getTime() - new Date(log.start_time).getTime()) / 60000)} min
                  </TableCell>
                  <TableCell>{log.notes || '-'}</TableCell>
                  <TableCell class="text-right">
                    <Button variant="link" on:click={() => window.location.href = `/dashboard/workouts/logs/${log.log_id}`}>
                      View details
                    </Button>
                  </TableCell>
                </TableRow>
              {/each}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    {/if}
  {/if}
</div>

<!-- Video Dialog -->
{#if activeVideo}
  <Dialog open={!!activeVideo} onOpenChange={() => closeVideoPopup()}>
    <DialogContent class="max-w-4xl">
      <DialogHeader>
        <DialogTitle>{activeVideo.title}</DialogTitle>
      </DialogHeader>
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
    </DialogContent>
  </Dialog>
{/if}

<style>
  /* Add to existing styles */
  .group:focus-visible {
    outline: 2px solid #4f46e5;
    outline-offset: 2px;
  }
</style> 