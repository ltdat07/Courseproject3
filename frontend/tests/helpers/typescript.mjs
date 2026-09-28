import { readFileSync } from "node:fs";
import { registerHooks } from "node:module";
import ts from "typescript";

registerHooks({
  resolve(specifier, context, nextResolve) {
    try {
      return nextResolve(specifier, context);
    } catch (error) {
      if (error.code !== "ERR_MODULE_NOT_FOUND" || !specifier.startsWith(".")) throw error;
      for (const extension of [".ts", ".tsx"]) {
        try {
          return nextResolve(specifier + extension, context);
        } catch (candidateError) {
          if (candidateError.code !== "ERR_MODULE_NOT_FOUND") throw candidateError;
        }
      }
      throw error;
    }
  },
  load(url, context, nextLoad) {
    if (!url.startsWith("file:") || !url.endsWith(".tsx")) return nextLoad(url, context);
    const source = ts.transpileModule(readFileSync(new URL(url), "utf8"), {
      compilerOptions: { jsx: ts.JsxEmit.ReactJSX, module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2023 },
    }).outputText;
    return { format: "module", source, shortCircuit: true };
  },
});
