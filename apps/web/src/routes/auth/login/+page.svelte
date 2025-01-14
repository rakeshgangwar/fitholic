<script lang="ts">
  import { enhance } from '$app/forms';
  import { goto } from '$app/navigation';
  import { signIn } from '$lib/utils/auth';
  import { toast } from 'svelte-sonner';
  import { theme } from '$lib/stores/theme';
  import { onMount } from 'svelte';
  
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '$lib/components/ui/card';
  import { Alert, AlertTitle, AlertDescription } from '$lib/components/ui/alert';
  import { AlertCircle, Moon, Sun } from 'lucide-svelte';
  import { cn } from '$lib/utils';
  
  let email = '';
  let password = '';
  let error = '';
  let loading = false;
  let currentTheme: 'light' | 'dark' = 'light';
  
  onMount(() => {
    // Initialize theme from localStorage or default to light
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | null;
    currentTheme = savedTheme || 'light';
    document.documentElement.classList.add(currentTheme);
    theme.set(currentTheme);
  });
  
  // Subscribe to theme changes
  theme.subscribe(value => {
    if (value === 'light' || value === 'dark') {
      currentTheme = value;
      localStorage.setItem('theme', value);
    }
  });
  
  // Toggle theme locally without updating profile
  function toggleTheme() {
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.classList.remove('light', 'dark');
    document.documentElement.classList.add(newTheme);
    theme.set(newTheme);
  }
  
  async function handleSubmit() {
    loading = true;
    error = '';
    
    try {
      await signIn(email, password);
      window.location.href = '/dashboard';
    } catch (err) {
      if (err instanceof Error) {
        error = err.message;
        toast.error(error);
      } else {
        error = 'Login failed. Please try again.';
        toast.error(error);
      }
    } finally {
      loading = false;
    }
  }
</script>

<svelte:head>
  {@html `
    <script>
      const theme = localStorage.getItem('theme') || 'light';
      document.documentElement.classList.remove('light', 'dark');
      document.documentElement.classList.add(theme);
    </script>
  `}
</svelte:head>

<div class="min-h-screen flex items-center justify-center bg-background py-12 px-4 sm:px-6 lg:px-8">
  <div class="fixed top-4 right-4">
    <button
      type="button"
      class={cn(
        "inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 hover:bg-accent hover:text-accent-foreground h-10 w-10",
        "bg-transparent"
      )}
      on:click={toggleTheme}
    >
      <Sun class="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
      <Moon class="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
      <span class="sr-only">Toggle theme</span>
    </button>
  </div>
  
  <Card class="w-full max-w-md">
    <CardHeader class="space-y-1">
      <CardTitle class="text-2xl font-bold text-center">Welcome back</CardTitle>
      <CardDescription class="text-center">
        Sign in to your account to continue
      </CardDescription>
    </CardHeader>

    <CardContent>
      <form class="space-y-4" on:submit|preventDefault={handleSubmit}>
        {#if error}
          <Alert variant="destructive">
            <AlertCircle class="h-4 w-4" />
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        {/if}

        <div class="space-y-2">
          <Label for="email">Email</Label>
          <Input
            id="email"
            type="email"
            placeholder="Enter your email"
            required
            bind:value={email}
            disabled={loading}
          />
        </div>

        <div class="space-y-2">
          <Label for="password">Password</Label>
          <Input
            id="password"
            type="password"
            placeholder="Enter your password"
            required
            bind:value={password}
            disabled={loading}
          />
        </div>

        <button
          type="submit"
          class={cn(
            "inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2",
            "w-full"
          )}
          disabled={loading}
        >
          {loading ? 'Signing in...' : 'Sign in'}
        </button>
      </form>
    </CardContent>

    <CardFooter>
      <div class="text-sm text-center w-full">
        <a href="/auth/register" class="text-primary hover:text-primary/90 font-medium">
          Don't have an account? Sign up
        </a>
      </div>
    </CardFooter>
  </Card>
</div> 