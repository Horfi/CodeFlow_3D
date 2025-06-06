/ frontend/src/hooks/useUserModel.js
import { useState, useEffect } from 'react';
import UserModelService from '../services/UserModelService';

export const useUserModel = () => {
  const [userModel, setUserModel] = useState(UserModelService.userModel);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load initial user model
    const loadModel = async () => {
      try {
        await UserModelService.loadUserModel();
        setUserModel(UserModelService.userModel);
      } catch (error) {
        console.error('Failed to load user model:', error);
      } finally {
        setLoading(false);
      }
    };

    loadModel();
  }, []);

  const updateUserModel = (interaction) => {
    UserModelService.updateFromInteraction(interaction);
    setUserModel({ ...UserModelService.userModel });
  };

  const getFileTemperature = (filePath) => {
    return UserModelService.getFileTemperature(filePath);
  };

  const getFileImportance = (filePath) => {
    return UserModelService.getFileImportance(filePath);
  };

  const getLanguagePreferences = () => {
    return UserModelService.getLanguagePreferences();
  };

  const saveModel = async () => {
    try {
      await UserModelService.saveUserModel();
    } catch (error) {
      console.error('Failed to save user model:', error);
    }
  };

  return {
    userModel,
    loading,
    updateUserModel,
    getFileTemperature,
    getFileImportance,
    getLanguagePreferences,
    saveModel
  };
};
