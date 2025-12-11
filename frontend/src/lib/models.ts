// Keep in sync with backend (llm.py)
// Order here matches dropdown order
export enum CodeGenerationModel {
  GPT_4O_2024_11_20 = "gpt-4o-2024-11-20",
  CLAUDE_3_OPUS = "claude-3-opus-20240229",
  CLAUDE_3_SONNET = "claude-3-sonnet-20240229",
  GEMINI_1_5_PRO = "gemini-1.5-pro",
  GEMINI_2_0_FLASH = "gemini-2.0-flash",
}

// Will generate a static error if a model in the enum above is not in the descriptions
export const CODE_GENERATION_MODEL_DESCRIPTIONS: {
  [key in CodeGenerationModel]: { name: string; inBeta: boolean };
} = {
  "gpt-4o-2024-11-20": { name: "GPT-4o", inBeta: false },
  "claude-3-opus-20240229": { name: "Claude 3 Opus", inBeta: false },
  "claude-3-sonnet-20240229": { name: "Claude 3 Sonnet", inBeta: false },
  "gemini-1.5-pro": { name: "Gemini 1.5 Pro", inBeta: false },
  "gemini-2.0-flash": { name: "Gemini 2.0 Flash", inBeta: false },
};
