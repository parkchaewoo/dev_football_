interface BallHeightSliderProps {
  height: number;
  onChange: (height: number) => void;
  disabled?: boolean;
}

export default function BallHeightSlider({
  height,
  onChange,
  disabled,
}: BallHeightSliderProps) {
  return (
    <div className="flex items-center gap-2 p-2 bg-gray-800 rounded-lg">
      <span className="text-xs text-gray-400 whitespace-nowrap">공 높이:</span>
      <input
        type="range"
        min={0.22}
        max={8}
        step={0.1}
        value={height}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        disabled={disabled}
        className="flex-1 h-1 accent-yellow-500"
      />
      <span className="text-xs text-gray-300 w-12 text-right">
        {height <= 0.3 ? '지면' : `${(height - 0.22).toFixed(1)}m`}
      </span>
    </div>
  );
}
