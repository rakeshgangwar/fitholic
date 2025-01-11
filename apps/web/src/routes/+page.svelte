<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { authStore } from '$lib/stores/auth';

  onMount(async () => {
    if ($authStore) {
      await goto('/dashboard');
    } else {
      await goto('/auth/login');
    }
  });
</script>

<div class="min-h-screen flex items-center justify-center">
  <div class="text-center">
    <h1 class="text-2xl font-bold text-indigo-600">Redirecting...</h1>
  </div>
</div>
