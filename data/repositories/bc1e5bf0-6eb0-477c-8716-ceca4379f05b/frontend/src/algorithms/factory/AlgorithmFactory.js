// frontend/src/algorithms/factory/AlgorithmFactory.js
import { PersonalizedLayout } from '../personalized/PersonalizedLayout';
import { PersonalizedColoring } from '../personalized/PersonalizedColoring';
import { PersonalizedSearch } from '../personalized/PersonalizedSearch';
import { PersonalizedSuggestions } from '../personalized/PersonalizedSuggestions';
import { PersonalizedFiltering } from '../personalized/PersonalizedFiltering';
import { PersonalizedRanking } from '../personalized/PersonalizedRanking';

import { RandomLayout } from '../random/RandomLayout';
import { RandomColoring } from '../random/RandomColoring';
import { RandomSearch } from '../random/RandomSearch';
import { RandomSuggestions } from '../random/RandomSuggestions';
import { RandomFiltering } from '../random/RandomFiltering';
import { RandomRanking } from '../random/RandomRanking';

import { VersionConfig } from './VersionConfig';

export class AlgorithmFactory {
  static createSuite(version, userModel = null) {
    const config = VersionConfig.getConfig(version);
    
    if (version === 'personalized') {
      return {
        layout: new PersonalizedLayout(userModel, config),
        coloring: new PersonalizedColoring(userModel, config),
        search: new PersonalizedSearch(userModel, config),
        suggestions: new PersonalizedSuggestions(userModel, config),
        filtering: new PersonalizedFiltering(userModel, config),
        ranking: new PersonalizedRanking(userModel, config),
        interactionHandler: this.createInteractionHandler(version, userModel),
        parsing: this.createParsingEngine(version, userModel),
        version: version,
        config: config
      };
    } else if (version === 'random') {
      return {
        layout: new RandomLayout(config),
        coloring: new RandomColoring(config),
        search: new RandomSearch(config),
        suggestions: new RandomSuggestions(config),
        filtering: new RandomFiltering(config),
        ranking: new RandomRanking(config),
        interactionHandler: this.createInteractionHandler(version, null),
        parsing: this.createParsingEngine(version, null),
        version: version,
        config: config
      };
    } else {
      throw new Error(`Unknown algorithm version: ${version}`);
    }
  }

  static createInteractionHandler(version, userModel) {
    return {
      recordInteraction: (interaction) => {
        // Track all interactions for analytics
        if (typeof window !== 'undefined') {
          window.analyticsQueue = window.analyticsQueue || [];
          window.analyticsQueue.push({
            ...interaction,
            version,
            sessionId: this.getSessionId(),
            userId: this.getUserId()
          });
        }

        // Update user model if personalized version
        if (version === 'personalized' && userModel) {
          userModel.updateFromInteraction(interaction);
        }
      },
      
      getInteractionHistory: () => {
        return window.analyticsQueue || [];
      }
    };
  }

  static createParsingEngine(version, userModel) {
    return {
      parseDependencies: async (content, language) => {
        // Simple dependency parsing for frontend
        const dependencies = [];
        
        if (language === 'javascript' || language === 'typescript') {
          const importRegex = /import\s+.*?\s+from\s+['"](.*?)['"];?/g;
          const requireRegex = /require\s*\(\s*['"](.*?)['"]\s*\)/g;
          
          let match;
          while ((match = importRegex.exec(content)) !== null) {
            dependencies.push({
              name: match[1],
              path: match[1],
              type: this.getDependencyType(match[1]),
              line: content.substring(0, match.index).split('\n').length
            });
          }
          
          while ((match = requireRegex.exec(content)) !== null) {
            dependencies.push({
              name: match[1],
              path: match[1],
              type: this.getDependencyType(match[1]),
              line: content.substring(0, match.index).split('\n').length
            });
          }
        } else if (language === 'python') {
          const importRegex = /(?:from\s+([\w.]+)\s+)?import\s+([\w.,\s]+)/g;
          
          let match;
          while ((match = importRegex.exec(content)) !== null) {
            const module = match[1] || match[2];
            dependencies.push({
              name: module,
              path: module,
              type: this.getDependencyType(module),
              line: content.substring(0, match.index).split('\n').length
            });
          }
        }
        
        return dependencies;
      }
    };
  }

  static getDependencyType(path) {
    if (path.startsWith('./') || path.startsWith('../')) return 'relative';
    if (path.startsWith('/') || path.includes('src/')) return 'internal';
    return 'external';
  }

  static getSessionId() {
    if (typeof window !== 'undefined') {
      let sessionId = sessionStorage.getItem('codeflow_session_id');
      if (!sessionId) {
        sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        sessionStorage.setItem('codeflow_session_id', sessionId);
      }
      return sessionId;
    }
    return 'unknown_session';
  }

  static getUserId() {
    if (typeof window !== 'undefined') {
      let userId = localStorage.getItem('codeflow_user_id');
      if (!userId) {
        userId = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('codeflow_user_id', userId);
      }
      return userId;
    }
    return 'unknown_user';
  }

  static switchVersion(currentAlgorithms, newVersion, userModel) {
    return this.createSuite(newVersion, userModel);
  }
}
