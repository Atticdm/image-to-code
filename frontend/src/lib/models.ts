// Keep in sync with backend (llm.py)
// Order here matches dropdown order
export enum CodeGenerationModel {
  GPT_5 = "gpt-5",
  GPT_5_TURBO = "gpt-5-turbo",
  CLAUDE_4_5_OPUS_2025_11_01 = "claude-opus-4-5-20251101",
  CLAUDE_4_5_SONNET_2025_11_01 = "claude-sonnet-4-5-20251101",
  GEMINI_3_PRO = "gemini-3-pro-preview",
  GPT_4_1_2025_04_14 = "gpt-4.1-2025-04-14",
  GPT_4O_2024_05_13 = "gpt-4o-2024-05-13",
}

// Will generate a static error if a model in the enum above is not in the descriptions
export const CODE_GENERATION_MODEL_DESCRIPTIONS: {
  [key in CodeGenerationModel]: { name: string; inBeta: boolean };
} = {
  "gpt-5": { name: "GPT-5", inBeta: false },
  "gpt-5-turbo": { name: "GPT-5 Turbo", inBeta: false },
  "claude-opus-4-5-20251101": { name: "Claude Opus 4.5", inBeta: false },
  "claude-sonnet-4-5-20251101": { name: "Claude Sonnet 4.5", inBeta: false },
  "gemini-3-pro-preview": { name: "Gemini 3 Pro", inBeta: false },
  "gpt-4.1-2025-04-14": { name: "GPT-4.1", inBeta: false },
  "gpt-4o-2024-05-13": { name: "GPT-4o", inBeta: false },
};
