<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "$lib/components/ui/card";
  import { Input } from "$lib/components/ui/input";
  import { Label } from "$lib/components/ui/label";
  import { Select, SelectTrigger, SelectContent, SelectItem } from "$lib/components/ui/select";
  import { Checkbox } from "$lib/components/ui/checkbox";
  import { Alert, AlertDescription } from "$lib/components/ui/alert";

  const dispatch = createEventDispatcher<{
    cancel: void;
    generate: {
      duration: number;
      location: 'anywhere' | 'home' | 'gym' | 'outdoor';
      equipment: string[];
      intensity: 'light' | 'moderate' | 'intense';
      focusAreas: string[];
    };
  }>();

  export let generating = false;
  export let error: string | null = null;

  let duration = 45; // minutes
  let location: 'anywhere' | 'home' | 'gym' | 'outdoor' = 'anywhere';
  let intensity: 'light' | 'moderate' | 'intense' = 'moderate';
  
  const availableEquipment = [
    { id: 'dumbbells', label: 'Dumbbells' },
    { id: 'barbell', label: 'Barbell' },
    { id: 'kettlebell', label: 'Kettlebell' },
    { id: 'resistance-bands', label: 'Resistance Bands' },
    { id: 'pull-up-bar', label: 'Pull-up Bar' },
    { id: 'bench', label: 'Bench' },
    { id: 'yoga-mat', label: 'Yoga Mat' },
    { id: 'none', label: 'No Equipment (Bodyweight)' }
  ];

  const focusAreas = [
    { id: 'full-body', label: 'Full Body' },
    { id: 'upper-body', label: 'Upper Body' },
    { id: 'lower-body', label: 'Lower Body' },
    { id: 'core', label: 'Core' },
    { id: 'cardio', label: 'Cardio' },
    { id: 'strength', label: 'Strength' },
    { id: 'flexibility', label: 'Flexibility' }
  ];

  let selectedEquipment: string[] = ['none'];
  let selectedFocusAreas: string[] = ['full-body'];

  function handleEquipmentChange(equipmentId: string, checked: boolean) {
    if (checked) {
      if (equipmentId === 'none') {
        selectedEquipment = ['none'];
      } else {
        selectedEquipment = [...selectedEquipment.filter(id => id !== 'none'), equipmentId];
      }
    } else {
      selectedEquipment = selectedEquipment.filter(id => id !== equipmentId);
      if (selectedEquipment.length === 0) {
        selectedEquipment = ['none'];
      }
    }
  }

  function handleSubmit() {
    dispatch('generate', {
      duration,
      location,
      equipment: selectedEquipment,
      intensity,
      focusAreas: selectedFocusAreas
    });
  }
</script>

<Card class="w-full max-w-2xl mx-auto">
  <CardHeader>
    <CardTitle>Generate Workout Plan</CardTitle>
    <CardDescription>
      Tell us about your preferences and available resources, and we'll create a personalized workout plan for you.
    </CardDescription>
  </CardHeader>
  <CardContent>
    {#if error}
      <Alert variant="destructive" class="mb-6">
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    {/if}

    <form class="space-y-6" on:submit|preventDefault={handleSubmit}>
      <div class="space-y-2">
        <Label>Duration (minutes)</Label>
        <div class="flex items-center gap-4">
          <Input
            type="number"
            min="15"
            max="120"
            step="5"
            bind:value={duration}
            class="w-32"
          />
          <span class="text-sm text-muted-foreground">minutes</span>
        </div>
      </div>

      <div class="space-y-2">
        <Label>Location</Label>
        <div class="flex flex-wrap gap-4">
          {#each ['anywhere', 'home', 'gym', 'outdoor'] as loc}
            <div class="flex items-center space-x-2">
              <input
                type="radio"
                id={loc}
                name="location"
                value={loc}
                bind:group={location}
                class="radio"
              />
              <label for={loc} class="text-sm font-medium leading-none">
                {loc.charAt(0).toUpperCase() + loc.slice(1)}
              </label>
            </div>
          {/each}
        </div>
      </div>

      <div class="space-y-2">
        <Label>Intensity</Label>
        <div class="flex flex-wrap gap-4">
          {#each ['light', 'moderate', 'intense'] as level}
            <div class="flex items-center space-x-2">
              <input
                type="radio"
                id={level}
                name="intensity"
                value={level}
                bind:group={intensity}
                class="radio"
              />
              <label for={level} class="text-sm font-medium leading-none">
                {level.charAt(0).toUpperCase() + level.slice(1)}
              </label>
            </div>
          {/each}
        </div>
      </div>

      <div class="space-y-2">
        <Label>Available Equipment</Label>
        <div class="grid grid-cols-2 gap-4">
          {#each availableEquipment as equipment}
            <div class="flex items-center space-x-2">
              <Checkbox
                id={equipment.id}
                checked={selectedEquipment.includes(equipment.id)}
                onCheckedChange={(checked: boolean) => handleEquipmentChange(equipment.id, checked)}
              />
              <label
                for={equipment.id}
                class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
              >
                {equipment.label}
              </label>
            </div>
          {/each}
        </div>
      </div>

      <div class="space-y-2">
        <Label>Focus Areas</Label>
        <div class="grid grid-cols-2 gap-4">
          {#each focusAreas as area}
            <div class="flex items-center space-x-2">
              <Checkbox
                id={area.id}
                checked={selectedFocusAreas.includes(area.id)}
                onCheckedChange={(checked: boolean) => {
                  if (checked) {
                    selectedFocusAreas = [...selectedFocusAreas, area.id];
                  } else {
                    selectedFocusAreas = selectedFocusAreas.filter(id => id !== area.id);
                  }
                }}
              />
              <label
                for={area.id}
                class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
              >
                {area.label}
              </label>
            </div>
          {/each}
        </div>
      </div>

      <div class="flex justify-end space-x-2">
        <button
          type="button"
          class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2"
          on:click={() => dispatch('cancel')}
        >
          Cancel
        </button>
        <button
          type="submit"
          class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
          disabled={generating}
        >
          {#if generating}
            <svg class="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Generating...
          {:else}
            Generate Workout
          {/if}
        </button>
      </div>
    </form>
  </CardContent>
</Card> 