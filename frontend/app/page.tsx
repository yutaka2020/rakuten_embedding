"use client";

import { useState } from "react";
import { InputField } from "./components/InputField";


type Mode = "url" | "file";

type SearchResult = {
  score: number;
  name: string;
  price: number | null;
  image_url: string;
  product_url: string;
  shop: string | null;
};

// 対応可能なファイル形式（バックエンドと一致させる）
const ALLOWED_EXT = [".jpg", ".jpeg", ".png", ".webp"];
const ALLOWED_MIME = ["image/jpeg", "image/png", "image/webp"];

// ファイル検証関数
function validateFile(file: File): string | null {
  const name = (file.name || "").toLowerCase();
  const ext = "." + name.split(".").pop() || "";

  // 拡張子チェック
  if (!ALLOWED_EXT.includes(ext)) {
    return `対応外の拡張子です（${ALLOWED_EXT.join(", ")} のみ対応）`;
  }

  // MIMEタイプチェック
  const mime = (file.type || "").toLowerCase();
  if (mime && !ALLOWED_MIME.includes(mime)) {
    return `対応外のファイル形式です（${ALLOWED_MIME.join(", ")} のみ対応）`;
  }

  return null;
}


export default function Home() {
  const [imageUrl, setImageUrl] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [fileError, setFileError] = useState<string | null>(null);
  const [minPrice, setMinPrice] = useState<string>("");
  const [maxPrice, setMaxPrice] = useState<string>("");

  const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

  // 入力モード（URL or ファイル）
  const [mode, setMode] = useState<Mode>("url");

  // ファイル選択時の処理（検証を含む）
  const handleFileChange = (selectedFile: File | null) => {
    setFile(selectedFile);
    if (selectedFile) {
      const validationError = validateFile(selectedFile);
      setFileError(validationError);
      if (validationError) {
        setError(validationError);
      } else {
        setError(""); // ファイルが有効な場合はエラーをクリア
      }
    } else {
      setFileError(null);
      setError("");
    }
  };

  // 入力モード切り替え
  const onSwitch = (m: Mode) => {
    setMode(m);
    setError("")
    setFileError(null);
    setResults([])

    // モード切り替え時ファイルをクリア、URLをクリア
    if (m === "url") {
      setFile(null);
      setFileError(null);
    }
    if (m === "file") setImageUrl("");
  }

  // 検索ボタンが押下された時の処理
  const handleSearch = async () => {
    setError("");
    setResults([]);

    // 入力モードがURLの場合はURLが入力されているかチェック
    if (mode === "url" && !imageUrl.trim()) {
      setError("画像URLを入力してください")
      return;
    }
    // 入力モードがファイルの場合はファイルが選択されているかチェック
    if (mode === "file" && !file) {
      setError("画像ファイルを選択してください")
      return;
    }

    // ファイルが選択されているが検証エラーがある場合は処理を停止
    if (mode === "file" && file && fileError) {
      return;
    }

    setLoading(true);

    try {
      // フォームデータを作成
      const formData = new FormData();
      if (mode === "url") {
        formData.append("image_url", imageUrl);
      } else if (file) {
        formData.append("file", file);
      }

      // 最低価格と最高価格をフォームデータに追加
      if (minPrice) formData.append("min_price", minPrice);
      if (maxPrice) formData.append("max_price", maxPrice);

      // サーバーにリクエストを送信
      const res = await fetch(`${API_BASE}/api/search`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const contentType = res.headers.get("content-type") ?? "";
        if (contentType.includes("application/json")) {
          const errorData = await res.json();
          throw new Error(errorData.error || "サーバーからのエラーが発生しました");
        }
        const errorText = await res.text();
        throw new Error(errorText || "サーバーからのエラーが発生しました");
      }

      const data = await res.json();
      console.log("サーバーからのレスポンス", data);

      // エラーがあった場合はエラーメッセージをセット
      if (data.error) {
        setError(data.error)
      } else {
        setResults(data.results)
      }

    } catch (err) {
      if (err instanceof Error) setError(err.message);
      else setError("サーバーとの通信に失敗しました");
      console.error(err)
    } finally {
      setLoading(false);
    }

  }

  // ==============================
  // UIを描画するコンポーネント
  // ==============================
  return (
    <main className="min-h-screen bg-gray-50 p-80">
      <h1 className="text-3xl font-bold text-center mb-6 text-gray-800">Image Search</h1>

      <div className="mx-auto w-full max-w-2xl mb-6">
        <div className="inline-flex rounded-xl overflow-hidden border border-gray-200 shadow-sm">
          <button
            className={`px-4 py-2 text-sm font-semibold ${mode === "url"
              ? "bg-white text-blue-600"
              : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              }`}
            onClick={() => onSwitch("url")}
          >URL入力</button>
          <button
            className={`px-4 py-2 text-sm font-semibold ${mode === "file"
              ? "bg-white text-blue-600"
              : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              }`}
            onClick={() => onSwitch("file")}
          >
            画像アップロード
          </button>
        </div>
      </div>

      <div className="flex items-start justify-center mb-6 gap-2">
        <InputField
          mode={mode}
          imageUrl={imageUrl}
          setImageUrl={setImageUrl}
          file={file}
          setFile={handleFileChange} />

        <div className="flex flex-col items-center gap-3 mb-6">

          <input
            type="number"
            placeholder="最低価格（例：5000）"
            value={minPrice}
            onChange={(e) => setMinPrice(e.target.value)}
            className="w-80 p-2 border border-gray-300 rounded-lg text-black"
          />

          <input
            type="number"
            placeholder="最高価格（例：15000）"
            value={maxPrice}
            onChange={(e) => setMaxPrice(e.target.value)}
            className="w-80 p-2 border border-gray-300 rounded-lg text-black"
          />
        </div>
        <button
          onClick={handleSearch}
          disabled={loading || (mode === "file" && fileError !== null)}
          className={`px-4 py-2 rounded-lg font-semibold text-white ${loading || (mode === "file" && fileError !== null) ? "bg-blue-300 cursor-not-allowed"
            : "bg-blue-500 hover:bg-blue-600"}`}>{loading ? "検索中..." : "検索"}</button>
      </div>
      {error && (
        <p className="text-center text-red-500 font-medium mb-4">{error}</p>
      )}

      {results.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {results.map((item, i) => (
            <div
              key={item.product_url ?? item.image_url ?? i}
              className="bg-white p-4 rounded-xl shadow-md border border-gray-100"
            >
              <img src={item.image_url} alt={item.name} className="w-full h-48 object-cover rounded-lg" />
              <h2 className="font-semibold text-lg mt-2 text-gray-800 line-clamp-2">{item.name}</h2>
              <p className="text-gray-600">値段 : {item.price ?? "価格未設定"}</p>
              <p className="text-gray-500">ブランド : {item.shop ?? "未設定"}</p>
              <a href={item.product_url} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline text-sm">
                商品ページへ
              </a>
            </div>
          ))}
        </div>
      ) : (
        !loading &&
        !error && (
          <p className="text-center text-gray-500 mt-10">検索結果がまだありません</p>
        )
      )}
    </main>
  )
}
