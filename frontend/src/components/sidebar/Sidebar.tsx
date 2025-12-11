import classNames from "classnames";
import { useAppStore } from "../../store/app-store";
import { useProjectStore } from "../../store/project-store";
import { AppState } from "../../types";
import SelectAndEditModeToggleButton from "../select-and-edit/SelectAndEditModeToggleButton";
import { Button } from "../ui/button";
import { Textarea } from "../ui/textarea";
import { useEffect, useRef, useState, useCallback } from "react";
import HistoryDisplay from "../history/HistoryDisplay";
import Variants from "../variants/Variants";
import UpdateImageUpload, { UpdateImagePreview } from "../UpdateImageUpload";
import { ReloadIcon, Cross2Icon } from "@radix-ui/react-icons";

interface SidebarProps {
  showSelectAndEditFeature: boolean;
  doUpdate: (instruction: string) => void;
  regenerate: () => void;
  cancelCodeGeneration: () => void;
}

function Sidebar({
  showSelectAndEditFeature,
  doUpdate,
  regenerate,
  cancelCodeGeneration,
}: SidebarProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [isErrorExpanded, setIsErrorExpanded] = useState(false);
  const [isDragging, setIsDragging] = useState(false);

  const { appState, updateInstruction, setUpdateInstruction, updateImages, setUpdateImages } = useAppStore();

  const fileToDataURL = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = (error) => reject(error);
      reader.readAsDataURL(file);
    });
  };

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files).filter(file => 
      file.type === 'image/png' || file.type === 'image/jpeg'
    );
    
    if (files.length > 0) {
      try {
        const newImagePromises = files.map(file => fileToDataURL(file));
        const newImages = await Promise.all(newImagePromises);
        setUpdateImages([...updateImages, ...newImages]);
      } catch (error) {
        console.error('Error reading files:', error);
      }
    }
  }, [updateImages, setUpdateImages]);

  const { inputMode, referenceImages, head, commits } = useProjectStore();

  const isSelectedVariantComplete =
    head &&
    commits[head] &&
    commits[head].variants[commits[head].selectedVariantIndex].status ===
      "complete";

  const isSelectedVariantError =
    head &&
    commits[head] &&
    commits[head].variants[commits[head].selectedVariantIndex].status ===
      "error";

  const selectedVariantErrorMessage =
    head &&
    commits[head] &&
    commits[head].variants[commits[head].selectedVariantIndex].errorMessage;

  useEffect(() => {
    if (
      (appState === AppState.CODE_READY || isSelectedVariantComplete) &&
      textareaRef.current
    ) {
      textareaRef.current.focus();
    }
  }, [appState, isSelectedVariantComplete]);

  useEffect(() => {
    setIsErrorExpanded(false);
  }, [head, commits[head || ""]?.selectedVariantIndex]);

  return (
    <div className="flex flex-col h-full gap-y-4">
      {/* Reference Image */}
      {referenceImages.length > 0 && (
        <div className="flex flex-col gap-2 p-4 border-b border-zinc-800 bg-zinc-900/30">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-500">
            {inputMode === "video" ? "Original Video" : "Reference"}
          </h3>
          <div className={classNames("relative rounded-lg overflow-hidden border border-zinc-700/50", {
            "ring-2 ring-blue-500/20": appState === AppState.CODING,
          })}>
            {inputMode === "image" && (
              <img
                className="w-full object-cover max-h-48"
                src={referenceImages[0]}
                alt="Reference"
              />
            )}
            {inputMode === "video" && (
              <video
                muted
                autoPlay
                loop
                className="w-full object-cover max-h-48"
                src={referenceImages[0]}
              />
            )}
            {appState === AppState.CODING && (
               <div className="absolute inset-0 bg-blue-500/10 animate-pulse pointer-events-none" />
            )}
          </div>
        </div>
      )}

      {/* Variants Selection */}
      <div className="px-4">
          <Variants />
      </div>

      {/* History Feed */}
      <div className="flex-1 overflow-y-auto min-h-0 px-4">
        <HistoryDisplay shouldDisableReverts={appState === AppState.CODING} />
      </div>

      {/* Generation Controls */}
      {appState === AppState.CODING && !isSelectedVariantComplete && (
         <div className="p-4 border-t border-zinc-800 bg-zinc-900/50">
            <Button
              onClick={cancelCodeGeneration}
              variant="destructive"
              className="w-full flex items-center justify-center gap-2"
            >
              <Cross2Icon /> Cancel Generation
            </Button>
            {inputMode === "video" && (
              <div className="text-xs text-yellow-500 mt-2 text-center bg-yellow-500/10 p-2 rounded border border-yellow-500/20">
                Video processing takes 3-4 minutes.
              </div>
            )}
         </div>
      )}

      {/* Error Message */}
      {isSelectedVariantError && (
        <div className="p-4 mx-4 bg-red-500/10 border border-red-500/20 rounded-lg">
           <p className="text-red-400 text-sm font-medium mb-1">Generation Failed</p>
           <p className="text-red-300 text-xs font-mono break-all">
             {selectedVariantErrorMessage?.slice(0, 100)}...
           </p>
        </div>
      )}

      {/* Update Input (Bottom Sticky) */}
      {(appState === AppState.CODE_READY || isSelectedVariantComplete) && !isSelectedVariantError && (
        <div 
          className="p-4 border-t border-zinc-800 bg-zinc-900 mt-auto"
          onDragEnter={() => setIsDragging(true)}
          onDragLeave={(e) => {
             if (!e.currentTarget.contains(e.relatedTarget as Node)) setIsDragging(false);
          }}
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDrop}
        >
          <div className="relative flex flex-col gap-2">
            {isDragging && (
                <div className="absolute inset-0 bg-blue-500/20 border-2 border-dashed border-blue-500 rounded-lg z-10 flex items-center justify-center backdrop-blur-sm">
                   <p className="text-blue-200 font-medium">Drop update images</p>
                </div>
            )}
            
            <UpdateImagePreview updateImages={updateImages} setUpdateImages={setUpdateImages} />
            
            <Textarea
              ref={textareaRef}
              placeholder="Describe changes (e.g., 'Make the header blue')..."
              className="min-h-[80px] bg-zinc-950 border-zinc-800 focus:border-zinc-600 focus:ring-1 focus:ring-zinc-600 resize-none text-sm"
              onChange={(e) => setUpdateInstruction(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  doUpdate(updateInstruction);
                }
              }}
              value={updateInstruction}
            />
            
            <div className="flex justify-between items-center">
              <div className="flex gap-2">
                 <UpdateImageUpload updateImages={updateImages} setUpdateImages={setUpdateImages} />
                 {showSelectAndEditFeature && <SelectAndEditModeToggleButton />}
              </div>
              
              <div className="flex gap-2">
                  <Button
                    onClick={regenerate}
                    variant="ghost"
                    size="sm"
                    className="text-zinc-400 hover:text-white"
                    title="Regenerate current step"
                  >
                    <ReloadIcon className="w-4 h-4" />
                  </Button>
                  <Button
                    onClick={() => doUpdate(updateInstruction)}
                    size="sm"
                    className="bg-white text-black hover:bg-zinc-200"
                    disabled={!updateInstruction.trim() && updateImages.length === 0}
                  >
                    Update
                  </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Sidebar;
