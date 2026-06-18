// Reusable Approval Card for the Kanban board
interface Props {
  postId:    string;
  platform:  string;
  status:    string;
  content?:  string;
  imageUrl?: string;
}

const STATUS_COLOR: Record<string, string> = {
  draft:              "bg-gray-100 text-gray-600",
  image_review:       "bg-yellow-100 text-yellow-700",
  image_regenerating: "bg-orange-100 text-orange-700",
  approved:           "bg-blue-100 text-blue-700",
  publishing:         "bg-purple-100 text-purple-700",
  published:          "bg-green-100 text-green-700",
};

export default function ApprovalCard({ postId, platform, status, content, imageUrl }: Props) {
  const badge = STATUS_COLOR[status] || "bg-gray-100 text-gray-600";
  return (
    <div className="border rounded-xl p-4 bg-white">
      <div className="flex items-center justify-between mb-3">
        <span className="font-medium capitalize text-sm">{platform}</span>
        <span className={`text-xs px-2 py-1 rounded-full font-medium ${badge}`}>
          {status.replace(/_/g, " ")}
        </span>
      </div>
      {imageUrl && <img src={imageUrl} alt="" className="w-full rounded-lg mb-3 object-cover h-32" />}
      {content && <p className="text-xs text-gray-500 line-clamp-3">{content}</p>}
      <p className="text-xs text-gray-300 mt-2 font-mono">{postId.slice(0, 8)}…</p>
    </div>
  );
}
