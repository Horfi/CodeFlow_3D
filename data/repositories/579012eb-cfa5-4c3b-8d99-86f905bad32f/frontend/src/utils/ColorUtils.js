// frontend/src/utils/ColorUtils.js
export class ColorUtils {
  static hexToRgb(hex) {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : null;
  }

  static rgbToHex(r, g, b) {
    return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
  }

  static interpolateColor(color1, color2, factor) {
    const rgb1 = this.hexToRgb(color1);
    const rgb2 = this.hexToRgb(color2);
    
    if (!rgb1 || !rgb2) return color1;
    
    const r = Math.round(rgb1.r + (rgb2.r - rgb1.r) * factor);
    const g = Math.round(rgb1.g + (rgb2.g - rgb1.g) * factor);
    const b = Math.round(rgb1.b + (rgb2.b - rgb1.b) * factor);
    
    return this.rgbToHex(r, g, b);
  }

  static temperatureToColor(temperature) {
    // Map temperature (0-1) to a color gradient from blue to red
    if (temperature <= 0.5) {
      return this.interpolateColor('#0066ff', '#ffff00', temperature * 2);
    } else {
      return this.interpolateColor('#ffff00', '#ff0000', (temperature - 0.5) * 2);
    }
  }

  static importanceToColor(importance) {
    // Map importance (0-1) to a color gradient from gray to gold
    return this.interpolateColor('#666666', '#ffd700', importance);
  }

  static getLanguageColor(language) {
    const colors = {
      'JavaScript': '#f7df1e',
      'TypeScript': '#007acc',
      'Python': '#3776ab',
      'Java': '#ed8b00',
      'C++': '#00599c',
      'C': '#555555',
      'HTML': '#e34f26',
      'CSS': '#1572b6',
      'SCSS': '#cf649a',
      'JSON': '#000000',
      'XML': '#0060ac',
      'YAML': '#cb171e',
      'Markdown': '#083fa1'
    };
    return colors[language] || '#888888';
  }

  static adjustBrightness(color, factor) {
    const rgb = this.hexToRgb(color);
    if (!rgb) return color;
    
    const r = Math.min(255, Math.max(0, rgb.r * factor));
    const g = Math.min(255, Math.max(0, rgb.g * factor));
    const b = Math.min(255, Math.max(0, rgb.b * factor));
    
    return this.rgbToHex(Math.round(r), Math.round(g), Math.round(b));
  }

  static getContrastColor(backgroundColor) {
    const rgb = this.hexToRgb(backgroundColor);
    if (!rgb) return '#000000';
    
    const brightness = (rgb.r * 299 + rgb.g * 587 + rgb.b * 114) / 1000;
    return brightness > 128 ? '#000000' : '#ffffff';
  }
}