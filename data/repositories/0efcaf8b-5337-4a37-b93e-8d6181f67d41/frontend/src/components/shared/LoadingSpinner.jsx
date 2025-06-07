// frontend/src/components/shared/LoadingSpinner.jsx
import React from 'react';

const LoadingSpinner = ({ 
  size = 'medium', 
  color = 'primary',
  text,
  className = '' 
}) => {
  const getSpinnerClass = () => {
    let classes = ['loading-spinner'];
    classes.push(`spinner-${size}`);
    classes.push(`spinner-${color}`);
    if (className) classes.push(className);
    return classes.join(' ');
  };

  return (
    <div className={getSpinnerClass()}>
      <div className="spinner-circle">
        <div className="spinner-inner" />
      </div>
      {text && <div className="spinner-text">{text}</div>}
    </div>
  );
};

export default LoadingSpinner;