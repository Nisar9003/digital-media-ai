// Reusable Image Review Component
interface Props {
  imageUrl: string;
  onApprove: (feedback: string) => void;
  onRegenerate: (feedback: string) => void;
}

export default function ImageReview({ imageUrl, onApprove, onRegenerate }: Props) {
  return (
    <div className="rounded-xl border overflow-hidden">
      <img src={imageUrl} alt="Generated" className="w-full object-cover" />
    </div>
  );
}
