interface PlatformProps {
  position: { x: number; y: number };
}

export const Platform: React.FC<PlatformProps> = ({ position }) => {
  const width = 60;
  const height = 20;
  return (
    <rect
      x={position.x - width / 2}
      y={position.y - height / 2}
      width={width}
      height={height}
      fill="white"
    />
  );
};
