import React from "react";
import ImageUpload from "../ImageUpload";
import { UrlInputSection } from "../UrlInputSection";
import ImportCodeSection from "../ImportCodeSection";
import { Settings } from "../../types";
import { Badge } from "../ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger } from "../ui/select";
import { Label } from "../ui/label";
import { useRegistryStore } from "../../store/registry-store";
import { getModelNameFromRegistry } from "../../lib/backendRegistry";

interface Props {
  doCreate: (images: string[], inputMode: "image" | "video") => void;
  importFromCode: (code: string, stack: string) => void;
  settings: Settings;
  setSettings: React.Dispatch<React.SetStateAction<Settings>>;
}

const StartPane: React.FC<Props> = ({ doCreate, importFromCode, settings, setSettings }) => {
  const { registry } = useRegistryStore();
  const codeModelOptions =
    registry?.recommended?.codeGenerationModels?.length
      ? registry.recommended.codeGenerationModels
      : registry?.models?.map((m) => m.id) ?? [];
  const analysisModelOptions =
    registry?.recommended?.analysisModels?.length
      ? registry.recommended.analysisModels
      : registry?.models?.map((m) => m.id) ?? [];

  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-4rem)] p-4 animate-in fade-in duration-700">
      <div className="max-w-3xl w-full flex flex-col items-center gap-y-8">
        {/* Header Section */}
        <div className="text-center space-y-4">
          <Badge variant="secondary" className="mb-2 px-3 py-1 text-xs uppercase tracking-wider">
            AI-Powered
          </Badge>
          <h1 className="text-4xl md:text-6xl font-bold tracking-tight bg-gradient-to-r from-white to-zinc-400 bg-clip-text text-transparent">
            Image to Code
          </h1>
          <p className="text-lg text-zinc-400 max-w-lg mx-auto leading-relaxed">
            Convert screenshots, mockups, and designs into clean, functional code instantly.
          </p>
        </div>

        {/* Model Selection Card */}
        <div className="w-full bg-zinc-900/30 border border-zinc-800/50 rounded-xl p-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Code Generation Model */}
            <div className="space-y-2">
              <Label className="text-sm text-zinc-400">Code Generation Model</Label>
              <Select
                value={settings.codeGenerationModel}
                disabled={codeModelOptions.length === 0}
                onValueChange={(value) =>
                  setSettings((s) => ({
                    ...s,
                    codeGenerationModel: value,
                  }))
                }
              >
                <SelectTrigger className="w-full bg-zinc-900/50 border-zinc-700 hover:border-zinc-600 transition-colors">
                  {getModelNameFromRegistry(registry, settings.codeGenerationModel) ||
                    "Select model"}
                </SelectTrigger>
                <SelectContent>
                  {codeModelOptions.map((model) => (
                    <SelectItem key={model} value={model}>
                      {getModelNameFromRegistry(registry, model)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Analysis Model (for element extraction) */}
            <div className="space-y-2">
              <Label className="text-sm text-zinc-400">
                Analysis Model
                <span className="ml-2 text-xs text-zinc-500">(element extraction)</span>
              </Label>
              <Select
                value={settings.analysisModel || "none"}
                disabled={analysisModelOptions.length === 0}
                onValueChange={(value) =>
                  setSettings((s) => ({
                    ...s,
                    analysisModel: value && value !== "none" ? value : null,
                  }))
                }
              >
                <SelectTrigger className="w-full bg-zinc-900/50 border-zinc-700 hover:border-zinc-600 transition-colors">
                  {settings.analysisModel
                    ? getModelNameFromRegistry(registry, settings.analysisModel)
                    : "Standard (no extraction)"}
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">Standard (no extraction)</SelectItem>
                  {analysisModelOptions.map((model) => (
                    <SelectItem key={model} value={model}>
                      {getModelNameFromRegistry(registry, model)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          
          {settings.analysisModel && (
            <p className="mt-3 text-xs text-emerald-400/80 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              Element extraction enabled - original design elements will be preserved
            </p>
          )}
        </div>

        {/* Main Action Card */}
        <div className="w-full bg-zinc-900/50 border border-zinc-800 rounded-2xl p-2 shadow-2xl backdrop-blur-sm">
          <div className="bg-zinc-950/80 rounded-xl border border-zinc-800/50 p-8 flex flex-col gap-y-6">
            <ImageUpload setReferenceImages={doCreate} />
            
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t border-zinc-800" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-zinc-950 px-2 text-zinc-500">Or start with</span>
              </div>
            </div>

            <div className="flex flex-col md:flex-row gap-4 justify-center">
              <UrlInputSection
                doCreate={doCreate}
                screenshotOneApiKey={settings.screenshotOneApiKey}
              />
            </div>
          </div>
        </div>

        {/* Footer/Alternative */}
        <div className="text-sm text-zinc-500">
          <ImportCodeSection importFromCode={importFromCode} />
        </div>
      </div>
    </div>
  );
};

export default StartPane;
