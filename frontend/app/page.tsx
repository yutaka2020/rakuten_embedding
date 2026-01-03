"use client";

import { useState } from "react";
import { InputField } from "./components/InputField";


type Mode = "url" | "file";


export default function Home() {
  const [imageUrl, setImageUrl] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [minPrice, setMinPrice] = useState<string>("");
  const [maxPrice, setMaxPrice] = useState<string>("");

  const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

  // 入力モード（URL or ファイル）
  const [mode, setMode] = useState<Mode>("url");

  // 入力モード切り替え
  const onSwitch = (m: Mode) => {
    setMode(m);
    setError("")
    setResults([])

    // モード切り替え時ファイルをクリア、URLをクリア
    if (m === "url") setFile(null);
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
        const errorData = await res.json();
        throw new Error(errorData.error || "サーバーからのエラーが発生しました");
      }

      const data = await res.json();
      console.log("サーバーからのレスポンス", data);

      // エラーがあった場合はエラーメッセージをセット
      if (data.error) {
        setError(data.err)
      } else {
        setResults(data.results)
      }

    } catch (err) {
      console.error("通信エラー", err);
      setError("サーバーとの通信に失敗しました")
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
          setFile={setFile} />

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
          disabled={loading}
          className={`px-4 py-2 rounded-lg font-semibold text-white ${loading ? "bg-blue-300 cursor-not-allowed"
            : "bg-blue-500 hover:bg-blue-600"}`}>{loading ? "検索中..." : "検索"}</button>
      </div>
      {error && (
        <p className="text-center text-red-500 font-medium mb-4">{error}</p>
      )}

      {results.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {file && (
            <div className="bg-white p-4 rounded-xl shadow-md border border-gray-100">
              <img
                src={URL.createObjectURL(file)}
                alt="preview"
                className="w-full h-48 object-cover rounded-lg"
              />
              <h2 className="font-semibold text-lg mt-2 text-gray-800">検索対象画像</h2>
            </div>
          )}

          {results.map((item, i) => (
            <div key={i} className="bg-white p-4 rounded-xl shadow-md boeder border-gray-100">
              <img src={item.image_url} alt={item.name} className="w-full h-48 object-cover rounded-lg" />
              <h2 className="font-semibold text-lg mt-2 text-gray-800 line-clamp-2">{item.name}</h2>
              <p className="text-gray-600">値段 : {item.price}</p>
              <p className="text-gray-500">ブランド : {item.shop}</p>
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