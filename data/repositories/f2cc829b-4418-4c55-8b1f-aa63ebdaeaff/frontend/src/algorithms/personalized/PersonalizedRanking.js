// frontend/src/algorithms/personalized/PersonalizedRanking.js
import { RankingInterface } from '../factory/AlgorithmInterface';

export class PersonalizedRanking extends RankingInterface {
  constructor(userModel, config) {
    super(userModel, config);
  }

  sortBookmarks(bookmarks, criteria) {
    const sorted = [...bookmarks];
    
    switch (criteria) {
      case 'usage':
        return sorted.sort((a, b) => {
          const usageA = this.userModel?.getFileInteractionCount(a.path) || 0;
          const usageB = this.userModel?.getFileInteractionCount(b.path) || 0;
          return usageB - usageA;
        });
        
      case 'date':
        return sorted.sort((a, b) => (b.dateAdded || 0) - (a.dateAdded || 0));
        
      case 'name':
        return sorted.sort((a, b) => a.name.localeCompare(b.name));
        
      case 'importance':
        return sorted.sort((a, b) => {
          const importanceA = this.userModel?.getFileImportance(a.path) || 0;
          const importanceB = this.userModel?.getFileImportance(b.path) || 0;
          return importanceB - importanceA;
        });
        
      default:
        return sorted;
    }
  }

  getBookmarkStats(bookmark) {
    if (!this.userModel) return '';
    
    const interactions = this.userModel.getFileInteractionCount(bookmark.path) || 0;
    const lastAccess = this.userModel.getLastAccessTime(bookmark.path);
    
    let stats = `${interactions} clicks`;
    
    if (lastAccess) {
      const hoursAgo = Math.floor((Date.now() - lastAccess) / (1000 * 60 * 60));
      if (hoursAgo < 1) {
        stats += ', just now';
      } else if (hoursAgo < 24) {
        stats += `, ${hoursAgo}h ago`;
      } else {
        const daysAgo = Math.floor(hoursAgo / 24);
        stats += `, ${daysAgo}d ago`;
      }
    }
    
    return stats;
  }

  rankFilesByImportance(files) {
    if (!this.userModel) {
      return files.sort((a, b) => a.name.localeCompare(b.name));
    }

    return files.sort((a, b) => {
      const scoreA = this.calculatePersonalizedImportance(a);
      const scoreB = this.calculatePersonalizedImportance(b);
      return scoreB - scoreA;
    });
  }

  calculatePersonalizedImportance(file) {
    const interactions = this.userModel?.getFileInteractionCount(file.path) || 0;
    const timeSpent = this.userModel?.getTotalTimeSpent(file.path) || 0;
    const recency = this.userModel?.getFileRecencyScore(file.path) || 0;
    const graphImportance = file.importance?.total_score || 0;

    // Weighted combination
    return (
      interactions * 0.3 +
      timeSpent * 0.2 +
      recency * 0.2 +
      graphImportance * 0.3
    );
  }
}