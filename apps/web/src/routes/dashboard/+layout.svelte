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
    nav_sign_out_error,

	nav_settings

  } from '$lib/paraglide/messages';

  let isMenuOpen = false;
  
  function toggleMenu() {
    isMenuOpen = !isMenuOpen;
  }

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

<div class="min-h-screen bg-background">
  <nav class="bg-card shadow-sm">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <div class="flex">
          <div class="flex-shrink-0 flex items-center">
            <span class="text-2xl font-bold text-primary">{nav_brand()}</span>
          </div>
          <div class="hidden md:ml-6 md:flex md:space-x-8">
            <a href="/dashboard" class="border-transparent text-muted-foreground hover:border-border hover:text-foreground inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
              {nav_dashboard()}
            </a>
            <a href="/dashboard/workouts" class="border-transparent text-muted-foreground hover:border-border hover:text-foreground inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
              {nav_workout()}
            </a>
            <a href="/dashboard/exercises" class="border-transparent text-muted-foreground hover:border-border hover:text-foreground inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
              {nav_exercises()}
            </a>
            <a 
              aria-disabled="true"
              class="border-transparent text-muted-foreground/40 cursor-not-allowed hover:border-transparent hover:text-muted-foreground/40 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
            >
              {nav_nutrition()}
            </a>
            <a 
              aria-disabled="true"
              class="border-transparent text-muted-foreground/40 cursor-not-allowed hover:border-transparent hover:text-muted-foreground/40 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
            >
              {nav_progress()}
            </a>
          </div>
        </div>
        
        <div class="flex items-center md:hidden">
          <button
            type="button"
            class="inline-flex items-center justify-center p-2 rounded-md text-muted-foreground hover:text-foreground hover:bg-accent focus:outline-none focus:ring-2 focus:ring-ring"
            on:click={toggleMenu}
          >
            <span class="sr-only">Open main menu</span>
            <svg
              class:hidden={isMenuOpen}
              class="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
            <svg
              class:hidden={!isMenuOpen}
              class="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="hidden md:flex md:items-center md:space-x-4">
          <LanguageSwitcher />
          <a 
            href="/dashboard/settings"
            class="text-muted-foreground hover:text-foreground px-3 py-2 rounded-md text-sm font-medium"
          >
            {nav_settings()}
          </a>
          <button
            on:click={handleSignOut}
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-primary-foreground bg-primary hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-ring"
          >
            {nav_sign_out()}
          </button>
        </div>
      </div>
    </div>

    <div class="md:hidden" class:hidden={!isMenuOpen}>
      <div class="pt-2 pb-3 space-y-1">
        <a
          href="/dashboard"
          class="block pl-3 pr-4 py-2 border-l-4 text-base font-medium border-transparent text-muted-foreground hover:bg-accent hover:border-border hover:text-foreground"
        >
          {nav_dashboard()}
        </a>
        <a
          href="/dashboard/workouts"
          class="block pl-3 pr-4 py-2 border-l-4 text-base font-medium border-transparent text-muted-foreground hover:bg-accent hover:border-border hover:text-foreground"
        >
          {nav_workout()}
        </a>
        <a
          href="/dashboard/exercises"
          class="block pl-3 pr-4 py-2 border-l-4 text-base font-medium border-transparent text-muted-foreground hover:bg-accent hover:border-border hover:text-foreground"
        >
          {nav_exercises()}
        </a>
        <span
          class="block pl-3 pr-4 py-2 border-l-4 text-base font-medium border-transparent text-muted-foreground/40 cursor-not-allowed"
        >
          {nav_nutrition()}
        </span>
        <span
          class="block pl-3 pr-4 py-2 border-l-4 text-base font-medium border-transparent text-muted-foreground/40 cursor-not-allowed"
        >
          {nav_progress()}
        </span>
        <a
          href="/dashboard/settings"
          class="block pl-3 pr-4 py-2 border-l-4 text-base font-medium border-transparent text-muted-foreground hover:bg-accent hover:border-border hover:text-foreground"
        >
          {nav_settings()}
        </a>
        <div class="pl-3 pr-4 py-2">
          <LanguageSwitcher />
        </div>
        <button
          on:click={handleSignOut}
          class="w-full text-left pl-3 pr-4 py-2 border-l-4 text-base font-medium border-transparent text-red-600 hover:bg-gray-50 hover:border-red-300"
        >
          {nav_sign_out()}
        </button>
      </div>
    </div>
  </nav>

  <slot />
</div> 