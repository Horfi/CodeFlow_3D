/ frontend/src/components/shared/Button.jsx
import React from 'react';

const Button = ({ 
  children, 
  onClick, 
  disabled = false, 
  size = 'medium', 
  variant = 'default',
  type = 'button',
  className = '',
  title,
  ...props 
}) => {
  const getButtonClass = () => {
    let classes = ['btn'];
    
    // Size classes
    classes.push(`btn-${size}`);
    
    // Variant classes
    classes.push(`btn-${variant}`);
    
    // State classes
    if (disabled) classes.push('btn-disabled');
    
    // Custom classes
    if (className) classes.push(className);
    
    return classes.join(' ');
  };

  return (
    <button
      type={type}
      className={getButtonClass()}
      onClick={onClick}
      disabled={disabled}
      title={title}
      {...props}
    >
      {children}
    </button>
  );
};

export default Button;