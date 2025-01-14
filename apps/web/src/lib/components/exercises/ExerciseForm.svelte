<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { Exercise } from '$lib/types';
  import { api } from '$lib/api';
  import {
    exercises_create_new,
    exercises_edit,
    exercises_generate_ai,
    exercises_cancel,
    exercises_form_name,
    exercises_form_name_placeholder,
    exercises_form_description,
    exercises_form_description_placeholder,
    exercises_form_muscle_groups,
    exercises_form_equipment,
    exercises_form_difficulty_level,
    exercises_form_instructions,
    exercises_form_instructions_placeholder,
    exercises_form_video_url,
    exercises_form_video_url_placeholder,
    exercises_form_required,
    exercises_form_save_failed,
    exercises_ai_modal_title,
    exercises_ai_exercise_type,
    exercises_ai_target_muscles,
    exercises_ai_available_equipment,
    exercises_ai_difficulty,
    exercises_ai_considerations,
    exercises_ai_considerations_placeholder,
    exercises_ai_generate,
    exercises_ai_generating,
    exercises_ai_error_muscles,
    exercises_ai_error_failed,
    exercises_save,
    exercises_saving,
    exercises_muscle_groups_chest,
    exercises_muscle_groups_back,
    exercises_muscle_groups_shoulders,
    exercises_muscle_groups_biceps,
    exercises_muscle_groups_triceps,
    exercises_muscle_groups_legs,
    exercises_muscle_groups_core,
    exercises_muscle_groups_full_body,
    exercises_muscle_groups_cardio,
    exercises_equipment_none,
    exercises_equipment_dumbbells,
    exercises_equipment_barbell,
    exercises_equipment_kettlebell,
    exercises_equipment_resistance_bands,
    exercises_equipment_pullup_bar,
    exercises_equipment_bench,
    exercises_equipment_cable,
    exercises_equipment_smith,
    exercises_difficulty_beginner,
    exercises_difficulty_intermediate,
    exercises_difficulty_advanced,
    exercises_type_strength,
    exercises_type_cardio,
    exercises_type_flexibility,
    exercises_type_balance,
    exercises_type_plyometric
  } from '$lib/paraglide/messages';
  import { cn } from '$lib/utils';
  import { buttonVariants } from '$lib/components/ui/button/button.svelte';
  import * as Card from '$lib/components/ui/card';
  import * as Tabs from '$lib/components/ui/tabs';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import { Textarea } from '$lib/components/ui/textarea';
  import * as Select from '$lib/components/ui/select';
  import { Alert, AlertDescription } from '$lib/components/ui/alert';
  import { AlertCircle, X } from 'lucide-svelte';
  import { Checkbox } from '$lib/components/ui/checkbox';

  export let exercise: Exercise | null = null;
  export let showAIForm = false;

  const dispatch = createEventDispatcher<{
    exerciseCreated: void;
    cancel: void;
  }>();

  let loading = false;
  let error: string | null = null;
  let generatingWithAI = false;
  let activeTab = showAIForm ? 'ai' : 'manual';

  // Form fields
  let name = exercise?.name ?? '';
  let description = exercise?.description ?? '';
  let muscleGroups = exercise?.muscle_groups ?? [];
  let equipment = exercise?.equipment ?? [];
  let difficulty = exercise?.difficulty ?? 'beginner';
  let instructions = exercise?.instructions ?? '';
  let videoUrl = exercise?.video_url ?? '';

  // AI Generation fields
  let aiExerciseType = 'strength';
  let aiTargetMuscles: string[] = [];
  let aiEquipment: string[] = [];
  let aiDifficulty = 'beginner';
  let aiConsiderations = '';

  const muscleGroupOptions = [
    { value: 'chest', label: exercises_muscle_groups_chest() },
    { value: 'back', label: exercises_muscle_groups_back() },
    { value: 'shoulders', label: exercises_muscle_groups_shoulders() },
    { value: 'biceps', label: exercises_muscle_groups_biceps() },
    { value: 'triceps', label: exercises_muscle_groups_triceps() },
    { value: 'legs', label: exercises_muscle_groups_legs() },
    { value: 'core', label: exercises_muscle_groups_core() },
    { value: 'full_body', label: exercises_muscle_groups_full_body() },
    { value: 'cardio', label: exercises_muscle_groups_cardio() }
  ];

  const equipmentOptions = [
    { value: 'none', label: exercises_equipment_none() },
    { value: 'dumbbells', label: exercises_equipment_dumbbells() },
    { value: 'barbell', label: exercises_equipment_barbell() },
    { value: 'kettlebell', label: exercises_equipment_kettlebell() },
    { value: 'resistance_bands', label: exercises_equipment_resistance_bands() },
    { value: 'pullup_bar', label: exercises_equipment_pullup_bar() },
    { value: 'bench', label: exercises_equipment_bench() },
    { value: 'cable', label: exercises_equipment_cable() },
    { value: 'smith', label: exercises_equipment_smith() }
  ];

  const difficultyOptions = [
    { value: 'beginner', label: exercises_difficulty_beginner() },
    { value: 'intermediate', label: exercises_difficulty_intermediate() },
    { value: 'advanced', label: exercises_difficulty_advanced() }
  ];

  const exerciseTypes = [
    { value: 'strength', label: exercises_type_strength() },
    { value: 'cardio', label: exercises_type_cardio() },
    { value: 'flexibility', label: exercises_type_flexibility() },
    { value: 'balance', label: exercises_type_balance() },
    { value: 'plyometric', label: exercises_type_plyometric() }
  ];

  function toggleMuscleGroup(group: string, target: string[] = muscleGroups, setter?: (value: string[]) => void) {
    const newValue = target.includes(group)
      ? target.filter(g => g !== group)
      : [...target, group];
    
    if (setter) {
      setter(newValue);
    } else {
      muscleGroups = newValue;
    }
  }

  function toggleEquipment(item: string, target: string[] = equipment, setter?: (value: string[]) => void) {
    const newValue = target.includes(item)
      ? target.filter(e => e !== item)
      : [...target, item];
    
    if (setter) {
      setter(newValue);
    } else {
      equipment = newValue;
    }
  }

  function getLabel(value: string, options: Array<{ value: string, label: string }>) {
    return options.find(opt => opt.value === value)?.label || value;
  }

  async function generateExercise() {
    if (aiTargetMuscles.length === 0) {
      error = exercises_ai_error_muscles();
      return;
    }

    generatingWithAI = true;
    error = null;

    try {
      const response = await api.post('/exercises/generate', {
        exercise_type: aiExerciseType,
        target_muscles: aiTargetMuscles,
        available_equipment: aiEquipment,
        difficulty: aiDifficulty,
        considerations: aiConsiderations
      });

      // Update form with AI-generated content
      const generatedExercise = response.data;
      name = generatedExercise.name;
      description = generatedExercise.description;
      muscleGroups = generatedExercise.muscle_groups;
      equipment = generatedExercise.equipment;
      difficulty = generatedExercise.difficulty;
      instructions = generatedExercise.instructions;
      videoUrl = generatedExercise.video_url;

      // Switch to manual tab to review and edit
      activeTab = 'manual';
    } catch (err) {
      error = err instanceof Error ? err.message : exercises_ai_error_failed();
    } finally {
      generatingWithAI = false;
    }
  }

  async function handleSubmit() {
    if (!name || muscleGroups.length === 0) {
      error = exercises_form_required();
      return;
    }

    loading = true;
    error = null;

    const exerciseData = {
      name,
      description,
      muscle_groups: muscleGroups,
      equipment,
      difficulty,
      instructions,
      video_url: videoUrl || null
    };

    try {
      if (exercise) {
        await api.put(`/exercises/${exercise.exercise_id}`, exerciseData);
      } else {
        await api.post('/exercises', exerciseData);
      }
      dispatch('exerciseCreated');
    } catch (err) {
      error = err instanceof Error ? err.message : exercises_form_save_failed();
    } finally {
      loading = false;
    }
  }
</script>

<Card.Root class="bg-card">
  <Card.Header class="flex flex-row items-center justify-between space-y-0 pb-2">
    <Card.Title class="text-2xl font-bold">
      {exercise ? exercises_edit() : exercises_create_new()}
    </Card.Title>
    <button
      type="button"
      class="rounded-full text-muted-foreground hover:text-foreground"
      on:click={() => dispatch('cancel')}
    >
      <X class="h-6 w-6" />
    </button>
  </Card.Header>

  <Card.Content>
    {#if error}
      <Alert variant="destructive" class="mb-6">
        <AlertCircle class="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    {/if}

    <Tabs.Root value={activeTab} onValueChange={(value) => activeTab = value} class="space-y-6">
      <Tabs.List>
        <Tabs.Trigger value="ai">AI Generation</Tabs.Trigger>
        <Tabs.Trigger value="manual">Manual Creation</Tabs.Trigger>
      </Tabs.List>

      <Tabs.Content value="ai" class="space-y-6">
        <div class="grid gap-6">
          <!-- Exercise Type -->
          <div class="grid gap-2">
            <Label for="ai-exercise-type">{exercises_ai_exercise_type()}</Label>
            <Select.Root type="single" bind:value={aiExerciseType}>
              <Select.Trigger class="w-full">
                {aiExerciseType ? getLabel(aiExerciseType, exerciseTypes) : exercises_type_strength()}
              </Select.Trigger>
              <Select.Content>
                {#each exerciseTypes as { value, label }}
                  <Select.Item {value} {label} />
                {/each}
              </Select.Content>
            </Select.Root>
          </div>

          <!-- Target Muscles -->
          <div class="grid gap-2">
            <Label>{exercises_ai_target_muscles()} <span class="text-destructive">*</span></Label>
            <div class="grid grid-cols-2 gap-4 p-4 border rounded-lg">
              {#each muscleGroupOptions as { value, label }}
                <div class="flex items-center space-x-2">
                  <Checkbox
                    id={`ai-muscle-${value}`}
                    checked={aiTargetMuscles.includes(value)}
                    onCheckedChange={() => toggleMuscleGroup(value, aiTargetMuscles, (v) => aiTargetMuscles = v)}
                  />
                  <Label for={`ai-muscle-${value}`} class="text-sm font-normal">{label}</Label>
                </div>
              {/each}
            </div>
          </div>

          <!-- Available Equipment -->
          <div class="grid gap-2">
            <Label>{exercises_ai_available_equipment()}</Label>
            <div class="grid grid-cols-2 gap-4 p-4 border rounded-lg">
              {#each equipmentOptions as { value, label }}
                <div class="flex items-center space-x-2">
                  <Checkbox
                    id={`ai-equipment-${value}`}
                    checked={aiEquipment.includes(value)}
                    onCheckedChange={() => toggleEquipment(value, aiEquipment, (v) => aiEquipment = v)}
                  />
                  <Label for={`ai-equipment-${value}`} class="text-sm font-normal">{label}</Label>
                </div>
              {/each}
            </div>
          </div>

          <!-- Difficulty -->
          <div class="grid gap-2">
            <Label for="ai-difficulty">{exercises_ai_difficulty()}</Label>
            <Select.Root type="single" bind:value={aiDifficulty}>
              <Select.Trigger class="w-full">
                {aiDifficulty ? getLabel(aiDifficulty, difficultyOptions) : exercises_difficulty_beginner()}
              </Select.Trigger>
              <Select.Content>
                {#each difficultyOptions as { value, label }}
                  <Select.Item {value} {label} />
                {/each}
              </Select.Content>
            </Select.Root>
          </div>

          <!-- Considerations -->
          <div class="grid gap-2">
            <Label for="ai-considerations">{exercises_ai_considerations()}</Label>
            <Textarea
              id="ai-considerations"
              bind:value={aiConsiderations}
              placeholder={exercises_ai_considerations_placeholder()}
              rows={3}
            />
          </div>

          <button
            type="button"
            class={cn(buttonVariants({ variant: 'default' }))}
            disabled={generatingWithAI}
            on:click={generateExercise}
          >
            {generatingWithAI ? exercises_ai_generating() : exercises_ai_generate()}
          </button>
        </div>
      </Tabs.Content>

      <Tabs.Content value="manual" class="space-y-6">
        <form on:submit|preventDefault={handleSubmit} class="space-y-6">
          <!-- Basic Information -->
          <div class="grid gap-6">
            <div class="grid gap-2">
              <Label for="name">{exercises_form_name()} <span class="text-destructive">*</span></Label>
              <Input
                type="text"
                id="name"
                bind:value={name}
                placeholder={exercises_form_name_placeholder()}
              />
            </div>

            <div class="grid gap-2">
              <Label for="description">{exercises_form_description()}</Label>
              <Textarea
                id="description"
                bind:value={description}
                placeholder={exercises_form_description_placeholder()}
                rows={3}
              />
            </div>
          </div>

          <!-- Categories -->
          <div class="grid gap-6">
            <div class="grid gap-2">
              <Label>{exercises_form_muscle_groups()} <span class="text-destructive">*</span></Label>
              <div class="grid grid-cols-2 gap-4 p-4 border rounded-lg">
                {#each muscleGroupOptions as { value, label }}
                  <div class="flex items-center space-x-2">
                    <Checkbox
                      id={`muscle-${value}`}
                      checked={muscleGroups.includes(value)}
                      onCheckedChange={() => toggleMuscleGroup(value)}
                    />
                    <Label for={`muscle-${value}`} class="text-sm font-normal">{label}</Label>
                  </div>
                {/each}
              </div>
            </div>

            <div class="grid gap-2">
              <Label>{exercises_form_equipment()}</Label>
              <div class="grid grid-cols-2 gap-4 p-4 border rounded-lg">
                {#each equipmentOptions as { value, label }}
                  <div class="flex items-center space-x-2">
                    <Checkbox
                      id={`equipment-${value}`}
                      checked={equipment.includes(value)}
                      onCheckedChange={() => toggleEquipment(value)}
                    />
                    <Label for={`equipment-${value}`} class="text-sm font-normal">{label}</Label>
                  </div>
                {/each}
              </div>
            </div>
          </div>

          <!-- Exercise Details -->
          <div class="grid gap-6">
            <div class="grid gap-2">
              <Label for="difficulty">{exercises_form_difficulty_level()}</Label>
              <Select.Root type="single" bind:value={difficulty}>
                <Select.Trigger class="w-full">
                  {difficulty ? getLabel(difficulty, difficultyOptions) : exercises_difficulty_beginner()}
                </Select.Trigger>
                <Select.Content>
                  {#each difficultyOptions as { value, label }}
                    <Select.Item {value} {label} />
                  {/each}
                </Select.Content>
              </Select.Root>
            </div>

            <div class="grid gap-2">
              <Label for="instructions">{exercises_form_instructions()}</Label>
              <Textarea
                id="instructions"
                bind:value={instructions}
                placeholder={exercises_form_instructions_placeholder()}
                rows={4}
              />
            </div>

            <div class="grid gap-2">
              <Label for="video-url">{exercises_form_video_url()}</Label>
              <Input
                type="url"
                id="video-url"
                bind:value={videoUrl}
                placeholder={exercises_form_video_url_placeholder()}
              />
            </div>
          </div>

          <!-- Form Actions -->
          <div class="flex justify-end space-x-4">
            <button
              type="button"
              class={cn(buttonVariants({ variant: 'outline' }))}
              on:click={() => dispatch('cancel')}
            >
              {exercises_cancel()}
            </button>
            <button
              type="submit"
              class={cn(buttonVariants({ variant: 'default' }))}
              disabled={loading}
            >
              {loading ? exercises_saving() : exercises_save()}
            </button>
          </div>
        </form>
      </Tabs.Content>
    </Tabs.Root>
  </Card.Content>
</Card.Root> 