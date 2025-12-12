import { create } from "zustand";
import { BackendRegistry, fetchBackendRegistry } from "../lib/backendRegistry";

type RegistryStatus = "idle" | "loading" | "ready" | "error";

interface RegistryStore {
  status: RegistryStatus;
  error: string | null;
  registry: BackendRegistry | null;
  loadRegistry: () => Promise<void>;
}

let inFlight: Promise<BackendRegistry> | null = null;

export const useRegistryStore = create<RegistryStore>((set, get) => ({
  status: "idle",
  error: null,
  registry: null,
  loadRegistry: async () => {
    const { status, registry } = get();
    if (status === "loading" || registry) return;

    set({ status: "loading", error: null });
    try {
      inFlight = inFlight ?? fetchBackendRegistry();
      const loaded = await inFlight;
      set({ registry: loaded, status: "ready", error: null });
    } catch (e) {
      inFlight = null;
      set({
        status: "error",
        error: e instanceof Error ? e.message : String(e),
      });
    }
  },
}));

