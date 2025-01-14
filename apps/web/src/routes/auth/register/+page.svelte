<script lang="ts">
  import { enhance } from '$app/forms';
  import { goto } from '$app/navigation';
  import { signUp } from '$lib/utils/auth';
  import { toast } from 'svelte-sonner';
  
  import { Button } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '$lib/components/ui/card';
  import { Alert, AlertTitle, AlertDescription } from '$lib/components/ui/alert';
  import { AlertCircle } from 'lucide-svelte';
  
  let email = '';
  let password = '';
  let confirmPassword = '';
  let firstName = '';
  let lastName = '';
  let error = '';
  let loading = false;
  
  async function handleSubmit() {
    if (password !== confirmPassword) {
      error = 'Passwords do not match';
      toast.error(error);
      return;
    }
    
    loading = true;
    error = '';
    
    try {
      await signUp(email, password, firstName, lastName);
      toast.success('Account created successfully! Please sign in.');
      await goto('/auth/login?registered=true');
    } catch (err) {
      if (err instanceof Error) {
        error = err.message;
        toast.error(error);
      } else {
        error = 'Registration failed. Please try again.';
        toast.error(error);
      }
    } finally {
      loading = false;
    }
  }
</script>

<div class="min-h-screen flex items-center justify-center bg-background py-12 px-4 sm:px-6 lg:px-8">
  <Card class="w-full max-w-md">
    <CardHeader class="space-y-1">
      <CardTitle class="text-2xl font-bold text-center">Create an account</CardTitle>
      <CardDescription class="text-center">
        Enter your details to create your account
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

        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-2">
            <Label for="firstName">First name</Label>
            <Input
              id="firstName"
              type="text"
              placeholder="Enter your first name"
              required
              bind:value={firstName}
              disabled={loading}
            />
          </div>
          <div class="space-y-2">
            <Label for="lastName">Last name</Label>
            <Input
              id="lastName"
              type="text"
              placeholder="Enter your last name"
              required
              bind:value={lastName}
              disabled={loading}
            />
          </div>
        </div>

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
            placeholder="Create a password"
            required
            bind:value={password}
            disabled={loading}
          />
        </div>

        <div class="space-y-2">
          <Label for="confirmPassword">Confirm password</Label>
          <Input
            id="confirmPassword"
            type="password"
            placeholder="Confirm your password"
            required
            bind:value={confirmPassword}
            disabled={loading}
          />
        </div>

        <Button type="submit" class="w-full" disabled={loading}>
          {loading ? 'Creating account...' : 'Create account'}
        </Button>
      </form>
    </CardContent>

    <CardFooter>
      <div class="text-sm text-center w-full">
        <a href="/auth/login" class="text-primary hover:text-primary/90 font-medium">
          Already have an account? Sign in
        </a>
      </div>
    </CardFooter>
  </Card>
</div> 