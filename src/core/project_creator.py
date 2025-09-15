"""
Enhanced Project Creator that properly structures React projects
"""

import os
import re
import json
from pathlib import Path

class ProjectCreator:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    def create_project(self, user_prompt, enhanced_prompt, generated_code):
        """Create a properly structured React project"""
        try:
            # Create project directory
            project_name = self._generate_project_name(user_prompt)
            project_path = self._create_project_directory(project_name)
            
            # Parse and extract components from generated code
            components = self._parse_generated_code(generated_code)
            
            # Create React project structure
            self._create_react_structure(project_path, components, user_prompt)
            
            return project_path
            
        except Exception as e:
            self.logger.error(f"Project creation failed: {e}")
            return None

    def _parse_generated_code(self, generated_code):
        """Parse generated code and extract components"""
        components = {}
        
        # Extract React components using regex
        component_pattern = r'(?:const|function)\s+(\w+)\s*=?\s*\([^)]*\)\s*(?:=>)?\s*\{([\s\S]*?)\}'
        matches = re.finditer(component_pattern, generated_code, re.MULTILINE)
        
        for match in matches:
            component_name = match.group(1)
            component_code = match.group(0)
            
            if component_name not in ['useState', 'useEffect']:  # Skip hooks
                components[component_name] = self._clean_component_code(component_code)
        
        # If no components found, create default structure
        if not components:
            components = self._create_default_components(generated_code)
        
        return components

    def _create_default_components(self, generated_code):
        """Create default component structure if parsing fails"""
        return {
            'App': self._create_app_component(),
            'Header': self._create_header_component(),
            'MainContent': self._extract_main_content(generated_code),
            'Footer': self._create_footer_component()
        }

    def _create_react_structure(self, project_path, components, user_prompt):
        """Create complete React project structure"""
        
        # Create folder structure
        folders = [
            'src', 'src/components', 'src/pages', 'src/hooks', 
            'src/styles', 'src/assets', 'src/utils', 'public'
        ]
        
        for folder in folders:
            os.makedirs(os.path.join(project_path, folder), exist_ok=True)
        
        # Create package.json
        self._create_package_json(project_path, user_prompt)
        
        # Create component files
        for name, code in components.items():
            self._create_component_file(project_path, name, code)
        
        # Create configuration files
        self._create_config_files(project_path)
        
        # Create styles
        self._create_style_files(project_path)
        
        # Create index.html
        self._create_index_html(project_path, user_prompt)

    def _create_component_file(self, project_path, component_name, component_code):
        """Create individual component file"""
        component_dir = os.path.join(project_path, 'src', 'components', component_name)
        os.makedirs(component_dir, exist_ok=True)
        
        # Create component file
        component_file = os.path.join(component_dir, f'{component_name}.jsx')
        
        # Add proper imports and exports
        full_code = f"""import React from 'react';

{component_code}

export default {component_name};
"""
        
        with open(component_file, 'w') as f:
            f.write(full_code)

    def _create_package_json(self, project_path, user_prompt):
        """Create comprehensive package.json"""
        package_data = {
            "name": self._generate_project_name(user_prompt).lower().replace(' ', '-'),
            "version": "0.1.0",
            "private": True,
            "dependencies": {
                "@testing-library/jest-dom": "^5.16.4",
                "@testing-library/react": "^13.3.0",
                "@testing-library/user-event": "^13.5.0",
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-router-dom": "^6.3.0",
                "react-scripts": "5.0.1",
                "web-vitals": "^2.1.4"
            },
            "devDependencies": {
                "autoprefixer": "^10.4.7",
                "postcss": "^8.4.14",
                "tailwindcss": "^3.1.6"
            },
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build",
                "test": "react-scripts test",
                "eject": "react-scripts eject"
            },
            "eslintConfig": {
                "extends": ["react-app", "react-app/jest"]
            },
            "browserslist": {
                "production": [">0.2%", "not dead", "not op_mini all"],
                "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
            }
        }
        
        with open(os.path.join(project_path, 'package.json'), 'w') as f:
            json.dump(package_data, f, indent=2)
