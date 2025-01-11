<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';
  import type { Exercise, WorkoutTemplate, TemplateExercise } from '$lib/types';
  import { api } from '$lib/api';

  const dispatch = createEventDispatcher<{
    templateCreated: void;
    templateDeleted: void;
    templateSelected: WorkoutTemplate;
  }>();

  export let templates: WorkoutTemplate[] = [];
  export let loading = false;
  
  let showForm = false;
  let editingTemplate: WorkoutTemplate | null = null;
  let exercises: Exercise[] = [];
  let selectedExercises: TemplateExercise[] = [];
  let name = '';
  let description = '';
  let difficulty = 'beginner';
  let error = '';

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
    editingTemplate = null;
    showForm = false;
  }

  function startEditing(template: WorkoutTemplate) {
    editingTemplate = template;
    name = template.name;
    description = template.description || '';
    difficulty = template.difficulty;
    selectedExercises = template.exercises;
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
      if (editingTemplate) {
        await api.put(`/workouts/templates/${editingTemplate.template_id}`, workoutData);
      } else {
        await api.post('/workouts/templates', workoutData);
      }
      dispatch('templateCreated');
      resetForm();
    } catch (err) {
      error = 'Failed to save workout template';
    }
  }

  async function deleteTemplate(templateId: string) {
    if (!confirm('Are you sure you want to delete this template?')) return;

    try {
      await api.delete(`/workouts/templates/${templateId}`);
      dispatch('templateDeleted');
    } catch (err) {
      error = 'Failed to delete template';
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

  function handleExerciseSelect(event: Event) {
    const select = event.target as HTMLSelectElement;
    const selectedIndex = parseInt(select.value);
    if (!isNaN(selectedIndex)) {
      addExercise(exercises[selectedIndex]);
    }
    select.value = ''; // Reset select after adding
  }

  function handleNumberInput(event: Event, index: number, field: string) {
    const input = event.target as HTMLInputElement;
    const value = parseInt(input.value);
    if (!isNaN(value)) {
      updateExercise(index, field, value);
    }
  }
</script>

{#if showForm}
  <div class="workout-planner">
    <div class="form-header">
      <h2>{editingTemplate ? 'Edit' : 'Create'} Workout Template</h2>
      <button type="button" class="secondary" on:click={resetForm}>Back to Templates</button>
    </div>

    {#if error}
      <div class="error">{error}</div>
    {/if}

    <form on:submit|preventDefault={handleSubmit}>
      <div class="form-group">
        <label for="name">Workout Name *</label>
        <input
          type="text"
          id="name"
          bind:value={name}
          required
          placeholder="e.g., Full Body Workout"
        />
      </div>

      <div class="form-group">
        <label for="description">Description</label>
        <textarea
          id="description"
          bind:value={description}
          placeholder="Describe your workout..."
        />
      </div>

      <div class="form-group">
        <label for="difficulty">Difficulty *</label>
        <select id="difficulty" bind:value={difficulty}>
          <option value="beginner">Beginner</option>
          <option value="intermediate">Intermediate</option>
          <option value="advanced">Advanced</option>
        </select>
      </div>

      <div class="exercises-section">
        <h3>Exercises</h3>
        
        <div class="exercise-picker">
          <label>Add Exercise:</label>
          <select on:change={handleExerciseSelect}>
            <option value="">Select an exercise...</option>
            {#each exercises as exercise, i}
              <option value={i}>{exercise.name}</option>
            {/each}
          </select>
        </div>

        {#if selectedExercises.length > 0}
          <div class="selected-exercises">
            {#each selectedExercises as exercise, i}
              <div class="exercise-item">
                <div class="exercise-header">
                  <span>{exercises.find(e => e.exercise_id === exercise.exercise_id)?.name}</span>
                  <button type="button" class="danger" on:click={() => removeExercise(i)}>Remove</button>
                </div>
                <div class="exercise-details">
                  <label>
                    Sets:
                    <input
                      type="number"
                      min="1"
                      bind:value={exercise.sets}
                      on:input={(e) => handleNumberInput(e, i, 'sets')}
                    />
                  </label>
                  <label>
                    Reps:
                    <input
                      type="number"
                      min="1"
                      bind:value={exercise.reps}
                      on:input={(e) => handleNumberInput(e, i, 'reps')}
                    />
                  </label>
                  <label>
                    Rest (seconds):
                    <input
                      type="number"
                      min="0"
                      step="5"
                      bind:value={exercise.rest_time}
                      on:input={(e) => handleNumberInput(e, i, 'rest_time')}
                    />
                  </label>
                </div>
              </div>
            {/each}
          </div>
        {:else}
          <p class="no-exercises">No exercises added yet</p>
        {/if}
      </div>

      <div class="form-actions">
        <button type="submit" disabled={loading}>
          {loading ? 'Saving...' : editingTemplate ? 'Update Workout' : 'Create Workout'}
        </button>
      </div>
    </form>
  </div>
{:else}
  <div class="templates-list">
    <div class="templates-header">
      <h2>Your Workout Templates</h2>
      <button on:click={() => showForm = true}>Create Template</button>
    </div>

    {#if loading}
      <div class="loading">Loading templates...</div>
    {:else if templates.length === 0}
      <div class="no-templates">
        <p>You haven't created any workout templates yet.</p>
        <button on:click={() => showForm = true}>Create Your First Template</button>
      </div>
    {:else}
      <div class="templates-grid">
        {#each templates as template}
          <div class="template-card">
            <div class="template-header">
              <h3>{template.name}</h3>
              <span class="difficulty {template.difficulty}">
                {template.difficulty}
              </span>
            </div>
            {#if template.description}
              <p class="description">{template.description}</p>
            {/if}
            <div class="exercises-count">
              {template.exercises.length} exercise{template.exercises.length === 1 ? '' : 's'}
            </div>
            <div class="template-actions">
              <button
                class="secondary"
                on:click={() => startEditing(template)}
              >
                Edit
              </button>
              <button
                class="secondary"
                on:click={() => dispatch('templateSelected', template)}
              >
                Start Workout
              </button>
              <button
                class="danger"
                on:click={() => deleteTemplate(template.template_id)}
              >
                Delete
              </button>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </div>
{/if}

<style>
  .workout-planner {
    max-width: 800px;
    margin: 0 auto;
  }

  .form-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
  }

  .error {
    color: red;
    margin-bottom: 1rem;
    padding: 0.5rem;
    border: 1px solid red;
    border-radius: 4px;
  }

  .form-group {
    margin-bottom: 1rem;
  }

  label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
  }

  input, select, textarea {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    margin-bottom: 0.5rem;
  }

  textarea {
    min-height: 100px;
  }

  .exercises-section {
    margin-top: 2rem;
  }

  .exercise-picker {
    margin-bottom: 1rem;
  }

  .selected-exercises {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .exercise-item {
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 1rem;
  }

  .exercise-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  .exercise-details {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
  }

  .exercise-details label {
    font-size: 0.9rem;
  }

  .exercise-details input {
    width: 80px;
  }

  .no-exercises {
    text-align: center;
    color: #666;
    padding: 2rem;
  }

  .templates-list {
    max-width: 1200px;
    margin: 0 auto;
  }

  .templates-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
  }

  .loading, .no-templates {
    text-align: center;
    padding: 2rem;
    color: #666;
  }

  .templates-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
  }

  .template-card {
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 1rem;
  }

  .template-header {
    display: flex;
    justify-content: space-between;
    align-items: start;
    margin-bottom: 1rem;
  }

  .template-header h3 {
    margin: 0;
    font-size: 1.2rem;
  }

  .difficulty {
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.8rem;
    text-transform: capitalize;
  }

  .difficulty.beginner {
    background-color: #e8f5e9;
    color: #2e7d32;
  }

  .difficulty.intermediate {
    background-color: #fff3e0;
    color: #ef6c00;
  }

  .difficulty.advanced {
    background-color: #ffebee;
    color: #c62828;
  }

  .description {
    color: #666;
    margin-bottom: 1rem;
    font-size: 0.9rem;
  }

  .exercises-count {
    color: #666;
    font-size: 0.9rem;
    margin-bottom: 1rem;
  }

  .template-actions {
    display: flex;
    gap: 0.5rem;
  }

  button {
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1rem;
    background-color: #4CAF50;
    color: white;
  }

  button.secondary {
    background-color: #f5f5f5;
    color: #333;
  }

  button.danger {
    background-color: #f44336;
    color: white;
  }

  button:hover {
    opacity: 0.9;
  }

  button:disabled {
    background-color: #ccc;
    cursor: not-allowed;
  }
</style> 