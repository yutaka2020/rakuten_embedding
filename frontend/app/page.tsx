"use client";

import { Mode } from "fs";
import { url } from "inspector";
import { useState } from "react";

export default function Home() {
  const [imageUrl, setImageUrl] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [mode, setMode] = useState<Mode>("url");


  const onSwitch = (m: Mode) => {
    setMode(m);
    setError("")
    setResults([])

    if (m === "url") setFile(null);
    if (m === "file") setImageUrl("");
  }

  // 検索ボタンハ押下時処理
  const handleSearch = async () => {
    setError("");
    setResults([]);

    if (mode === "url" && !imageUrl.trim()) {
      setError("画像URLを入力してください")
      return;
    }
    if (mode === "file" && !file) {
      setError("画像ファイルを選択してください")
      return;
    }
    setLoading(true);
    try {
      const formData = new FormData();
      if (mode === "url") {
        formData.append("image_url", imageUrl);
      } else if (file) {
        formData.append("file", file);
      }

      const res = await fetch("http://127.0.0.1:8000/api/search", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      console.log("サーバーからのレスポンス", data);
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
  function InputField({ mode, imageUrl, setImageUrl, setFile }: any) {
    switch (mode) {
      case "url":
        return (<input
          type="text"
          placeholder="画像URLを入力してください"
          value={imageUrl}
          onChange={(e) => setImageUrl(e.target.value)}
          className="w-80 p-2 border border-gray-300 rounded-lg text-black focus:outline-none focus:ring-2 focus:ring-blue-400"
        />);

      case "file":
        return (
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="block text-sm text-gray-700
            file:mr-4 file:py-2 file:px-4
            file:rounded-md file:border-0
            file:text-sm file:font-semibold
            file:bg-blue-100 file:text-blue-700
            hover:file:bg-blue-200"
          />
        )
    }
  }

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
          >
            URL入力
          </button>
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

      <div className="flex justify-center mb-6 gap-2">
        <InputField
          mode={mode}
          imageUrl={imageUrl}
          setImageUrl={setImageUrl}
          setFile={setFile} />
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