// frontend/src/algorithms/random/RandomRanking.js
import { RankingInterface } from '../factory/AlgorithmInterface';

export class RandomRanking extends RankingInterface {
  constructor(config) {
    super(null, config);
  }

  sortBookmarks(bookmarks, criteria) {
    const sorted = [...bookmarks];
    
    switch (criteria) {
      case 'name':
        return sorted.sort((a, b) => a.name.localeCompare(b.name));
      case 'date':
        return sorted.sort((a, b) => (b.dateAdded || 0) - (a.dateAdded || 0));
      case 'usage':
      case 'importance':
      default:
        // Random order for usage and importance
        return sorted.sort(() => Math.random() - 0.5);
    }
  }

  getBookmarkStats(bookmark) {
    // No meaningful stats in random version
    return 'Added recently';
  }

  rankFilesByImportance(files) {
    // Random ranking
    return [...files].sort(() => Math.random() - 0.5);
  }
}