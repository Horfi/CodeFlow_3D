// frontend/src/components/layout/MainLayout.jsx
import React, { useState, useEffect } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import Header from './Header';
import SplitLayout from './SplitLayout';
import { AlgorithmFactory } from '../../algorithms/factory/AlgorithmFactory';
import { useGraph3D } from '../../hooks/useGraph3D';
import { useUserModel } from '../../hooks/useUserModel';
import { useAnalytics } from '../../hooks/useAnalytics';

const MainLayout = () => {
  const { projectId } = useParams();
  const [searchParams, setSearchParams] = useSearchParams();
  const [version, setVersion] = useState(searchParams.get('version') || 'personalized');
  const [algorithms, setAlgorithms] = useState(null);
  const [projectData, setProjectData] = useState(null);
  const [loading, setLoading] = useState(true);

  const { userModel, updateUserModel } = useUserModel();
  const { graphState, updateGraph } = useGraph3D();
  const { trackInteraction } = useAnalytics();

  useEffect(() => {
    const newAlgorithms = AlgorithmFactory.createSuite(version, userModel);
    setAlgorithms(newAlgorithms);
  }, [version, userModel]);

  useEffect(() => {
    if (projectId) {
      loadProjectData(projectId);
    }
  }, [projectId]);

  const loadProjectData = async (id) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/project/${id}`);
      const data = await response.json();
      setProjectData(data);
      updateGraph(data.graph);
    } catch (error) {
      console.error('Failed to load project:', error);
    }
    setLoading(false);
  };

  const handleVersionSwitch = (newVersion) => {
    setVersion(newVersion);
    setSearchParams({ version: newVersion });
    trackInteraction({
      type: 'version_switch',
      newVersion,
      timestamp: Date.now()
    });
  };

  if (loading) {
    return (
      <div className="loading-container">
        <h2>Loading project...</h2>
      </div>
    );
  }

  return (
    <div className="main-layout">
      <Header 
        onVersionSwitch={handleVersionSwitch}
        currentVersion={version}
      />
      <SplitLayout
        algorithms={algorithms}
        projectData={projectData}
        version={version}
        onInteraction={trackInteraction}
      />
    </div>
  );
};

export default MainLayout;