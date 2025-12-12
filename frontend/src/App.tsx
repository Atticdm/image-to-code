import { useEffect, useRef } from "react";
import { generateCode } from "./generateCode";
import SettingsDialog from "./components/settings/SettingsDialog";
import { AppState, CodeGenerationParams, EditorTheme, Settings } from "./types";
import { IS_RUNNING_ON_CLOUD } from "./config";
import { PicoBadge } from "./components/messages/PicoBadge";
import { OnboardingNote } from "./components/messages/OnboardingNote";
import { usePersistedState } from "./hooks/usePersistedState";
import TermsOfServiceDialog from "./components/TermsOfServiceDialog";
import { USER_CLOSE_WEB_SOCKET_CODE } from "./constants";
import { extractHistory } from "./components/history/utils";
import toast from "react-hot-toast";
import useBrowserTabIndicator from "./hooks/useBrowserTabIndicator";
import { useAppStore } from "./store/app-store";
import { useProjectStore } from "./store/project-store";
import Sidebar from "./components/sidebar/Sidebar";
import PreviewPane from "./components/preview/PreviewPane";
import StartPane from "./components/start-pane/StartPane";
import { Commit } from "./components/commits/types";
import { createCommit } from "./components/commits/utils";
import { GitHubLogoIcon } from "@radix-ui/react-icons";
import { useRegistryStore } from "./store/registry-store";

function App() {
  const {
    // Inputs
    inputMode,
    setInputMode,
    isImportedFromCode,
    setIsImportedFromCode,
    referenceImages,
    setReferenceImages,
    initialPrompt,
    setInitialPrompt,

    head,
    commits,
    addCommit,
    removeCommit,
    setHead,
    appendCommitCode,
    setCommitCode,
    updateSelectedVariantIndex,
    resetCommits,
    resetHead,
    updateVariantStatus,
    resizeVariants,

    // Outputs
    appendExecutionConsole,
    resetExecutionConsoles,
  } = useProjectStore();

  const {
    disableInSelectAndEditMode,
    setUpdateInstruction,
    updateImages,
    setUpdateImages,
    appState,
    setAppState,
  } = useAppStore();

  // Settings
  const [settings, setSettings] = usePersistedState<Settings>(
    {
      openAiApiKey: null,
      openAiBaseURL: null,
      anthropicApiKey: null,
      geminiApiKey: null,
      screenshotOneApiKey: null,
      isImageGenerationEnabled: true,
      editorTheme: EditorTheme.COBALT,
      generatedCodeConfig: "html_tailwind",
      codeGenerationModel: "gpt-5",
      analysisModel: "claude-opus-4-5-20251101", // Default analysis model
      isTermOfServiceAccepted: false,
    },
    "setting"
  );

  const wsRef = useRef<WebSocket>(null);
  const requestByCommitHashRef = useRef<Record<string, CodeGenerationParams>>({});
  const { registry, loadRegistry } = useRegistryStore();

  const showSelectAndEditFeature =
    settings.generatedCodeConfig === "html_tailwind" ||
    settings.generatedCodeConfig === "html_css";

  useBrowserTabIndicator(appState === AppState.CODING);

  useEffect(() => {
    loadRegistry();
  }, [loadRegistry]);

  useEffect(() => {
    if (!registry) return;

    // If persisted settings contain values that the backend no longer offers, reset to defaults.
    const modelIds = new Set(registry.models.map((m) => m.id));
    const stackIds = new Set(registry.stacks.map((s) => s.id));

    setSettings((prev) => {
      const next = { ...prev };

      if (!next.generatedCodeConfig || !stackIds.has(next.generatedCodeConfig)) {
        next.generatedCodeConfig =
          (registry.defaults.generatedCodeConfig as string) || "html_tailwind";
      }
      if (!next.codeGenerationModel || !modelIds.has(next.codeGenerationModel)) {
        next.codeGenerationModel =
          (registry.defaults.codeGenerationModel as string) || "gpt-5";
      }
      if (next.analysisModel && !modelIds.has(next.analysisModel)) {
        next.analysisModel = registry.defaults.analysisModel as string;
      }

      return next;
    });
  }, [registry, setSettings]);

  useEffect(() => {
    if (!settings.generatedCodeConfig) {
      setSettings((prev) => ({
        ...prev,
        generatedCodeConfig: "html_tailwind",
      }));
    }
  }, [settings.generatedCodeConfig, setSettings]);

  const reset = () => {
    setAppState(AppState.INITIAL);
    setUpdateInstruction("");
    setUpdateImages([]);
    disableInSelectAndEditMode();
    resetExecutionConsoles();
    resetCommits();
    resetHead();
    setInputMode("image");
    setReferenceImages([]);
    setIsImportedFromCode(false);
  };

  const regenerate = () => {
    // Regenerate always reruns the initial create flow and resets state.
    if (inputMode === "image" || inputMode === "video") {
      doCreate(referenceImages, inputMode);
    } else {
      doCreateFromText(initialPrompt);
    }
  };

  const cancelCodeGeneration = () => {
    wsRef.current?.close?.(USER_CLOSE_WEB_SOCKET_CODE);
  };

  const cancelCodeGenerationAndReset = (commit: Commit) => {
    if (commit.type === "ai_create") {
      reset();
    } else {
      removeCommit(commit.hash);
      const parentCommitHash = commit.parentHash;
      if (parentCommitHash) {
        setHead(parentCommitHash);
      } else {
        throw new Error("Parent commit not found");
      }
      setAppState(AppState.CODE_READY);
    }
  };

  function doGenerateCode(params: CodeGenerationParams) {
    resetExecutionConsoles();
    setAppState(AppState.CODING);
    const updatedParams = { ...params, ...settings };
    const baseCommitObject = {
      variants: Array(1).fill(null).map(() => ({ code: "" })),
    };
    const commitInputObject =
      params.generationType === "create"
        ? {
            ...baseCommitObject,
            type: "ai_create" as const,
            parentHash: null,
            inputs: params.prompt,
          }
        : {
            ...baseCommitObject,
            type: "ai_edit" as const,
            parentHash: head,
            inputs: params.history
              ? params.history[params.history.length - 1]
              : { text: "", images: [] },
          };

    const commit = createCommit(commitInputObject);
    addCommit(commit);
    setHead(commit.hash);
    requestByCommitHashRef.current[commit.hash] = params;

    generateCode(wsRef, updatedParams, {
      onChange: (token, variantIndex) => {
        appendCommitCode(commit.hash, variantIndex, token);
      },
      onSetCode: (code, variantIndex) => {
        setCommitCode(commit.hash, variantIndex, code);
      },
      onStatusUpdate: (line, variantIndex) =>
        appendExecutionConsole(variantIndex, line),
      onVariantComplete: (variantIndex) => {
        updateVariantStatus(commit.hash, variantIndex, "complete");
      },
      onVariantError: (variantIndex, error) => {
        updateVariantStatus(commit.hash, variantIndex, "error", error);
      },
      onVariantCount: (count) => {
        resizeVariants(commit.hash, count);
      },
      onCancel: () => {
        cancelCodeGenerationAndReset(commit);
      },
      onComplete: () => {
        setAppState(AppState.CODE_READY);
      },
    });
  }

  function generateAnotherOption() {
    if (appState === AppState.CODING) return;
    if (head === null) {
      toast.error("Nothing to regenerate yet.");
      return;
    }

    const commit = commits[head];
    if (!commit) return;

    const baseParams = requestByCommitHashRef.current[head];
    if (!baseParams) {
      toast.error("Missing generation context for this result.");
      return;
    }

    const maxOptions = 4;
    if (commit.variants.length >= maxOptions) {
      toast.error(`Max options reached (${maxOptions}).`);
      return;
    }

    const targetIndex = commit.variants.length;
    resizeVariants(head, targetIndex + 1);
    updateSelectedVariantIndex(head, targetIndex);
    setAppState(AppState.CODING);

    const updatedParams = { ...baseParams, ...settings };
    generateCode(wsRef, updatedParams, {
      onChange: (token) => {
        appendCommitCode(head, targetIndex, token);
      },
      onSetCode: (code) => {
        setCommitCode(head, targetIndex, code);
      },
      onStatusUpdate: (line) => appendExecutionConsole(targetIndex, line),
      onVariantComplete: () => {
        updateVariantStatus(head, targetIndex, "complete");
      },
      onVariantError: (_variantIndex, error) => {
        updateVariantStatus(head, targetIndex, "error", error);
      },
      onVariantCount: () => {
        // Ignore: this call is only for a single additional option.
      },
      onCancel: () => {
        updateVariantStatus(head, targetIndex, "cancelled");
        setAppState(AppState.CODE_READY);
      },
      onComplete: () => {
        setAppState(AppState.CODE_READY);
      },
    });
  }

  function doCreate(referenceImages: string[], inputMode: "image" | "video") {
    reset();
    setReferenceImages(referenceImages);
    setInputMode(inputMode);
    if (referenceImages.length > 0) {
      doGenerateCode({
        generationType: "create",
        inputMode,
        prompt: { text: "", images: [referenceImages[0]] },
      });
    }
  }

  function doCreateFromText(text: string) {
    reset();
    setInputMode("text");
    setInitialPrompt(text);
    doGenerateCode({
      generationType: "create",
      inputMode: "text",
      prompt: { text, images: [] },
    });
  }

  async function doUpdate(updateInstruction: string, selectedElement?: HTMLElement) {
    if (updateInstruction.trim() === "") {
      toast.error("Please include some instructions for AI on what to update.");
      return;
    }
    if (head === null) throw new Error("Update called with no head");

    let historyTree;
    try {
      historyTree = extractHistory(head, commits);
    } catch {
      throw new Error("Invalid version history");
    }

    let modifiedUpdateInstruction = updateInstruction;
    if (selectedElement) {
      modifiedUpdateInstruction =
        updateInstruction +
        " referring to this element specifically: " +
        selectedElement.outerHTML;
    }

    const updatedHistory = [
      ...historyTree,
      { text: modifiedUpdateInstruction, images: updateImages },
    ];

    doGenerateCode({
      generationType: "update",
      inputMode,
      prompt:
        inputMode === "text"
          ? { text: initialPrompt, images: [] }
          : { text: "", images: [referenceImages[0]] },
      history: updatedHistory,
      isImportedFromCode,
    });

    setUpdateInstruction("");
    setUpdateImages([]);
  }

  const handleTermDialogOpenChange = (open: boolean) => {
    setSettings((s) => ({ ...s, isTermOfServiceAccepted: !open }));
  };

  function setStack(stack: string) {
    setSettings((prev) => ({ ...prev, generatedCodeConfig: stack }));
  }

  function importFromCode(code: string, stack: string) {
    reset();
    setIsImportedFromCode(true);
    setStack(stack);
    const commit = createCommit({
      type: "code_create",
      parentHash: null,
      variants: [{ code }],
      inputs: null,
    });
    addCommit(commit);
    setHead(commit.hash);
    setAppState(AppState.CODE_READY);
  }

  return (
    <div className="flex flex-col h-screen bg-zinc-950 text-white font-sans selection:bg-blue-500/30">
      {IS_RUNNING_ON_CLOUD && <PicoBadge />}
      {IS_RUNNING_ON_CLOUD && (
        <TermsOfServiceDialog
          open={!settings.isTermOfServiceAccepted}
          onOpenChange={handleTermDialogOpenChange}
        />
      )}

      {/* Modern Header */}
      <header className="flex items-center justify-between px-6 py-3 border-b border-zinc-800 bg-zinc-950 z-50">
        <div className="flex items-center gap-2">
          <button onClick={reset} className="font-bold text-lg tracking-tight hover:opacity-80 transition-opacity">
            Image to Code
          </button>
        </div>
        
        <div className="flex items-center gap-4">
          <a
            href="https://github.com/Atticdm/image-to-code"
            target="_blank"
            rel="noopener noreferrer"
            className="text-zinc-400 hover:text-white transition-colors"
          >
            <GitHubLogoIcon className="w-5 h-5" />
          </a>
          <SettingsDialog settings={settings} setSettings={setSettings} />
        </div>
      </header>

      {/* Main Layout Area */}
      <div className="flex-1 overflow-hidden relative">
        {appState === AppState.INITIAL ? (
          /* Initial State - Centered Content */
          <div className="h-full overflow-y-auto">
            <StartPane
              doCreate={doCreate}
              importFromCode={importFromCode}
              settings={settings}
              setSettings={setSettings}
            />
          </div>
        ) : (
          /* Coding State - Split View */
          <div className="flex h-full">
            {/* Left Sidebar - History & Chat */}
            <aside className="w-[400px] flex flex-col border-r border-zinc-800 bg-zinc-900/50 backdrop-blur-sm z-40 transition-all duration-300 ease-in-out">
              <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
                {IS_RUNNING_ON_CLOUD && !settings.openAiApiKey && <OnboardingNote />}
                
                <Sidebar
                  showSelectAndEditFeature={showSelectAndEditFeature}
                  doUpdate={doUpdate}
                  regenerate={regenerate}
                  cancelCodeGeneration={cancelCodeGeneration}
                  generateAnotherOption={generateAnotherOption}
                />
              </div>
            </aside>

            {/* Right Panel - Preview & Code */}
            <main className="flex-1 relative bg-zinc-950 overflow-hidden">
               <PreviewPane doUpdate={doUpdate} reset={reset} settings={settings} />
            </main>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
