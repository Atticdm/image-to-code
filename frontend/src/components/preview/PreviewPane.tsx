import { Tabs, TabsList, TabsTrigger, TabsContent } from "../ui/tabs";
import {
  FaUndo,
  FaDownload,
  FaDesktop,
  FaMobile,
  FaCode,
} from "react-icons/fa";
import { AppState, Settings } from "../../types";
import CodeTab from "./CodeTab";
import { Button } from "../ui/button";
import { useAppStore } from "../../store/app-store";
import { useProjectStore } from "../../store/project-store";
import { extractHtml } from "./extractHtml";
import PreviewComponent from "./PreviewComponent";
import { downloadCode } from "./download";

interface Props {
  doUpdate: (instruction: string) => void;
  reset: () => void;
  settings: Settings;
}

function PreviewPane({ doUpdate, reset, settings }: Props) {
  const { appState } = useAppStore();
  const { inputMode, head, commits } = useProjectStore();

  const currentCommit = head && commits[head] ? commits[head] : "";
  const currentCode = currentCommit
    ? currentCommit.variants[currentCommit.selectedVariantIndex].code
    : "";

  const previewCode =
    inputMode === "video" && appState === AppState.CODING
      ? extractHtml(currentCode)
      : currentCode;

  return (
    <div className="h-full flex flex-col bg-zinc-950/50">
      <Tabs defaultValue="desktop" className="flex flex-col h-full w-full">
        <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800 bg-zinc-900/50">
          
          {/* View Toggle */}
          <TabsList className="bg-zinc-950 border border-zinc-800">
            <TabsTrigger value="desktop" className="data-[state=active]:bg-zinc-800 data-[state=active]:text-white text-zinc-400">
              <FaDesktop className="mr-2" /> Desktop
            </TabsTrigger>
            <TabsTrigger value="mobile" className="data-[state=active]:bg-zinc-800 data-[state=active]:text-white text-zinc-400">
              <FaMobile className="mr-2" /> Mobile
            </TabsTrigger>
            <TabsTrigger value="code" className="data-[state=active]:bg-zinc-800 data-[state=active]:text-white text-zinc-400">
              <FaCode className="mr-2" /> Code
            </TabsTrigger>
          </TabsList>

          {/* Actions */}
          <div className="flex items-center gap-2">
            {appState === AppState.CODE_READY && (
              <>
                <Button
                  onClick={reset}
                  variant="ghost"
                  size="sm"
                  className="text-zinc-400 hover:text-white hover:bg-zinc-800"
                >
                  <FaUndo className="mr-2" /> Reset
                </Button>
                <Button
                  onClick={() => downloadCode(previewCode)}
                  size="sm"
                  className="bg-zinc-100 text-zinc-900 hover:bg-white"
                >
                  <FaDownload className="mr-2" /> Export
                </Button>
              </>
            )}
          </div>
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-hidden relative bg-zinc-950/50">
          <TabsContent value="desktop" className="h-full w-full m-0 p-0 outline-none data-[state=active]:flex flex-col">
            <PreviewComponent
              code={previewCode}
              device="desktop"
              doUpdate={doUpdate}
            />
          </TabsContent>
          
          <TabsContent value="mobile" className="h-full w-full m-0 p-0 outline-none data-[state=active]:flex flex-col items-center justify-center bg-zinc-900/50">
            <PreviewComponent
              code={previewCode}
              device="mobile"
              doUpdate={doUpdate}
            />
          </TabsContent>
          
          <TabsContent value="code" className="h-full w-full m-0 p-0 outline-none data-[state=active]:flex flex-col">
            <CodeTab 
              code={previewCode} 
              setCode={() => {}} 
              settings={settings} 
            />
          </TabsContent>
        </div>
      </Tabs>
    </div>
  );
}

export default PreviewPane;
