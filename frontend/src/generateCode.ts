import toast from "react-hot-toast";
import { WS_BACKEND_URL } from "./config";
import {
  APP_ERROR_WEB_SOCKET_CODE,
  USER_CLOSE_WEB_SOCKET_CODE,
} from "./constants";
import { FullGenerationSettings } from "./types";

const ERROR_MESSAGE =
  "Error generating code. Check the Developer Console AND the backend logs for details. Feel free to open a Github issue.";

const CANCEL_MESSAGE = "Code generation cancelled";

type WebSocketResponse = {
  type:
    | "chunk"
    | "status"
    | "setCode"
    | "error"
    | "variantComplete"
    | "variantError"
    | "variantCount";
  value: string;
  variantIndex?: number;
};

interface CodeGenerationCallbacks {
  onChange: (chunk: string, variantIndex: number) => void;
  onSetCode: (code: string, variantIndex: number) => void;
  onStatusUpdate: (status: string, variantIndex: number) => void;
  onVariantComplete: (variantIndex: number) => void;
  onVariantError: (variantIndex: number, error: string) => void;
  onVariantCount: (count: number) => void;
  onCancel: () => void;
  onComplete: () => void;
}

export function generateCode(
  wsRef: React.MutableRefObject<WebSocket | null>,
  params: FullGenerationSettings,
  callbacks: CodeGenerationCallbacks
) {
  const wsUrl = `${WS_BACKEND_URL}/generate-code`;
  console.log("Connecting to backend @ ", wsUrl);

  const ws = new WebSocket(wsUrl);
  wsRef.current = ws;

  ws.addEventListener("open", () => {
    ws.send(JSON.stringify(params));
  });

  ws.addEventListener("message", async (event: MessageEvent) => {
    let response: WebSocketResponse;
    try {
      response = JSON.parse(event.data) as WebSocketResponse;
    } catch (e) {
      console.error("Failed to parse WS message", e);
      return;
    }

    const handlers: Record<
      WebSocketResponse["type"],
      (r: WebSocketResponse) => void
    > = {
      chunk: (r) => {
        if (typeof r.variantIndex !== "number") return;
        callbacks.onChange(r.value, r.variantIndex);
      },
      status: (r) => {
        if (typeof r.variantIndex !== "number") return;
        callbacks.onStatusUpdate(r.value, r.variantIndex);
      },
      setCode: (r) => {
        if (typeof r.variantIndex !== "number") return;
        callbacks.onSetCode(r.value, r.variantIndex);
      },
      variantComplete: (r) => {
        if (typeof r.variantIndex !== "number") return;
        callbacks.onVariantComplete(r.variantIndex);
      },
      variantError: (r) => {
        if (typeof r.variantIndex !== "number") return;
        callbacks.onVariantError(r.variantIndex, r.value);
      },
      variantCount: (r) => {
        callbacks.onVariantCount(parseInt(r.value));
      },
      error: (r) => {
        console.error("Error generating code", r.value);
        toast.error(r.value);
      },
    };

    handlers[response.type]?.(response);
  });

  ws.addEventListener("close", (event) => {
    console.log("Connection closed", event.code, event.reason);
    if (event.code === USER_CLOSE_WEB_SOCKET_CODE) {
      toast.success(CANCEL_MESSAGE);
      callbacks.onCancel();
    } else if (event.code === APP_ERROR_WEB_SOCKET_CODE) {
      console.error("Known server error", event);
      callbacks.onCancel();
    } else if (event.code !== 1000) {
      console.error("Unknown server or connection error", event);
      toast.error(ERROR_MESSAGE);
      callbacks.onCancel();
    } else {
      callbacks.onComplete();
    }
  });

  ws.addEventListener("error", (error) => {
    console.error("WebSocket error", error);
    toast.error(ERROR_MESSAGE);
  });
}
