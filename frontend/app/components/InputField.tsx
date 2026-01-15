"use client";

import { useEffect, useState } from "react";

const ALLOWED_EXT = ["jpg", "jpeg", "png", "webp"];


type Props = {
    mode: "url" | "file";
    imageUrl: string;
    setImageUrl: (v: string) => void;
    file: File | null;
    setFile: (f: File | null) => void;
};

export function InputField({ mode, imageUrl, setImageUrl, file, setFile }: Props) {
    const [previewUrl, setPreviewUrl] = useState<string>("");

    useEffect(() => {
        if (!file) {
            setPreviewUrl("");
            return;
        }
        const url = URL.createObjectURL(file);
        setPreviewUrl(url);
        return () => URL.revokeObjectURL(url);
    }, [file]);

    switch (mode) {
        case "url":
            return (
                <input
                    type="text"
                    placeholder="画像URLを入力してください"
                    value={imageUrl}
                    onChange={(e) => setImageUrl(e.target.value)}
                    className="w-80 p-2 border border-gray-300 rounded-lg text-black focus:outline-none focus:ring-2 focus:ring-blue-400"
                />
            );

        case "file":
            return (
                <div className="flex flex-col items-center gap-3">
                    <input
                        id="fileUpload"
                        type="file"
                        accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp"
                        onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                        className="hidden"
                    />

                    <label
                        htmlFor="fileUpload"
                        className="cursor-pointer bg-blue-100 text-blue-700 px-4 py-2 rounded-md hover:bg-blue-200 font-semibold"
                    >
                        画像を選択
                    </label>

                    {file ? (
                        <>
                            <p className="text-gray-700 text-sm">
                                選択されたファイル: <span className="font-semibold">{file.name}</span>
                            </p>
                            {previewUrl && (
                                <div className="w-80 bg-white p-2 rounded-xl shadow-md border border-gray-100">
                                    <img
                                        src={previewUrl}
                                        alt="preview"
                                        className="w-full h-48 object-cover rounded-lg"
                                    />
                                </div>
                            )}
                            <button
                                type="button"
                                onClick={() => setFile(null)}
                                className="text-xs text-gray-600 hover:underline"
                            >
                                選択をクリア
                            </button>
                        </>
                    ) : (
                        <p className="text-gray-400 text-sm">ファイルが選択されていません</p>
                    )}
                </div>
            );

        default:
            return null;
    }
}
