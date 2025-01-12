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

  export let exercise: Exercise | null = null;
  export let showAIForm = false;

  const dispatch = createEventDispatcher<{
    exerciseCreated: void;
    cancel: void;
  }>();

  let loading = false;
  let error: string | null = null;
  let showAIModal = false;
  let generatingWithAI = false;

  // Add reactive statement to update showAIModal when showAIForm changes
  $: showAIModal = showAIForm;

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

  // Helper function to get label for a value
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
      console.log(generatedExercise);
      videoUrl = generatedExercise.video_url;

      showAIModal = false;
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

<div class="exercise-form max-w-3xl mx-auto bg-white rounded-xl shadow-lg">
  <!-- Header -->
  <div class="px-6 py-4 border-b border-gray-200">
    <div class="flex justify-between items-center">
      <h2 class="text-2xl font-bold text-gray-900">
        {exercise ? exercises_edit() : exercises_create_new()}
      </h2>
      <button
        class="text-gray-500 hover:text-gray-700 transition-colors duration-200"
        on:click={() => dispatch('cancel')}
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  </div>

  <!-- Form Content -->
  <div class="p-6">
    {#if error}
      <div class="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl flex items-start">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-red-400 mt-0.5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
        </svg>
        <p class="ml-3 text-sm font-medium text-red-800">{error}</p>
      </div>
    {/if}

    <form on:submit|preventDefault={handleSubmit} class="space-y-8">
      <!-- Basic Information Section -->
      <div class="space-y-6">
        <h3 class="text-lg font-medium text-gray-900 border-b border-gray-200 pb-2">Basic Information</h3>
        
        <div class="grid grid-cols-1 gap-6">
          <!-- Name -->
          <div>
            <label for="name" class="block text-sm font-medium text-gray-700 mb-1">
              {exercises_form_name()} <span class="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="name"
              bind:value={name}
              required
              class="block w-full rounded-lg border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 transition-colors duration-200"
              placeholder={exercises_form_name_placeholder()}
            />
          </div>

          <!-- Description -->
          <div>
            <label for="description" class="block text-sm font-medium text-gray-700 mb-1">
              {exercises_form_description()}
            </label>
            <textarea
              id="description"
              bind:value={description}
              rows="3"
              class="block w-full rounded-lg border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 transition-colors duration-200"
              placeholder={exercises_form_description_placeholder()}
            />
          </div>
        </div>
      </div>

      <!-- Categories Section -->
      <div class="space-y-6">
        <h3 class="text-lg font-medium text-gray-900 border-b border-gray-200 pb-2">Categories</h3>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Muscle Groups -->
          <div class="bg-gray-50 rounded-xl p-4">
            <label class="block text-sm font-medium text-gray-700 mb-3">
              {exercises_form_muscle_groups()} <span class="text-red-500">*</span>
            </label>
            <div class="grid grid-cols-2 gap-3">
              {#each muscleGroupOptions as { value, label }}
                <label class="relative flex items-start">
                  <div class="flex items-center h-5">
                    <input
                      type="checkbox"
                      checked={muscleGroups.includes(value)}
                      on:change={() => toggleMuscleGroup(value)}
                      class="rounded border-gray-300 text-green-600 focus:ring-green-500 transition-colors duration-200"
                    />
                  </div>
                  <div class="ml-2 text-sm">
                    <span class="font-medium text-gray-700">{label}</span>
                  </div>
                </label>
              {/each}
            </div>
          </div>

          <!-- Equipment -->
          <div class="bg-gray-50 rounded-xl p-4">
            <label class="block text-sm font-medium text-gray-700 mb-3">
              {exercises_form_equipment()}
            </label>
            <div class="grid grid-cols-2 gap-3">
              {#each equipmentOptions as { value, label }}
                <label class="relative flex items-start">
                  <div class="flex items-center h-5">
                    <input
                      type="checkbox"
                      checked={equipment.includes(value)}
                      on:change={() => toggleEquipment(value)}
                      class="rounded border-gray-300 text-green-600 focus:ring-green-500 transition-colors duration-200"
                    />
                  </div>
                  <div class="ml-2 text-sm">
                    <span class="font-medium text-gray-700">{label}</span>
                  </div>
                </label>
              {/each}
            </div>
          </div>
        </div>
      </div>

      <!-- Details Section -->
      <div class="space-y-6">
        <h3 class="text-lg font-medium text-gray-900 border-b border-gray-200 pb-2">Exercise Details</h3>
        
        <div class="grid grid-cols-1 gap-6">
          <!-- Difficulty -->
          <div>
            <label for="difficulty" class="block text-sm font-medium text-gray-700 mb-1">
              {exercises_form_difficulty_level()}
            </label>
            <select
              id="difficulty"
              bind:value={difficulty}
              class="block w-full rounded-lg border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 transition-colors duration-200"
            >
              {#each difficultyOptions as { value, label }}
                <option {value}>{label}</option>
              {/each}
            </select>
          </div>

          <!-- Instructions -->
          <div>
            <label for="instructions" class="block text-sm font-medium text-gray-700 mb-1">
              {exercises_form_instructions()}
            </label>
            <textarea
              id="instructions"
              bind:value={instructions}
              rows="4"
              class="block w-full rounded-lg border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 transition-colors duration-200"
              placeholder={exercises_form_instructions_placeholder()}
            />
          </div>

          <!-- Video URL -->
          <div>
            <label for="video-url" class="block text-sm font-medium text-gray-700 mb-1">
              {exercises_form_video_url()}
            </label>
            <input
              type="url"
              id="video-url"
              bind:value={videoUrl}
              class="block w-full rounded-lg border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 transition-colors duration-200"
              placeholder={exercises_form_video_url_placeholder()}
            />
          </div>
        </div>
      </div>

      <!-- Form Actions -->
      <div class="pt-6 border-t border-gray-200">
        <div class="flex justify-end space-x-3">
          <button
            type="button"
            class="px-4 py-2 border border-gray-300 rounded-lg shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-all duration-200"
            on:click={() => dispatch('cancel')}
          >
            {exercises_cancel()}
          </button>
          <button
            type="submit"
            disabled={loading}
            class="px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:bg-green-300 transition-all duration-200"
          >
            {loading ? exercises_saving() : exercises_save()}
          </button>
        </div>
      </div>
    </form>
  </div>
</div>

{#if showAIModal}
  <div class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4 z-50">
    <div class="bg-white rounded-xl max-w-xl w-full p-6 shadow-xl">
      <div class="flex justify-between items-center mb-6">
        <h3 class="text-xl font-semibold text-gray-900">{exercises_ai_modal_title()}</h3>
        <button
          class="text-gray-400 hover:text-gray-500 transition-colors duration-200"
          on:click={() => showAIModal = false}
        >
          <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {#if error}
        <div class="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl flex items-start">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-red-400 mt-0.5" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
          <p class="ml-3 text-sm font-medium text-red-800">{error}</p>
        </div>
      {/if}

      <div class="space-y-6">
        <!-- Exercise Type -->
        <div>
          <label for="ai-exercise-type" class="block text-sm font-medium text-gray-700 mb-1">
            {exercises_ai_exercise_type()}
          </label>
          <select
            id="ai-exercise-type"
            bind:value={aiExerciseType}
            class="block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 transition-colors duration-200"
          >
            {#each exerciseTypes as { value, label }}
              <option {value}>{label}</option>
            {/each}
          </select>
        </div>

        <!-- Target Muscles -->
        <div class="bg-gray-50 rounded-xl p-4">
          <label class="block text-sm font-medium text-gray-700 mb-3">
            {exercises_ai_target_muscles()} <span class="text-red-500">*</span>
          </label>
          <div class="grid grid-cols-2 gap-3">
            {#each muscleGroupOptions as { value, label }}
              <label class="relative flex items-start">
                <div class="flex items-center h-5">
                  <input
                    type="checkbox"
                    checked={aiTargetMuscles.includes(value)}
                    on:change={() => toggleMuscleGroup(value, aiTargetMuscles, (v) => aiTargetMuscles = v)}
                    class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 transition-colors duration-200"
                  />
                </div>
                <div class="ml-2 text-sm">
                  <span class="font-medium text-gray-700">{label}</span>
                </div>
              </label>
            {/each}
          </div>
        </div>

        <!-- Available Equipment -->
        <div class="bg-gray-50 rounded-xl p-4">
          <label class="block text-sm font-medium text-gray-700 mb-3">
            {exercises_ai_available_equipment()}
          </label>
          <div class="grid grid-cols-2 gap-3">
            {#each equipmentOptions as { value, label }}
              <label class="relative flex items-start">
                <div class="flex items-center h-5">
                  <input
                    type="checkbox"
                    checked={aiEquipment.includes(value)}
                    on:change={() => toggleEquipment(value, aiEquipment, (v) => aiEquipment = v)}
                    class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 transition-colors duration-200"
                  />
                </div>
                <div class="ml-2 text-sm">
                  <span class="font-medium text-gray-700">{label}</span>
                </div>
              </label>
            {/each}
          </div>
        </div>

        <!-- Difficulty -->
        <div>
          <label for="ai-difficulty" class="block text-sm font-medium text-gray-700 mb-1">
            {exercises_ai_difficulty()}
          </label>
          <select
            id="ai-difficulty"
            bind:value={aiDifficulty}
            class="block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 transition-colors duration-200"
          >
            {#each difficultyOptions as { value, label }}
              <option {value}>{label}</option>
            {/each}
          </select>
        </div>

        <!-- Considerations -->
        <div>
          <label for="ai-considerations" class="block text-sm font-medium text-gray-700 mb-1">
            {exercises_ai_considerations()}
          </label>
          <textarea
            id="ai-considerations"
            bind:value={aiConsiderations}
            rows="3"
            class="block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 transition-colors duration-200"
            placeholder={exercises_ai_considerations_placeholder()}
          />
        </div>

        <!-- Modal Actions -->
        <div class="flex justify-end space-x-3 mt-8">
          <button
            type="button"
            class="px-4 py-2 border border-gray-300 rounded-lg shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all duration-200"
            on:click={() => showAIModal = false}
          >
            {exercises_cancel()}
          </button>
          <button
            type="button"
            disabled={generatingWithAI}
            class="px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-indigo-300 transition-all duration-200"
            on:click={generateExercise}
          >
            {generatingWithAI ? exercises_ai_generating() : exercises_ai_generate()}
          </button>
        </div>
      </div>
    </div>
  </div>
{/if} 