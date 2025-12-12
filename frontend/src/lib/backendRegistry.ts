import { HTTP_BACKEND_URL } from "../config";

export type Provider = "openai" | "anthropic" | "gemini";

export type ModelId = string;
export type StackId = string;

export interface PublicModelInfo {
  id: ModelId;
  name: string;
  provider: Provider;
  supports_input_modes: string[];
  supports_generation_types: string[];
}

export interface PublicStackInfo {
  id: StackId;
  label: string;
  components: string[];
  in_beta: boolean;
}

export interface BackendRegistry {
  models: PublicModelInfo[];
  stacks: PublicStackInfo[];
  defaults: {
    generatedCodeConfig?: StackId | null;
    codeGenerationModel?: ModelId | null;
    analysisModel?: ModelId | null;
    [key: string]: string | null | undefined;
  };
  recommended: {
    codeGenerationModels?: ModelId[];
    analysisModels?: ModelId[];
    [key: string]: ModelId[] | undefined;
  };
}

export async function fetchBackendRegistry(): Promise<BackendRegistry> {
  const resp = await fetch(`${HTTP_BACKEND_URL}/models`);
  if (!resp.ok) {
    throw new Error(`Failed to load backend registry: ${resp.status}`);
  }
  return (await resp.json()) as BackendRegistry;
}

export function getStackLabelFromRegistry(
  registry: BackendRegistry | null,
  stackId: StackId
): string {
  const s = registry?.stacks?.find((x) => x.id === stackId);
  return s?.label ?? stackId;
}

export function getStackComponentsFromRegistry(
  registry: BackendRegistry | null,
  stackId: StackId
): string[] {
  const s = registry?.stacks?.find((x) => x.id === stackId);
  return s?.components ?? [];
}

export function getModelNameFromRegistry(
  registry: BackendRegistry | null,
  modelId: ModelId
): string {
  const m = registry?.models?.find((x) => x.id === modelId);
  return m?.name ?? modelId;
}

