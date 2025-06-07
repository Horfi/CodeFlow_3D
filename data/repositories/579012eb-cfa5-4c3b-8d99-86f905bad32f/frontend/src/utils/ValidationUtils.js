// frontend/src/utils/ValidationUtils.js
export class ValidationUtils {
  static isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  static isValidUrl(url) {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  }

  static isValidGitUrl(url) {
    const gitRegex = /^https?:\/\/.*\.git$|^git@.*:.*\.git$|^https?:\/\/github\.com\/.*\/.*$/;
    return gitRegex.test(url);
  }

  static sanitizeFilename(filename) {
    return filename.replace(/[^a-z0-9_.-]/gi, '_');
  }

  static validateFileExtension(filename, allowedExtensions) {
    const ext = filename.split('.').pop()?.toLowerCase();
    return allowedExtensions.includes(ext);
  }

  static isValidJson(str) {
    try {
      JSON.parse(str);
      return true;
    } catch {
      return false;
    }
  }

  static escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  static truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength - 3) + '...';
  }
}