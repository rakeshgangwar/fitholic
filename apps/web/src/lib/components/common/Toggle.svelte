<!-- Custom Toggle Switch Component -->
<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    
    const dispatch = createEventDispatcher<{
        change: { checked: boolean };
    }>();
    
    export let checked = false;
    export let disabled = false;
    export let label = '';
    export let description = '';

    function handleChange(event: Event) {
        const target = event.target as HTMLInputElement;
        checked = target.checked;
        dispatch('change', { checked });
    }
</script>

<label class="relative inline-flex items-center cursor-pointer {disabled ? 'opacity-50 cursor-not-allowed' : ''}">
    <input 
        type="checkbox"
        class="sr-only peer"
        bind:checked
        {disabled}
        on:change={handleChange}
    />
    <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 dark:peer-focus:ring-indigo-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-indigo-600"></div>
    {#if label || description}
        <div class="ml-3">
            {#if label}
                <div class="text-sm font-medium text-gray-900">{label}</div>
            {/if}
            {#if description}
                <div class="text-sm text-gray-500">{description}</div>
            {/if}
        </div>
    {/if}
</label> 