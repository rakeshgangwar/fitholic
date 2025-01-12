<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { Exercise } from '$lib/types';
  import { api } from '$lib/api';

  export let exercise: Exercise | null = null;

  const dispatch = createEventDispatcher<{
    exerciseCreated: void;
    cancel: void;
  }>();

  let loading = false;
  let error: string | null = null;
  let showAIModal = false;
  let generatingWithAI = false;

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
    'Chest', 'Back', 'Shoulders', 'Biceps', 'Triceps', 
    'Legs', 'Core', 'Full Body', 'Cardio'
  ];

  const equipmentOptions = [
    'None', 'Dumbbells', 'Barbell', 'Kettlebell', 'Resistance Bands',
    'Pull-up Bar', 'Bench', 'Cable Machine', 'Smith Machine'
  ];

  const difficultyOptions = ['beginner', 'intermediate', 'advanced'];
  const exerciseTypes = ['strength', 'cardio', 'flexibility', 'balance', 'plyometric'];

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

  async function generateExercise() {
    if (aiTargetMuscles.length === 0) {
      error = 'Please select at least one target muscle group';
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

      showAIModal = false;
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to generate exercise';
    } finally {
      generatingWithAI = false;
    }
  }

  async function handleSubmit() {
    if (!name || muscleGroups.length === 0) {
      error = 'Please fill in all required fields';
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
      error = err instanceof Error ? err.message : 'Failed to save exercise';
    } finally {
      loading = false;
    }
  }
</script>

<div class="exercise-form max-w-2xl mx-auto bg-white p-6 rounded-lg shadow">
  <div class="mb-6 flex justify-between items-center">
    <h2 class="text-2xl font-bold text-gray-900">
      {exercise ? 'Edit Exercise' : 'Create New Exercise'}
    </h2>
    <div class="flex space-x-2">
      {#if !exercise}
        <button
          type="button"
          class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          on:click={() => showAIModal = true}
        >
          Generate with AI
        </button>
      {/if}
      <button
        class="text-gray-600 hover:text-gray-800"
        on:click={() => dispatch('cancel')}
      >
        Cancel
      </button>
    </div>
  </div>

  {#if error}
    <div class="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
      <p class="text-sm text-red-600">{error}</p>
    </div>
  {/if}

  <form on:submit|preventDefault={handleSubmit} class="space-y-6">
    <div>
      <label for="name" class="block text-sm font-medium text-gray-700">
        Exercise Name *
      </label>
      <input
        type="text"
        id="name"
        bind:value={name}
        required
        class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
        placeholder="e.g., Barbell Squat"
      />
    </div>

    <div>
      <label for="description" class="block text-sm font-medium text-gray-700">
        Description
      </label>
      <textarea
        id="description"
        bind:value={description}
        rows="3"
        class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
        placeholder="Brief description of the exercise..."
      />
    </div>

    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">
        Muscle Groups *
      </label>
      <div class="grid grid-cols-2 md:grid-cols-3 gap-2">
        {#each muscleGroupOptions as group}
          <label class="inline-flex items-center">
            <input
              type="checkbox"
              checked={muscleGroups.includes(group)}
              on:change={() => toggleMuscleGroup(group)}
              class="rounded border-gray-300 text-green-600 focus:ring-green-500"
            />
            <span class="ml-2 text-sm text-gray-700">{group}</span>
          </label>
        {/each}
      </div>
    </div>

    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">
        Required Equipment
      </label>
      <div class="grid grid-cols-2 md:grid-cols-3 gap-2">
        {#each equipmentOptions as item}
          <label class="inline-flex items-center">
            <input
              type="checkbox"
              checked={equipment.includes(item)}
              on:change={() => toggleEquipment(item)}
              class="rounded border-gray-300 text-green-600 focus:ring-green-500"
            />
            <span class="ml-2 text-sm text-gray-700">{item}</span>
          </label>
        {/each}
      </div>
    </div>

    <div>
      <label for="difficulty" class="block text-sm font-medium text-gray-700">
        Difficulty Level
      </label>
      <select
        id="difficulty"
        bind:value={difficulty}
        class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
      >
        {#each difficultyOptions as option}
          <option value={option}>{option}</option>
        {/each}
      </select>
    </div>

    <div>
      <label for="instructions" class="block text-sm font-medium text-gray-700">
        Instructions
      </label>
      <textarea
        id="instructions"
        bind:value={instructions}
        rows="4"
        class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
        placeholder="Step-by-step instructions for performing the exercise..."
      />
    </div>

    <div>
      <label for="video-url" class="block text-sm font-medium text-gray-700">
        Video URL
      </label>
      <input
        type="url"
        id="video-url"
        bind:value={videoUrl}
        class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
        placeholder="URL to demonstration video"
      />
    </div>

    <div class="flex justify-end space-x-3">
      <button
        type="button"
        class="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
        on:click={() => dispatch('cancel')}
      >
        Cancel
      </button>
      <button
        type="submit"
        disabled={loading}
        class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:bg-green-300"
      >
        {loading ? 'Saving...' : exercise ? 'Update Exercise' : 'Create Exercise'}
      </button>
    </div>
  </form>
</div>

{#if showAIModal}
  <div class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4">
    <div class="bg-white rounded-lg max-w-xl w-full p-6">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-medium text-gray-900">Generate Exercise with AI</h3>
        <button
          class="text-gray-400 hover:text-gray-500"
          on:click={() => showAIModal = false}
        >
          <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {#if error}
        <div class="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
          <p class="text-sm text-red-600">{error}</p>
        </div>
      {/if}

      <div class="space-y-4">
        <div>
          <label for="ai-exercise-type" class="block text-sm font-medium text-gray-700">
            Exercise Type
          </label>
          <select
            id="ai-exercise-type"
            bind:value={aiExerciseType}
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          >
            {#each exerciseTypes as type}
              <option value={type}>{type}</option>
            {/each}
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Target Muscle Groups *
          </label>
          <div class="grid grid-cols-2 gap-2">
            {#each muscleGroupOptions as group}
              <label class="inline-flex items-center">
                <input
                  type="checkbox"
                  checked={aiTargetMuscles.includes(group)}
                  on:change={() => toggleMuscleGroup(group, aiTargetMuscles, (v) => aiTargetMuscles = v)}
                  class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                />
                <span class="ml-2 text-sm text-gray-700">{group}</span>
              </label>
            {/each}
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Available Equipment
          </label>
          <div class="grid grid-cols-2 gap-2">
            {#each equipmentOptions as item}
              <label class="inline-flex items-center">
                <input
                  type="checkbox"
                  checked={aiEquipment.includes(item)}
                  on:change={() => toggleEquipment(item, aiEquipment, (v) => aiEquipment = v)}
                  class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                />
                <span class="ml-2 text-sm text-gray-700">{item}</span>
              </label>
            {/each}
          </div>
        </div>

        <div>
          <label for="ai-difficulty" class="block text-sm font-medium text-gray-700">
            Difficulty Level
          </label>
          <select
            id="ai-difficulty"
            bind:value={aiDifficulty}
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          >
            {#each difficultyOptions as option}
              <option value={option}>{option}</option>
            {/each}
          </select>
        </div>

        <div>
          <label for="ai-considerations" class="block text-sm font-medium text-gray-700">
            Special Considerations
          </label>
          <textarea
            id="ai-considerations"
            bind:value={aiConsiderations}
            rows="3"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            placeholder="Any special requirements or limitations (e.g., low impact, no jumping, etc.)"
          />
        </div>

        <div class="flex justify-end space-x-3 mt-6">
          <button
            type="button"
            class="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            on:click={() => showAIModal = false}
          >
            Cancel
          </button>
          <button
            type="button"
            disabled={generatingWithAI}
            class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-indigo-300"
            on:click={generateExercise}
          >
            {generatingWithAI ? 'Generating...' : 'Generate Exercise'}
          </button>
        </div>
      </div>
    </div>
  </div>
{/if} 