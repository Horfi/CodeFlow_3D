// frontend/src/hooks/useAnalytics.js
import { useCallback } from 'react';
import AnalyticsService from '../services/AnalyticsService';

export const useAnalytics = () => {
  const trackInteraction = useCallback((interaction) => {
    AnalyticsService.track(interaction);
  }, []);

  const trackPageView = useCallback((page) => {
    AnalyticsService.trackPageView(page);
  }, []);

  const trackFileInteraction = useCallback((type, filePath, details) => {
    AnalyticsService.trackFileInteraction(type, filePath, details);
  }, []);

  const trackGraphInteraction = useCallback((type, nodeId, details) => {
    AnalyticsService.trackGraphInteraction(type, nodeId, details);
  }, []);

  const trackSearch = useCallback((query, resultCount, version) => {
    AnalyticsService.trackSearch(query, resultCount, version);
  }, []);

  const trackVersionSwitch = useCallback((fromVersion, toVersion) => {
    AnalyticsService.trackVersionSwitch(fromVersion, toVersion);
  }, []);

  const trackTaskCompletion = useCallback((taskType, duration, success) => {
    AnalyticsService.trackTaskCompletion(taskType, duration, success);
  }, []);

  const trackError = useCallback((error, context) => {
    AnalyticsService.trackError(error, context);
  }, []);

  return {
    trackInteraction,
    trackPageView,
    trackFileInteraction,
    trackGraphInteraction,
    trackSearch,
    trackVersionSwitch,
    trackTaskCompletion,
    trackError
  };
};
