"use client";

import { useState } from "react";

export default function Home() {
  const [imageUrl, setImageUrl] = useState("")
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false)

  // 検索ボタンハ押下時処理
  const handleSearch = async () => {
    if (!imageUrl.trim()) {
      setError("画像URLを入力してください")
      return;
    }

    setError("");
    setLoading(true)
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
    } finally {
      setLoading(false);
    }

  }
  return (
    <main>
      <h1>AI Search</h1>
      <div>
        <input
          type="text"
          placeholder="画像URLを入力してください"
          value={imageUrl}
          onChange={(e) => setImageUrl(e.target.value)} />
        <button onClick={handleSearch}>検索</button>
      </div>
      {error && (
        <p>{error}</p>
      )}
      {imageUrl && (
        <p>入力値：<b>{imageUrl}</b></p>
      )}
    </main>
  )
}