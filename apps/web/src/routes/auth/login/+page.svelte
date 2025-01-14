<script lang="ts">
  import { goto } from '$app/navigation';
  import { signIn } from '$lib/utils/auth';
  import { authStore } from '$lib/stores/auth';
  
  let email = '';
  let password = '';
  let error = '';
  let loading = false;
  
  async function handleSubmit(event: SubmitEvent) {
    event.preventDefault();
    if (loading) return;
    
    loading = true;
    error = '';
    
    try {
      const { user } = await signIn(email, password);
      authStore.set(user);
      loading = false; // Set loading to false before navigation
      window.location.href = '/dashboard'; // Use window.location.href for more reliable navigation
    } catch (err) {
      if (err instanceof Error) {
        error = err.message;
      } else {
        error = 'Login failed. Please try again.';
      }
      loading = false;
    }
  }
</script>

<div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
  <div class="max-w-md w-full space-y-8">
    <div>
      <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
        Sign in to your account
      </h2>
    </div>
    <form class="mt-8 space-y-6" on:submit|preventDefault={handleSubmit}>
      {#if error}
        <div class="rounded-md bg-red-50 p-4">
          <div class="text-sm text-red-700">{error}</div>
        </div>
      {/if}
      
      <div class="rounded-md shadow-sm -space-y-px">
        <div>
          <label for="email" class="sr-only">Email address</label>
          <input
            id="email"
            name="email"
            type="email"
            required
            bind:value={email}
            class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
            placeholder="Email address"
            disabled={loading}
          />
        </div>
        <div>
          <label for="password" class="sr-only">Password</label>
          <input
            id="password"
            name="password"
            type="password"
            required
            bind:value={password}
            class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
            placeholder="Password"
            disabled={loading}
          />
        </div>
      </div>

      <div>
        <button
          type="submit"
          class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
          disabled={loading}
        >
          {#if loading}
            Signing in...
          {:else}
            Sign in
          {/if}
        </button>
      </div>
      
      <div class="text-sm text-center">
        <a href="/auth/register" class="font-medium text-indigo-600 hover:text-indigo-500">
          Don't have an account? Sign up
        </a>
      </div>
    </form>
  </div>
</div> 