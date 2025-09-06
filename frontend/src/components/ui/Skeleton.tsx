import React from 'react';

export const Skeleton: React.FC<{ className?: string } & React.HTMLAttributes<HTMLDivElement>> = ({ className = '', ...props }) => (
  <div
    className={`animate-pulse rounded-md bg-gray-200 dark:bg-gray-800 ${className}`}
    aria-hidden
    {...props}
  />
);

export default Skeleton;

