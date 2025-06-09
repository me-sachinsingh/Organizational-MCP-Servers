# MCP Admin Dashboard

This project is the frontend interface for the MCP Organizational Knowledge Servers. It provides a user-friendly dashboard for managing documents, servers, and search functionalities related to organizational knowledge.

## Project Structure

The project is organized into several key directories:

- **src**: Contains the source code for the application.
  - **components**: Reusable UI components categorized by functionality.
  - **pages**: Main application pages that utilize the components.
  - **services**: API and WebSocket service handlers.
  - **hooks**: Custom React hooks for managing state and side effects.
  - **types**: TypeScript type definitions for various data structures.
  - **utils**: Utility functions and constants.
  - **styles**: CSS styles for the application.
  - **App.tsx**: Main application component.
  - **main.tsx**: Entry point for the application.

- **public**: Contains static assets like the favicon and HTML file.

- **Configuration Files**: Includes `package.json`, `tsconfig.json`, and others for project setup and dependencies.

## Getting Started

To get started with the MCP Admin Dashboard, follow these steps:

1. **Clone the Repository**:
   ```
   git clone <repository-url>
   cd mcp-admin-dashboard
   ```

2. **Install Dependencies**:
   ```
   npm install
   ```

3. **Run the Development Server**:
   ```
   npm run dev
   ```

4. **Open in Browser**:
   Navigate to `http://localhost:3000` to view the application.

## Features

- **Dashboard**: Overview of server statuses and metrics.
- **Document Management**: Upload, view, and manage documents.
- **Server Management**: Configure and monitor server statuses.
- **Search Functionality**: Search and filter documents efficiently.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.