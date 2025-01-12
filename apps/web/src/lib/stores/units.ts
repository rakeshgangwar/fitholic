import { writable } from 'svelte/store';

type Units = 'metric' | 'imperial';

// Create a writable store for units
export const units = writable<Units>('metric');

// Helper functions for unit conversion
export const convertWeight = (value: number, from: Units, to: Units): number => {
    if (from === to) return value;
    return from === 'metric'
        ? value * 2.20462 // kg to lbs
        : value / 2.20462; // lbs to kg
};

export const convertHeight = (value: number, from: Units, to: Units): number => {
    if (from === to) return value;
    return from === 'metric'
        ? value * 0.393701 // cm to inches
        : value / 0.393701; // inches to cm
}; 