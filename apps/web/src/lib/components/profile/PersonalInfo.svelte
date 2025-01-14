<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import type { UserProfile, UserProfileUpdate } from '$lib/types';
    import { api } from '$lib/api';
    import { cn } from '$lib/utils';
    
    import { Input } from '$lib/components/ui/input';
    import { Label } from '$lib/components/ui/label';
    import { Button } from '$lib/components/ui/button';
    import { Checkbox } from '$lib/components/ui/checkbox';
    import { toast } from 'svelte-sonner';
    import { Select, SelectTrigger, SelectContent, SelectItem } from '$lib/components/ui/select';
    import { Alert, AlertTitle, AlertDescription } from '$lib/components/ui/alert';
    import { Calendar } from '$lib/components/ui/calendar';
    import * as Popover from '$lib/components/ui/popover';
    import { AlertCircle, CalendarIcon } from 'lucide-svelte';
    import { DateFormatter, type DateValue, getLocalTimeZone, parseDate, today } from '@internationalized/date';

    export let profile: UserProfile;

    const dispatch = createEventDispatcher();
    let saving = false;
    let error: string | null = null;

    const df = new DateFormatter('en-US', {
        dateStyle: 'long'
    });

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

    let dateValue: DateValue | undefined = formData.date_of_birth ? parseDate(formData.date_of_birth) : undefined;

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

    async function handleSubmit(event: SubmitEvent) {
        event.preventDefault();
        try {
            saving = true;
            error = null;
            await api.put('/profiles/me', formData);
            toast.success('Profile updated successfully');
            dispatch('saved');
        } catch (e: any) {
            error = e.message || 'Failed to save profile';
            toast.error(error);
        } finally {
            saving = false;
        }
    }
</script>

<form class="space-y-8" on:submit={handleSubmit}>

    <!-- Basic Information Section -->
    <div class="space-y-6">
        <div class="border-b pb-2">
            <h3 class="text-lg font-medium">Basic Information</h3>
            <p class="text-sm text-muted-foreground">Your personal measurements and details.</p>
        </div>
        
        <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <!-- Height -->
            <div class="space-y-2">
                <Label for="height">Height (cm)</Label>
                <Input 
                    type="number" 
                    id="height"
                    bind:value={formData.height}
                    placeholder="Enter your height"
                />
            </div>

            <!-- Weight -->
            <div class="space-y-2">
                <Label for="weight">Weight (kg)</Label>
                <Input 
                    type="number" 
                    id="weight"
                    bind:value={formData.weight}
                    placeholder="Enter your weight"
                />
            </div>

            <!-- Date of Birth -->
            <div class="space-y-2">
                <Label>Date of Birth</Label>
                <div>
                    <Popover.Root>
                        <Popover.Trigger>
                            <div>
                                <Button
                                    variant="outline"
                                    class={cn(
                                        "w-full justify-start text-left font-normal",
                                        !dateValue && "text-muted-foreground"
                                    )}
                                >
                                    <CalendarIcon class="mr-2 h-4 w-4" />
                                    {dateValue ? df.format(dateValue.toDate(getLocalTimeZone())) : "Pick a date"}
                                </Button>
                            </div>
                        </Popover.Trigger>
                        <Popover.Content class="w-auto p-0" align="start">
                            <Calendar 
                                value={dateValue}
                                onValueChange={(value: DateValue) => {
                                    dateValue = value;
                                    if (value) {
                                        formData.date_of_birth = value.toString();
                                    } else {
                                        formData.date_of_birth = undefined;
                                    }
                                }}
                                maxValue={today(getLocalTimeZone())}
                            />
                        </Popover.Content>
                    </Popover.Root>
                </div>
            </div>

            <!-- Gender -->
            <div class="space-y-2">
                <Label for="gender">Gender</Label>
                <Select bind:value={formData.gender}>
                    <SelectTrigger class="w-full">
                        <span class="text-muted-foreground">{formData.gender || 'Choose option...'}</span>
                    </SelectTrigger>
                    <SelectContent>
                        {#each genderOptions as option}
                            <SelectItem value={option.value}>{option.label}</SelectItem>
                        {/each}
                    </SelectContent>
                </Select>
            </div>
        </div>
    </div>

    <!-- Fitness Goals Section -->
    <div class="space-y-6">
        <div class="border-b pb-2">
            <h3 class="text-lg font-medium">Fitness Goals</h3>
            <p class="text-sm text-muted-foreground">Select your fitness objectives and preferences.</p>
        </div>

        <div class="space-y-4">
            <div class="space-y-4">
                <Label>What are your fitness goals?</Label>
                <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {#each fitnessGoalOptions as goal}
                        <div class="flex items-center space-x-2">
                            <Checkbox
                                id={`goal-${goal}`}
                                checked={formData.fitness_goals?.includes(goal)}
                                onCheckedChange={(checked: boolean) => {
                                    if (checked) {
                                        formData.fitness_goals = [...(formData.fitness_goals || []), goal];
                                    } else {
                                        formData.fitness_goals = formData.fitness_goals?.filter((g: string) => g !== goal);
                                    }
                                }}
                            />
                            <Label for={`goal-${goal}`} class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                                {goal}
                            </Label>
                        </div>
                    {/each}
                </div>
            </div>

            <!-- Workout Duration -->
            <div class="space-y-2 pt-4">
                <Label for="duration">Preferred Workout Duration</Label>
                <p class="text-sm text-muted-foreground pb-2">How long do you prefer your workouts to be?</p>
                <Input 
                    type="number"
                    id="duration"
                    bind:value={formData.preferred_workout_duration}
                    min="15"
                    max="180"
                    step="15"
                    class="max-w-[200px]"
                />
                <p class="text-sm text-muted-foreground">Minutes (15-180)</p>
            </div>
        </div>
    </div>

    <!-- Schedule & Equipment Section -->
    <div class="space-y-6">
        <div class="border-b pb-2">
            <h3 class="text-lg font-medium">Schedule & Equipment</h3>
            <p class="text-sm text-muted-foreground">Your workout schedule and available equipment.</p>
        </div>

        <div class="space-y-6">
            <!-- Workout Days -->
            <div class="space-y-4">
                <Label>Preferred Workout Days</Label>
                <p class="text-sm text-muted-foreground">Select the days you're available to work out.</p>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {#each daysOfWeek as day}
                        <div class="flex items-center space-x-2">
                            <Checkbox
                                id={`day-${day}`}
                                checked={formData.preferred_workout_days?.includes(day)}
                                onCheckedChange={(checked: boolean) => {
                                    if (checked) {
                                        formData.preferred_workout_days = [...(formData.preferred_workout_days || []), day];
                                    } else {
                                        formData.preferred_workout_days = formData.preferred_workout_days?.filter((d: string) => d !== day);
                                    }
                                }}
                            />
                            <Label for={`day-${day}`} class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                                {day}
                            </Label>
                        </div>
                    {/each}
                </div>
            </div>

            <!-- Equipment -->
            <div class="space-y-4">
                <Label>Available Equipment</Label>
                <p class="text-sm text-muted-foreground">What equipment do you have access to?</p>
                <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {#each equipmentOptions as equipment}
                        <div class="flex items-center space-x-2">
                            <Checkbox
                                id={`equipment-${equipment}`}
                                checked={formData.available_equipment?.includes(equipment)}
                                onCheckedChange={(checked: boolean) => {
                                    if (checked) {
                                        formData.available_equipment = [...(formData.available_equipment || []), equipment];
                                    } else {
                                        formData.available_equipment = formData.available_equipment?.filter((eq: string) => eq !== equipment);
                                    }
                                }}
                            />
                            <Label for={`equipment-${equipment}`} class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                                {equipment}
                            </Label>
                        </div>
                    {/each}
                </div>
            </div>
        </div>
    </div>

    <div class="flex justify-end pt-6">
        <Button type="submit" disabled={saving}>
            {saving ? 'Saving...' : 'Save Changes'}
        </Button>
    </div>
</form> 