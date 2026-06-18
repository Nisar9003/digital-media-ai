// Reusable Content Editor Component
interface Props {
  content: string;
  onChange: (val: string) => void;
}

export default function ContentEditor({ content, onChange }: Props) {
  return (
    <div className="border rounded-xl p-4">
      <label className="block text-xs font-medium text-gray-400 mb-2 uppercase tracking-wide">
        Caption
      </label>
      <textarea
        className="w-full text-sm resize-none outline-none min-h-32"
        value={content}
        onChange={e => onChange(e.target.value)}
        placeholder="Generated content will appear here..."
      />
    </div>
  );
}
