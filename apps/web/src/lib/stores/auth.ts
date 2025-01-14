import { writable, get } from 'svelte/store';
import type { User } from '$lib/utils/auth';
import { getCurrentUser, getStoredToken } from '$lib/utils/auth';
import { browser } from '$app/environment';

function createAuthStore() {
  const { subscribe, set } = writable<User | null>(null);
  let initialized = false;

  return {
    subscribe,
    set,
    init: async () => {
      if (initialized) return;
      
      try {
        if (browser && getStoredToken()) {
          const user = await getCurrentUser();
          if (user) {
            set(user);
          } else {
            set(null);
            if (browser) {
              localStorage.removeItem('token');
            }
          }
        } else {
          set(null);
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        set(null);
        if (browser) {
          localStorage.removeItem('token');
        }
      } finally {
        initialized = true;
      }
    },
    clear: () => {
      set(null);
      if (browser) {
        localStorage.removeItem('token');
      }
    },
    isAuthenticated: () => {
      return !!get({ subscribe }) && !!getStoredToken();
    }
  };
}

export const authStore = createAuthStore(); 