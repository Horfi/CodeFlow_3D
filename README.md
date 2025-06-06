# CodeFlow 3D

**AI-Augmented Codebase Dependency Explorer**

---

## Overview

CodeFlow 3D is a next-generation 3D code visualization tool designed to help developers navigate and understand complex codebases. Leveraging AI-powered personalization alongside a control-mode baseline, CodeFlow 3D enables rigorous comparison of how personalized recommendations and layouts impact developer productivity and satisfaction.

---

## Key Features

- **Immersive 3D Graph View**  
  Visualize file dependencies as an interactive 3D graph. Nodes represent files, edges represent import relationships, and folder context is shown via badges and floating labels.

- **Dual-Mode Operation (A/B Testing)**  
  - **Personalized Mode**: Layouts, colors, search results, and suggestions adapt in real time to each user’s interactions and preferences.  
  - **Random Mode**: Serves as a control condition with static, random placements and non-adaptive behaviors to assess personalization impact.

- **Centrality-Based Layout**  
  Files are ranked by a combination of PageRank-style importance, betweenness, degree, and eigenvector centrality to position the most critical files at the graph’s center.

- **AI-Driven Personalization**  
  Continuous user modeling captures click counts, time spent, edit history, language preferences, and navigation patterns to compute a “temperature” score for each file. High-temperature files are emphasized via color and placement.

- **Collapsible Panels & Smart UI Components**  
  - **Bookmarks Panel**: Sort and manage favorite files by usage, date, or importance.  
  - **Language Filter Panel**: Toggle language-specific filters with usage bars and quick select/clear/reset controls.  
  - **Search & Suggestions Panel**: Combines plain-text search with AI-ranked results and contextual file recommendations.

- **Integrated Code Editor**  
  Built on Monaco, the editor supports syntax highlighting for multiple languages, intelligent autocomplete (in personalized mode), real-time dependency detection, and seamless copy/save interactions.

- **Real-Time Graph Updates**  
  As code is edited, dependency changes are detected automatically and the 3D graph is updated on the fly.

- **Comprehensive Analytics & User Study Support**  
  Logs detailed interaction events (clicks, edits, navigation), supports task scenarios for A/B testing, and integrates pre-/post-user questionnaires and emotion assessment scales for HCI research.

---

## Architecture Overview

### 1. Frontend (React + Three.js)

- **Main App Component**  
  Initializes version (personalized vs. random) and injects the corresponding algorithm suite into child components.

- **Algorithm Factory**  
  Creates either a personalized or random implementation of all visualization and interaction algorithms, including layout, coloring, search, suggestions, filtering, and ranking.

- **3D Graph Renderer**  
  Uses Three.js to build and animate the graph.  
  - **Node Renderer**: Generates spheres sized by importance and colored by temperature or randomly.  
  - **Edge Renderer**: Draws curved tubes between nodes for clarity.  
  - **Folder Badge & Labels**: Adds small icons indicating each file’s folder, plus floating text labels grouping files by directory.

- **Collapsible Panel System**  
  Provides reusable panel components (Bookmarks, Language Filters, Search & Suggestions) that can be expanded or collapsed. Each panel interacts with the algorithm suite to display sorted/filter data and AI suggestions.

- **Advanced Code Editor Module**  
  Encapsulates:  
  - **Editor Initialization**: Sets up Monaco with multi-language support, intelligent autocomplete (personalized mode), and change listeners.  
  - **Dependency Analysis**: Parses content on change, detects new imports, and notifies the graph for real-time updates.  
  - **Interaction Tracking**: Records file opens, edits, copies, and saves to the user model.

### 2. Backend (Python Flask/FastAPI)

- **API Layer**  
  - **Repository Routes**: Clone, watch, and manage Git repositories.  
  - **Graph Routes**: Serve dependency graphs and centrality scores to the frontend.  
  - **File Routes**: Fetch and save file contents.  
  - **Analytics Routes**: Log and retrieve user interaction events.

- **Services & Business Logic**  
  - **RepositoryManager**: Handles Git cloning and triggers parsing.  
  - **ParserFactory**: Returns appropriate parser for each file type (e.g., Python, JavaScript).  
  - **GraphBuilder**: Builds dependency graph from parsed files.  
  - **CentralityCalculator**: Computes PageRank, betweenness, degree, and eigenvector centrality.  
  - **UserModelEngine**: Manages the user model and updates it in real time.  
  - **PersonalizationFactory**: Provides temperature scoring, context-aware suggestions, and other AI-powered features.  
  - **AnalyticsCollector**: Logs interaction events, tracks sessions, and gathers metrics for the user study.

- **Data Persistence**  
  - **SQLiteManager**: Interacts with the SQLite database.  
  - **UserDataManager**, **GraphDataManager**, **AnalyticsDataManager**: Handle CRUD operations for user data, graph structures, and analytics logs.

---

## Folder Structure (Key Directories)

