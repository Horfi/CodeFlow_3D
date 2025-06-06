// frontend/src/utils/FileUtils.js
export class FileUtils {
  static getFileExtension(filename) {
    return filename.split('.').pop()?.toLowerCase() || '';
  }

  static getFileName(filePath) {
    return filePath.split('/').pop() || filePath;
  }

  static getDirectory(filePath) {
    return filePath.split('/').slice(0, -1).join('/');
  }

  static isImageFile(filename) {
    const imageExtensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp'];
    return imageExtensions.includes(this.getFileExtension(filename));
  }

  static isCodeFile(filename) {
    const codeExtensions = [
      'js', 'jsx', 'ts', 'tsx', 'py', 'java', 'cpp', 'c', 'h',
      'css', 'scss', 'html', 'php', 'rb', 'go', 'rs', 'swift'
    ];
    return codeExtensions.includes(this.getFileExtension(filename));
  }

  static formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  static getRelativePath(fromPath, toPath) {
    const fromParts = fromPath.split('/');
    const toParts = toPath.split('/');
    
    let commonLength = 0;
    while (commonLength < fromParts.length && 
           commonLength < toParts.length && 
           fromParts[commonLength] === toParts[commonLength]) {
      commonLength++;
    }
    
    const upSteps = fromParts.length - commonLength - 1;
    const relativeParts = Array(upSteps).fill('..').concat(toParts.slice(commonLength));
    
    return relativeParts.join('/') || '.';
  }
}
