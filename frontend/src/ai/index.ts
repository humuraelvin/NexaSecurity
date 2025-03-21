import { google } from "@ai-sdk/google";
import { wrapLanguageModel } from "ai";

import { customMiddleware } from "./custom-middleware";

export const geminiProModel = wrapLanguageModel({
  model: google("gemini-2.0-flash-001"),
  middleware: customMiddleware,
});

export const geminiFlashModel = wrapLanguageModel({
  model: google("gemini-1.5-pro"),
  middleware: customMiddleware,
});