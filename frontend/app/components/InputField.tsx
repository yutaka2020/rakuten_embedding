"use client";

type Props = {
    mode: "url" | "file";
    imageUrl: string;
    setImageUrl: (v: string) => void;
    file: File | null;
    setFile: (f: File | null) => void;
};

export function InputField({ mode, imageUrl, setImageUrl, file, setFile }: Props) {
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
                <div className="flex flex-col items-center gap-2">
                    <input
                        id="fileUpload"
                        type="file"
                        accept="image/*"
                        onChange={(e) => setFile(e.target.files?.[0] || null)}
                        className="hidden"
                    />
                    <label
                        htmlFor="fileUpload"
                        className="cursor-pointer bg-blue-100 text-blue-700 px-4 py-2 rounded-md hover:bg-blue-200 font-semibold"
                    >
                        画像を選択
                    </label>
                    {file ? (
                        <p className="text-gray-700 text-sm">
                            選択されたファイル: <span className="font-semibold">{file.name}</span>
                        </p>
                    ) : (
                        <p className="text-gray-400 text-sm">ファイルが選択されていません</p>
                    )}
                </div>
            );

        default:
            return null;
    }
}
