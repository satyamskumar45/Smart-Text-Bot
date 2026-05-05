import { createWorker } from "tesseract.js";

let workers = {};

export const getWorker = async (lang = "eng", setProgress) => {
  if (!workers[lang]) {
    const worker = await createWorker({
      logger: (m) => {
        if (m.status === "recognizing text" && setProgress) {
          setProgress(Math.round(m.progress * 100));
        }
      },
    });

    await worker.loadLanguage(lang);
    await worker.initialize(lang);

    workers[lang] = worker;
  }

  return workers[lang];
};

export const extractTextFromImage = async (file, setProgress, lang = "eng") => {
  if (!file) return "";

  const worker = await getWorker(lang, setProgress);

  const { data } = await worker.recognize(file);

  return data.text;
};

export const terminateAllWorkers = async () => {
  for (const key in workers) {
    try {
      await workers[key].terminate();
    } catch (e) {}
  }
  workers = {};
};