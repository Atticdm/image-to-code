import { useState, useEffect } from "react";
import { useDropzone } from "react-dropzone";
import { toast } from "react-hot-toast";
import { URLS } from "../urls";
import ScreenRecorder from "./recording/ScreenRecorder";
import { ScreenRecorderState } from "../types";
import { UploadIcon, VideoIcon } from "@radix-ui/react-icons";

// Helper function to convert file to data URL
function fileToDataURL(file: File) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = (error) => reject(error);
    reader.readAsDataURL(file);
  });
}

type FileWithPreview = {
  preview: string;
} & File;

interface Props {
  setReferenceImages: (
    referenceImages: string[],
    inputMode: "image" | "video"
  ) => void;
}

function ImageUpload({ setReferenceImages }: Props) {
  const [files, setFiles] = useState<FileWithPreview[]>([]);
  const [screenRecorderState, setScreenRecorderState] =
    useState<ScreenRecorderState>(ScreenRecorderState.INITIAL);

  const { getRootProps, getInputProps, isDragActive, isDragAccept, isDragReject } =
    useDropzone({
      maxFiles: 1,
      maxSize: 1024 * 1024 * 20, // 20 MB
      accept: {
        "image/png": [".png"],
        "image/jpeg": [".jpeg"],
        "image/jpg": [".jpg"],
        "video/quicktime": [".mov"],
        "video/mp4": [".mp4"],
        "video/webm": [".webm"],
      },
      onDrop: (acceptedFiles) => {
        setFiles(
          acceptedFiles.map((file: File) =>
            Object.assign(file, {
              preview: URL.createObjectURL(file),
            })
          ) as FileWithPreview[]
        );

        Promise.all(acceptedFiles.map((file) => fileToDataURL(file)))
          .then((dataUrls) => {
            if (dataUrls.length > 0) {
              setReferenceImages(
                dataUrls.map((dataUrl) => dataUrl as string),
                (dataUrls[0] as string).startsWith("data:video")
                  ? "video"
                  : "image"
              );
            }
          })
          .catch((error) => {
            toast.error("Error reading files" + error);
            console.error("Error reading files:", error);
          });
      },
      onDropRejected: (rejectedFiles) => {
        toast.error(rejectedFiles[0].errors[0].message);
      },
    });

  useEffect(() => {
    return () => files.forEach((file) => URL.revokeObjectURL(file.preview));
  }, [files]);

  return (
    <div className="w-full">
      {screenRecorderState === ScreenRecorderState.INITIAL && (
        <div
          {...getRootProps()}
          className={`
            group relative flex flex-col items-center justify-center w-full min-h-[300px] 
            border-2 border-dashed rounded-xl transition-all duration-300 ease-in-out cursor-pointer
            ${isDragActive ? "scale-[0.99]" : "hover:bg-zinc-800/50"}
            ${
              isDragAccept
                ? "border-green-500 bg-green-500/10"
                : isDragReject
                ? "border-red-500 bg-red-500/10"
                : "border-zinc-700 hover:border-zinc-500 bg-zinc-900/30"
            }
          `}
        >
          <input {...getInputProps()} className="hidden" />
          
          <div className="flex flex-col items-center gap-4 p-8 text-center transition-transform duration-300 group-hover:-translate-y-1">
            <div className={`
              p-4 rounded-full bg-zinc-800 ring-1 ring-zinc-700 shadow-xl
              group-hover:ring-zinc-600 group-hover:bg-zinc-700 transition-all duration-300
            `}>
              <UploadIcon className="w-8 h-8 text-zinc-400 group-hover:text-white" />
            </div>
            
            <div className="space-y-2">
              <h3 className="text-xl font-medium text-white">
                Upload a screenshot or design
              </h3>
              <p className="text-sm text-zinc-400 max-w-xs mx-auto">
                Drag & drop or click to browse. Supports PNG, JPG, MP4, MOV.
              </p>
            </div>
          </div>

          {/* Video Recording Option Link */}
          <div className="absolute bottom-4 left-0 right-0 flex justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
             <div className="flex items-center gap-2 text-xs text-zinc-500 bg-zinc-950/80 px-3 py-1.5 rounded-full border border-zinc-800">
                <VideoIcon className="w-3 h-3" />
                <span>Supports Video Recording</span>
             </div>
          </div>
        </div>
      )}

      {screenRecorderState === ScreenRecorderState.INITIAL && (
        <div className="flex justify-center mt-4">
           <button 
             onClick={(e) => {
               e.stopPropagation();
               // Link to learn more logic could go here, or trigger recording directly
             }}
             className="text-xs text-zinc-500 hover:text-zinc-300 transition-colors flex items-center gap-1"
           >
             <a href={URLS["intro-to-video"]} target="_blank" rel="noreferrer" className="flex items-center gap-1">
               <span>Need to clone a full app flow? Try screen recording</span>
               <span className="bg-blue-600/10 text-blue-500 px-1.5 py-0.5 rounded text-[10px] font-bold">BETA</span>
             </a>
           </button>
        </div>
      )}

      <ScreenRecorder
        screenRecorderState={screenRecorderState}
        setScreenRecorderState={setScreenRecorderState}
        generateCode={setReferenceImages}
      />
    </div>
  );
}

export default ImageUpload;
