"use client";

import { useState } from "react";

export default function Home() {
  const [imageUrl, setImageUrl] = useState("")
  const [error, setError] = useState("");
  const [push, setPush] = useState(false)

  // 検索ボタンハ押下時処理
  const handleSearch = async () => {
    if (!imageUrl.trim()) {
      setError("画像URLを入力してください")
      return;
    }

    setError("");
    setPush(true)
  }
  try {
    const formData = new FormData();
    formData.append("image_url", imageUrl);
  }
  finally {
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
      {imageUrl && push && (
        <p>入力値：<b>{imageUrl}</b></p>
      )}
    </main>
  )
}