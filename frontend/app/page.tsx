"use client";

import { useState } from "react";

export default function Home() {
  const [imageUrl, setImageUrl] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any[]>([]);

  // 検索ボタンハ押下時処理
  const handleSearch = async () => {
    if (!imageUrl.trim()) {
      setError("画像URLを入力してください")
      return;
    }

    setError("");
    setLoading(true);
    setResults([]);
    try {
      const formData = new FormData();
      formData.append("image_url", imageUrl);

      const res = await fetch("http://127.0.0.1:8000/api/search", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      console.log("サーバーからのレスポンス", data);
    } catch (err) {
      console.error("通信エラー", err);
      setError("サーバーとの通信に失敗しました")
      console.error(err)
    } finally {
      setLoading(false);
    }

  }
  return (
    <main className="min-h-screen bg-gray-50 p-80">
      <h1 className="text-3xl font-bold text-center mb-6 text-gray-800">Image Search</h1>
      <div className="flex justify-center mb-6 gap-2">
        <input
          type="text"
          placeholder="画像URLを入力してください"
          value={imageUrl}
          onChange={(e) => setImageUrl(e.target.value)}
          className="w-80 p-2 border border-gray-300 rounded-lg text-black
          foucus:outline-none foucus:ring-2 foucus:ring-bulue-400" />
        <button
          onClick={handleSearch}
          disabled={loading}
          className={`px-4 py-2 rounded-lg font-semibold text-white ${loading ? "bg-blue-300 cursor-not-allowed"
            : "bg-blue-500 hover:bg-blue-600"}`}>{loading ? "検索中..." : "検索"}</button>
      </div>
      {error && (
        <p className="text-center text-red-500 font-medium mb-4">{error}</p>
      )}
      {imageUrl && (
        <p>入力値：<b>{imageUrl}</b></p>
      )}
    </main>
  )
}