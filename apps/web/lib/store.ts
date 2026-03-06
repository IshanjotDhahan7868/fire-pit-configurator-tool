"use client";
import { create } from "zustand";

export type ConfigState = {
  shape: "round" | "square" | "rectangular";
  size_preset: string;
  material: string;
  finish: string;
  fuel_type: string;
  burner: string;
  media: string;
  ignition: string;
  accessories: string[];
};

type Store = {
  config: ConfigState;
  setField: (field: keyof ConfigState, value: string | string[]) => void;
};

const defaultConfig: ConfigState = {
  shape: "round",
  size_preset: "medium",
  material: "steel",
  finish: "matte-black",
  fuel_type: "wood",
  burner: "none",
  media: "lava_rock",
  ignition: "manual",
  accessories: []
};

export const useConfigStore = create<Store>((set) => ({
  config: defaultConfig,
  setField: (field, value) =>
    set((state) => ({ config: { ...state.config, [field]: value as never } }))
}));
