<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import { Button, Label, Input, Select } from 'flowbite-svelte';
    import type { UserProfile, UserProfileUpdate } from '$lib/types';
    import { api } from '$lib/api';

    export let profile: UserProfile;

    const dispatch = createEventDispatcher();
    let saving = false;
    let error: string | null = null;

    console.log(profile);

    // Form data
    let formData: UserProfileUpdate = {
        height: profile.height || undefined,
        weight: profile.weight || undefined,
        date_of_birth: profile.date_of_birth || undefined,
        gender: profile.gender || '',
        fitness_goals: profile.fitness_goals || [],
        preferred_workout_duration: profile.preferred_workout_duration || 60,
        preferred_workout_days: profile.preferred_workout_days || [],
        available_equipment: profile.available_equipment || []
    };

    const genderOptions = [
        { value: 'male', label: 'Male' },
        { value: 'female', label: 'Female' },
        { value: 'other', label: 'Other' },
        { value: 'prefer_not_to_say', label: 'Prefer not to say' }
    ];
    const fitnessGoalOptions = [
        'Weight Loss',
        'Muscle Gain',
        'Strength Training',
        'Endurance',
        'General Fitness',
        'Flexibility'
    ];
    const equipmentOptions = [
        'None',
        'Dumbbells',
        'Barbell',
        'Resistance Bands',
        'Pull-up Bar',
        'Yoga Mat',
        'Kettlebell',
        'Bench'
    ];
    const daysOfWeek = [
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday',
        'Sunday'
    ];

    async function handleSubmit() {
        try {
            saving = true;
            error = null;
            await api.put('/profiles/me', formData);
            dispatch('saved');
        } catch (e: any) {
            error = e.message || 'Failed to save profile';
        } finally {
            saving = false;
        }
    }
</script>

<form on:submit|preventDefault={handleSubmit} class="space-y-6">
    {#if error}
        <div class="text-red-500 mb-4">{error}</div>
    {/if}

    <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
        <!-- Height -->
        <div>
            <Label for="height">Height (cm)</Label>
            <input
                type="number"
                id="height"
                bind:value={formData.height}
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                placeholder="Enter your height"
            />
        </div>

        <!-- Weight -->
        <div>
            <Label for="weight">Weight (kg)</Label>
            <input
                type="number"
                id="weight"
                bind:value={formData.weight}
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                placeholder="Enter your weight"
            />
        </div>

        <!-- Date of Birth -->
        <div>
            <Label for="dob">Date of Birth</Label>
            <input
                type="date"
                id="dob"
                bind:value={formData.date_of_birth}
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
        </div>

        <!-- Gender -->
        <div>
            <Label for="gender">Gender</Label>
            <select
                id="gender"
                bind:value={formData.gender}
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            >
                <option value="">Choose option...</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
                <option value="prefer_not_to_say">Prefer not to say</option>
            </select>
        </div>
    </div>

    <!-- Fitness Goals -->
    <div>
        <Label>Fitness Goals</Label>
        <div class="grid grid-cols-2 md:grid-cols-3 gap-2">
            {#each fitnessGoalOptions as goal}
                <label class="flex items-center space-x-2">
                    <input
                        type="checkbox"
                        value={goal}
                        checked={formData.fitness_goals?.includes(goal)}
                        on:change={(e) => {
                            if (e.currentTarget.checked) {
                                formData.fitness_goals = [...(formData.fitness_goals || []), goal];
                            } else {
                                formData.fitness_goals = formData.fitness_goals?.filter(g => g !== goal);
                            }
                        }}
                    />
                    <span>{goal}</span>
                </label>
            {/each}
        </div>
    </div>

    <!-- Workout Preferences -->
    <div class="mt-6">
        <Label for="duration">Preferred Workout Duration (minutes)</Label>
        <input
            type="number"
            id="duration"
            bind:value={formData.preferred_workout_duration}
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            min="15"
            max="180"
            step="15"
        />
    </div>

    <div>
        <Label>Preferred Workout Days</Label>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-2">
            {#each daysOfWeek as day}
                <label class="flex items-center space-x-2">
                    <input
                        type="checkbox"
                        value={day}
                        checked={formData.preferred_workout_days?.includes(day)}
                        on:change={(e) => {
                            if (e.currentTarget.checked) {
                                formData.preferred_workout_days = [...(formData.preferred_workout_days || []), day];
                            } else {
                                formData.preferred_workout_days = formData.preferred_workout_days?.filter(d => d !== day);
                            }
                        }}
                    />
                    <span>{day}</span>
                </label>
            {/each}
        </div>
    </div>

    <!-- Available Equipment -->
    <div>
        <Label>Available Equipment</Label>
        <div class="grid grid-cols-2 md:grid-cols-3 gap-2">
            {#each equipmentOptions as equipment}
                <label class="flex items-center space-x-2">
                    <input
                        type="checkbox"
                        value={equipment}
                        checked={formData.available_equipment?.includes(equipment)}
                        on:change={(e) => {
                            if (e.currentTarget.checked) {
                                formData.available_equipment = [...(formData.available_equipment || []), equipment];
                            } else {
                                formData.available_equipment = formData.available_equipment?.filter(eq => eq !== equipment);
                            }
                        }}
                    />
                    <span>{equipment}</span>
                </label>
            {/each}
        </div>
    </div>

    <div class="flex justify-end mt-6">
        <button 
            type="submit" 
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            disabled={saving}
        >
            {saving ? 'Saving...' : 'Save Changes'}
        </button>
    </div>
</form> 