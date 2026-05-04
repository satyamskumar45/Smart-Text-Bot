import { createWorker } from "tesseract.js";

// Optionally downscale large images to avoid huge OCR time / memory usage
async function downscaleImage(file, maxDim = 1600) {
  if (!file) return null;
  const imgBitmap = await createImageBitmap(file);
  const { width, height } = imgBitmap;
  const scale = Math.min(1, maxDim / Math.max(width, height));
  if (scale === 1) return file;

  const canvas = document.createElement("canvas");
  canvas.width = Math.round(width * scale);
  canvas.height = Math.round(height * scale);
  const ctx = canvas.getContext("2d");
  ctx.drawImage(imgBitmap, 0, 0, canvas.width, canvas.height);
  return new Promise((resolve) => canvas.toBlob((b) => resolve(new File([b], file.name, { type: file.type })), file.type));
}

/**
 * extractTextFromImage(file, onProgress?)
 * - Uses Tesseract.js to run OCR in the browser.
 * - Returns the extracted text as a string.
 * - Optional onProgress callback receives a number [0-100].
 */
/**
 * extractTextFromImage(file, onProgress, lang = 'eng')
 * - file: File|Blob image
 * - onProgress: optional callback(percent)
 * - lang: tesseract language code (e.g. 'eng', 'spa')
 */
// Worker cache to avoid re-initializing heavy WebWorkers repeatedly.
const workerPool = new Map(); // lang -> { worker, callbacks: Set<fn> }

async function getWorkerEntry(lang = "eng") {
  let entry = workerPool.get(lang);
  if (entry) return entry;

  const callbacks = new Set();
  const worker = createWorker({
    logger: (m) => {
      if (m && m.status === "recognizing text" && typeof m.progress === "number") {
        const pct = Math.round(m.progress * 100);
        callbacks.forEach((cb) => {
          try {
            cb(pct);
          } catch (e) {
            // ignore
          }
        });
      }
    },
  });

  // initialize worker for the language
  await worker.load();
  await worker.loadLanguage(lang);
  await worker.initialize(lang);

  entry = { worker, callbacks };
  workerPool.set(lang, entry);
  return entry;
}

export async function terminateAllWorkers() {
  const entries = Array.from(workerPool.values());
  await Promise.all(entries.map(async (e) => {
    try { await e.worker.terminate(); } catch (err) {}
  }));
  workerPool.clear();
}

export async function extractTextFromImage(file, onProgress, lang = "eng") {
  if (!file) return "";

  // Downscale large images to improve performance and memory usage
  let inputFile = file;
  try {
    inputFile = await downscaleImage(file, 1600) || file;
  } catch (e) {
    // If downscaling fails, continue with original file
    // eslint-disable-next-line no-console
    console.warn("Image downscale failed, using original file", e);
  }

  // Use cached worker per language to improve performance
  const entry = await getWorkerEntry(lang);
  if (onProgress) entry.callbacks.add(onProgress);

  try {
    const { data } = await entry.worker.recognize(inputFile);
    return data?.text || "";
  } finally {
    if (onProgress) entry.callbacks.delete(onProgress);
    if (onProgress) onProgress(100);
  }
}

export default extractTextFromImage;
