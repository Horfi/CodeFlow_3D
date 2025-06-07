// frontend/src/algorithms/factory/VersionConfig.js
export class VersionConfig {
  static getConfig(version) {
    const configs = {
      personalized: {
        enableUserTracking: true,
        enableAISuggestions: true,
        enableTemperatureColoring: true,
        enableSmartLayout: true,
        enablePatternAnalysis: true,
        layoutPhysics: {
          linkStrength: 0.7,
          chargeStrength: -500,
          gravityStrength: 0.1,
          alphaDecay: 0.02
        },
        colorScheme: {
          temperature: true,
          importance: true,
          usage: true
        },
        searchRanking: {
          useML: true,
          personalizeResults: true,
          contextAware: true
        },
        suggestions: {
          maxSuggestions: 8,
          algorithms: ['dependency', 'pattern', 'similarity', 'centrality'],
          confidenceThreshold: 0.3
        }
      },
      
      random: {
        enableUserTracking: false,
        enableAISuggestions: false,
        enableTemperatureColoring: false,
        enableSmartLayout: false,
        enablePatternAnalysis: false,
        layoutPhysics: {
          linkStrength: 0.5,
          chargeStrength: -300,
          gravityStrength: 0.05,
          alphaDecay: 0.01
        },
        colorScheme: {
          temperature: false,
          importance: false,
          usage: false
        },
        searchRanking: {
          useML: false,
          personalizeResults: false,
          contextAware: false
        },
        suggestions: {
          maxSuggestions: 5,
          algorithms: ['random'],
          confidenceThreshold: 0.0
        }
      }
    };

    return configs[version] || configs.personalized;
  }

  static validateConfig(config) {
    const required = ['enableUserTracking', 'layoutPhysics', 'colorScheme'];
    return required.every(key => key in config);
  }

  static mergeConfigs(base, override) {
    return {
      ...base,
      ...override,
      layoutPhysics: { ...base.layoutPhysics, ...override.layoutPhysics },
      colorScheme: { ...base.colorScheme, ...override.colorScheme },
      searchRanking: { ...base.searchRanking, ...override.searchRanking },
      suggestions: { ...base.suggestions, ...override.suggestions }
    };
  }
}