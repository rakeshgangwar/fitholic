<script lang="ts">
  import { authStore } from '$lib/stores/auth';
  import { signOut } from '$lib/utils/auth';
  import { goto } from '$app/navigation';
  import LanguageSwitcher from '$lib/components/LanguageSwitcher.svelte';
  import { 
    nav_brand,
    nav_dashboard,
    nav_workout,
    nav_exercises,
    nav_nutrition,
    nav_progress,
    nav_profile,
    nav_sign_out,
    nav_sign_out_error
  } from '$lib/paraglide/messages';

  async function handleSignOut() {
    try {
      await signOut();
      authStore.clear();
      await goto('/auth/login');
    } catch (err) {
      if (err instanceof Error) {
        console.error(nav_sign_out_error(), err.message);
      } else {
        console.error(nav_sign_out_error(), err);
      }
    }
  }
</script>

<div class="min-h-screen bg-gray-100">
  <nav class="bg-white shadow-sm">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <div class="flex">
          <div class="flex-shrink-0 flex items-center">
            <span class="text-2xl font-bold text-indigo-600">{nav_brand()}</span>
          </div>
          <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
            <a href="/dashboard" class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
              {nav_dashboard()}
            </a>
            <a href="/dashboard/workouts" class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
              {nav_workout()}
            </a>
            <a href="/dashboard/exercises" class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
              {nav_exercises()}
            </a>
            <a 
              aria-disabled="true"
              class="border-transparent text-gray-300 cursor-not-allowed hover:border-transparent hover:text-gray-300 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
            >
              {nav_nutrition()}
            </a>
            <a 
              aria-disabled="true"
              class="border-transparent text-gray-300 cursor-not-allowed hover:border-transparent hover:text-gray-300 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
            >
              {nav_progress()}
            </a>
          </div>
        </div>
        <div class="flex items-center space-x-4">
          <LanguageSwitcher />
          <a 
            href="/dashboard/profile"
            class="text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium"
          >
            {nav_profile()}
          </a>
          <button
            on:click={handleSignOut}
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            {nav_sign_out()}
          </button>
        </div>
      </div>
    </div>
  </nav>

  <slot />
</div> 