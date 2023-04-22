interface RailwayProps {
  width: number;
  height: number;
}

const Railway: React.FC<React.PropsWithChildren<RailwayProps>> = ({
  width,
  height,
  children,
}) => {
  return (
    <svg width="100%" viewBox={`0 0 ${width} ${height}`}>
      <rect width={width} height={height} fill="#222222" />
      {children}
    </svg>
  );
};

export default Railway;
