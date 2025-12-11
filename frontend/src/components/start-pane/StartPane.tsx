import React from "react";
import ImageUpload from "../ImageUpload";
import { UrlInputSection } from "../UrlInputSection";
import ImportCodeSection from "../ImportCodeSection";
import { Settings } from "../../types";
import { Stack } from "../../lib/stacks";
import { Badge } from "../ui/badge";

interface Props {
  doCreate: (images: string[], inputMode: "image" | "video") => void;
  importFromCode: (code: string, stack: Stack) => void;
  settings: Settings;
}

const StartPane: React.FC<Props> = ({ doCreate, importFromCode, settings }) => {
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
