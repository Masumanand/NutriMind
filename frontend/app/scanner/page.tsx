"use client";
import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { motion, AnimatePresence } from "framer-motion";
import { Scan, Upload, Mic, Barcode, Camera, Loader2, Plus } from "lucide-react";
import toast from "react-hot-toast";
import { scannerApi, foodApi, streakApi } from "@/lib/api";
import AppShell from "@/components/layout/AppShell";

type ScanMode = "image" | "voice" | "barcode";
interface ScanResult { food_name: string; confidence: number; calories_estimated: number; protein_g: number; carbs_g: number; fat_g: number; serving_size_g: number; health_score: number; sustainability_score: number; allergens: string[]; diet_tags: string[]; explanation: string; }

export default function ScannerPage() {
  const [mode, setMode] = useState<ScanMode>("image");
  const [scanning, setScanning] = useState(false);
  const [result, setResult] = useState<ScanResult | null>(null);
  const [voiceText, setVoiceText] = useState("");
  const [barcode, setBarcode] = useState("");
  const [preview, setPreview] = useState<string | null>(null);
  const [logging, setLogging] = useState(false);
  const [mealType, setMealType] = useState<string>("lunch");

  const onDrop = useCallback(async (files: File[]) => {
    const file = files[0];
    if (!file) return;
    setPreview(URL.createObjectURL(file));
    setScanning(true); setResult(null);
    try { const fd = new FormData(); fd.append("file", file); const { data } = await scannerApi.scanImage(fd); setResult(data); }
    catch { toast.error("Could not analyze image."); }
    finally { setScanning(false); }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop, accept: { "image/*": [".jpg", ".jpeg", ".png", ".webp"] }, maxFiles: 1 });

  const handleVoiceParse = async () => {
    if (!voiceText.trim()) return; setScanning(true);
    try { const { data } = await scannerApi.parseVoice(voiceText); toast.success(`Found ${data.item_count} food item(s)!`);
      for (const item of data.parsed_items) { await foodApi.logFood({ food_name: item.food_name, quantity_g: item.quantity_g, meal_type: item.meal_type || "snack", logged_via: "voice" }); }
      if (data.item_count > 0) toast.success("All items logged! ✅");
    } catch { toast.error("Could not parse voice input"); } finally { setScanning(false); }
  };

  const handleBarcodeScan = async () => {
    if (!barcode.trim()) return; setScanning(true);
    try { const { data } = await scannerApi.scanBarcode(barcode); setResult({ ...data, calories_estimated: data.calories_per_100g, protein_g: data.protein_per_100g, carbs_g: data.carbs_per_100g, fat_g: data.fat_per_100g, serving_size_g: 100, confidence: 1, allergens: [], diet_tags: [], explanation: data.recommendation }); }
    catch { toast.error("Product not found"); } finally { setScanning(false); }
  };

  const logScannedFood = async () => {
    if (!result) return; setLogging(true);
    try {
      await foodApi.logFood({ food_name: result.food_name, quantity_g: result.serving_size_g, meal_type: mealType, logged_via: "scanner" });
      // Trigger streak tracking for photo-logged meals
      if (["breakfast", "lunch", "dinner"].includes(mealType)) {
        try { await streakApi.logMealPhoto(mealType); } catch {}
      }
      toast.success(`${result.food_name} logged! 🎉 Streak updated!`);
      setResult(null); setPreview(null);
    }
    catch { toast.error("Failed to log food"); } finally { setLogging(false); }
  };

  return (
    <AppShell>
      <div className="space-y-6 animate-fade-in max-w-2xl mx-auto">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2"><Scan className="w-6 h-6 text-brand-500" /> Food Scanner</h1>
          <p className="text-gray-500 text-sm mt-1">Snap, speak, or scan to log food instantly</p>
        </div>

        <div className="flex gap-1 p-1 bg-gray-100 rounded-xl">
          {([{ key: "image", icon: Camera, label: "Photo" }, { key: "voice", icon: Mic, label: "Voice" }, { key: "barcode", icon: Barcode, label: "Barcode" }] as const).map(({ key, icon: Icon, label }) => (
            <button key={key} onClick={() => { setMode(key); setResult(null); setPreview(null); }} className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-medium transition-all ${mode === key ? "bg-white text-brand-600 shadow-sm" : "text-gray-500 hover:text-gray-700"}`}>
              <Icon className="w-4 h-4" /> {label}
            </button>
          ))}
        </div>

        {mode === "image" && (
          <div>
            <div {...getRootProps()} className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all ${isDragActive ? "border-brand-400 bg-brand-50" : "border-gray-200 hover:border-brand-300 hover:bg-gray-50"}`}>
              <input {...getInputProps()} />
              {preview ? <img src={preview} alt="Food preview" className="max-h-48 mx-auto rounded-xl object-cover" /> : (<><Upload className="w-10 h-10 text-gray-300 mx-auto mb-3" /><p className="text-gray-500">Drop a food photo here or click to upload</p><p className="text-xs text-gray-400 mt-1">JPG, PNG, WebP · Max 10MB</p></>)}
            </div>
            {scanning && <div className="flex items-center justify-center gap-2 mt-4 text-brand-600"><Loader2 className="w-5 h-5 animate-spin" /><span className="text-sm">Analyzing with AI...</span></div>}
          </div>
        )}

        {mode === "voice" && (
          <div className="glass-card p-6 space-y-4">
            <p className="text-sm text-gray-500">Type what you ate (voice transcription)</p>
            <textarea value={voiceText} onChange={(e) => setVoiceText(e.target.value)} placeholder='e.g. "I ate 2 rotis, a bowl of dal, and a glass of milk"' className="w-full bg-gray-50 border border-gray-200 rounded-xl p-4 text-gray-800 placeholder-gray-400 focus:outline-none focus:border-brand-300 resize-none h-28 text-sm" />
            <button onClick={handleVoiceParse} disabled={!voiceText.trim() || scanning} className="w-full py-3 bg-brand-500 hover:bg-brand-600 disabled:opacity-50 text-white font-semibold rounded-xl flex items-center justify-center gap-2 transition-all">
              {scanning ? <Loader2 className="w-4 h-4 animate-spin" /> : <Mic className="w-4 h-4" />} Parse & Log Food
            </button>
          </div>
        )}

        {mode === "barcode" && (
          <div className="glass-card p-6 space-y-4">
            <p className="text-sm text-gray-500">Enter product barcode number</p>
            <input value={barcode} onChange={(e) => setBarcode(e.target.value)} placeholder="e.g. 3017620422003" className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-gray-800 placeholder-gray-400 focus:outline-none focus:border-brand-300" />
            <button onClick={handleBarcodeScan} disabled={!barcode.trim() || scanning} className="w-full py-3 bg-brand-500 hover:bg-brand-600 disabled:opacity-50 text-white font-semibold rounded-xl flex items-center justify-center gap-2 transition-all">
              {scanning ? <Loader2 className="w-4 h-4 animate-spin" /> : <Barcode className="w-4 h-4" />} Look Up Product
            </button>
          </div>
        )}

        <AnimatePresence>
          {result && (
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} className="glass-card p-6 space-y-4">
              <div className="flex items-start justify-between">
                <div><h3 className="text-xl font-bold text-gray-800">{result.food_name}</h3><p className="text-xs text-gray-400 mt-0.5">Confidence: {Math.round(result.confidence * 100)}% · {result.serving_size_g}g serving</p></div>
                <div className="text-right"><p className={`text-2xl font-bold ${result.health_score >= 7 ? "text-green-600" : result.health_score >= 4 ? "text-yellow-500" : "text-red-500"}`}>{result.health_score}/10</p><p className="text-xs text-gray-400">Health Score</p></div>
              </div>
              <div className="grid grid-cols-4 gap-3">
                {[{ label: "Calories", value: Math.round(result.calories_estimated), unit: "kcal", color: "text-orange-500" }, { label: "Protein", value: Math.round(result.protein_g), unit: "g", color: "text-blue-500" }, { label: "Carbs", value: Math.round(result.carbs_g), unit: "g", color: "text-yellow-500" }, { label: "Fat", value: Math.round(result.fat_g), unit: "g", color: "text-purple-500" }].map((m) => (
                  <div key={m.label} className="bg-gray-50 rounded-xl p-3 text-center"><p className={`text-lg font-bold ${m.color}`}>{m.value}</p><p className="text-xs text-gray-400">{m.unit}</p><p className="text-xs text-gray-500">{m.label}</p></div>
                ))}
              </div>
              {result.explanation && <div className="bg-blue-50 border border-blue-100 rounded-xl p-3"><p className="text-xs text-blue-700">🧠 {result.explanation}</p></div>}
              {result.diet_tags?.length > 0 && <div className="flex flex-wrap gap-2">{result.diet_tags.map((tag) => <span key={tag} className="px-2 py-1 bg-brand-50 border border-brand-200 rounded-full text-xs text-brand-700">{tag}</span>)}</div>}
              {/* Meal Type Selector */}
              <div>
                <p className="text-xs text-gray-500 mb-2">Select meal type (counts towards your streak!):</p>
                <div className="flex gap-2">
                  {["breakfast", "lunch", "dinner", "snack"].map((type) => (
                    <button key={type} onClick={() => setMealType(type)} className={`px-3 py-1.5 rounded-lg text-xs font-medium capitalize transition-all ${mealType === type ? "bg-brand-500 text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"}`}>
                      {type}
                    </button>
                  ))}
                </div>
              </div>
              <button onClick={logScannedFood} disabled={logging} className="w-full py-3 bg-brand-500 hover:bg-brand-600 disabled:opacity-50 text-white font-semibold rounded-xl flex items-center justify-center gap-2 transition-all">
                {logging ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />} Log This Food
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </AppShell>
  );
}
