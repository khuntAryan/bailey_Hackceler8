import os
import re
import json
from pathlib import Path
from datetime import datetime

class CompleteProjectBuilder:
    def __init__(self):
        self.project_data = {
            'dependencies': {},
            'dev_dependencies': {},
            'api_keys': [],
            'components': [],
            'has_backend': False,
            'has_frontend': True,
            'framework': 'react',
            'build_tool': 'vite',
            'css_framework': 'tailwindcss'
        }
        
    def find_latest_perplexity_file(self):
        """Find the most recent Perplexity response file"""
        perplexity_dir = Path.home() / 'Desktop' / 'Perplexity_Responses'
        
        if not perplexity_dir.exists():
            raise FileNotFoundError(f"Directory not found: {perplexity_dir}")
        
        response_files = list(perplexity_dir.glob('perplexity_response_*.txt'))
        if not response_files:
            raise FileNotFoundError("No perplexity_response_*.txt files found!")
        
        latest_file = max(response_files, key=lambda f: f.stat().st_mtime)
        print(f"📁 Using LLM output: {latest_file}")
        return latest_file
    
    def parse_dependencies_section(self, content):
        """Parse dependencies and API keys from the top of the file"""
        lines = content.split('\n')
        
        # Look for dependency installation commands
        dependency_patterns = [
            r'npm\s+i(?:nstall)?\s+(.*)',
            r'npm\s+i(?:nstall)?\s+-D\s+(.*)',  # dev dependencies
            r'npm\s+install\s+(.*)'
        ]
        
        for line in lines[:50]:  # Check first 50 lines
            line = line.strip()
            
            # Parse npm install commands
            for pattern in dependency_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    packages = match.group(1).strip()
                    # Split packages and clean them
                    pkg_list = [pkg.strip() for pkg in packages.split() if pkg.strip()]
                    
                    if '-D' in line or 'dev' in line.lower():
                        for pkg in pkg_list:
                            self.project_data['dev_dependencies'][pkg] = 'latest'
                    else:
                        for pkg in pkg_list:
                            self.project_data['dependencies'][pkg] = 'latest'
        
        # Parse API keys section
        api_section = False
        for line in lines[:100]:  # Check first 100 lines
            if 'API Keys' in line or '.env' in line:
                api_section = True
                continue
            if api_section and line.strip().startswith(('MONGODB', 'JWT', 'CLOUDINARY', 'STRIPE', 'EMAIL', 'PORT')):
                key_name = line.split('=')[0].strip()
                self.project_data['api_keys'].append(key_name)
            if api_section and (line.strip() == '' or line.startswith('#')):
                continue
            if api_section and not line.strip().isupper() and '=' not in line:
                break
        
        # Detect project characteristics
        deps_str = str(self.project_data['dependencies']) + str(self.project_data['dev_dependencies'])
        
        if 'express' in deps_str or 'mongoose' in deps_str:
            self.project_data['has_backend'] = True
        if 'next' in deps_str:
            self.project_data['framework'] = 'nextjs'
            self.project_data['build_tool'] = 'next'
        if 'vite' in deps_str:
            self.project_data['build_tool'] = 'vite'
        if 'tailwind' in deps_str:
            self.project_data['css_framework'] = 'tailwindcss'
            
        print(f"✅ Detected: {len(self.project_data['dependencies'])} dependencies")
        print(f"✅ Detected: {len(self.project_data['dev_dependencies'])} dev dependencies")
        print(f"✅ Detected: {len(self.project_data['api_keys'])} API keys")
    
    def extract_code_components(self, content):
        """Extract all code components from the content"""
        lines = content.split('\n')
        components = []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith('// Component:'):
                component_name = line.replace('// Component:', '').strip()
                
                # Next line should be // File:
                if i + 1 < len(lines) and lines[i + 1].strip().startswith('// File:'):
                    file_path = lines[i + 1].strip().replace('// File:', '').strip()
                    
                    # Collect code until next // Component: or end
                    code_lines = []
                    j = i + 2
                    while j < len(lines):
                        if lines[j].strip().startswith('// Component:'):
                            break
                        code_lines.append(lines[j].rstrip())
                        j += 1
                    
                    # Join and clean code
                    code = '\n'.join(code_lines).strip()
                    
                    # Remove language markers
                    for lang in ['jsx', 'javascript', 'js', 'typescript', 'ts', 'tsx', 'bash', 'json']:
                        if code.startswith(f'{lang}\n'):
                            code = code[len(lang)+1:]
                            break
                    
                    # Remove markdown code fences
                    if code.startswith('```'):
                        code = '\n'.join(code.split('\n')[1:])
                    if code.endswith('```'):
                        code = '\n'.join(code.split('\n')[:-1])
                    
                    code = code.strip()
                    
                    # Only include substantial code
                    if len(code) > 50:
                        components.append({
                            'name': component_name,
                            'file_path': file_path,
                            'code': code
                        })
                    
                    i = j - 1
            i += 1
        
        self.project_data['components'] = components
        print(f"✅ Extracted: {len(components)} code components")
        return components
    
    def generate_package_json(self, project_dir):
        """Generate package.json with all detected dependencies"""
        # Ensure we have minimum required dependencies
        if not self.project_data['dependencies']:
            self.project_data['dependencies'] = {
                'react': '^18.2.0',
                'react-dom': '^18.2.0'
            }
        
        if not self.project_data['dev_dependencies']:
            self.project_data['dev_dependencies'] = {
                '@vitejs/plugin-react': '^4.0.0',
                'vite': '^4.4.0'
            }
        
        # Add Tailwind if detected
        if self.project_data['css_framework'] == 'tailwindcss':
            self.project_data['dev_dependencies'].update({
                'tailwindcss': '^3.3.0',
                'postcss': '^8.4.24',
                'autoprefixer': '^10.4.14'
            })
        
        package_json = {
            "name": "llm-generated-project",
            "private": True,
            "version": "0.0.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "lint": "eslint . --ext js,jsx,ts,tsx --report-unused-disable-directives --max-warnings 0",
                "preview": "vite preview"
            },
            "dependencies": self.project_data['dependencies'],
            "devDependencies": self.project_data['dev_dependencies']
        }
        
        # Add backend scripts if backend detected
        if self.project_data['has_backend']:
            package_json["scripts"]["server"] = "node server.js"
            package_json["scripts"]["start"] = "npm run server"
        
        package_json_path = project_dir / 'package.json'
        with open(package_json_path, 'w', encoding='utf-8') as f:
            json.dump(package_json, f, indent=2)
        
        print("✅ Generated: package.json")
        return package_json_path
    
    def generate_vite_config(self, project_dir):
        """Generate vite.config.js"""
        vite_config = '''import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    open: true
  }
})
'''
        vite_config_path = project_dir / 'vite.config.js'
        with open(vite_config_path, 'w', encoding='utf-8') as f:
            f.write(vite_config)
        
        print("✅ Generated: vite.config.js")
        return vite_config_path
    
    def generate_tailwind_config(self, project_dir):
        """Generate tailwind.config.js if Tailwind is used"""
        if self.project_data['css_framework'] != 'tailwindcss':
            return None
            
        tailwind_config = '''/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
'''
        tailwind_config_path = project_dir / 'tailwind.config.js'
        with open(tailwind_config_path, 'w', encoding='utf-8') as f:
            f.write(tailwind_config)
        
        print("✅ Generated: tailwind.config.js")
        return tailwind_config_path
    
    def generate_postcss_config(self, project_dir):
        """Generate postcss.config.js if Tailwind is used"""
        if self.project_data['css_framework'] != 'tailwindcss':
            return None
            
        postcss_config = '''export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
'''
        postcss_config_path = project_dir / 'postcss.config.js'
        with open(postcss_config_path, 'w', encoding='utf-8') as f:
            f.write(postcss_config)
        
        print("✅ Generated: postcss.config.js")
        return postcss_config_path
    
    def generate_index_html(self, project_dir):
        """Generate index.html"""
        index_html = '''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>LLM Generated Project</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
'''
        index_html_path = project_dir / 'index.html'
        with open(index_html_path, 'w', encoding='utf-8') as f:
            f.write(index_html)
        
        print("✅ Generated: index.html")
        return index_html_path
    
    def generate_main_jsx(self, project_dir):
        """Generate src/main.jsx"""
        src_dir = project_dir / 'src'
        src_dir.mkdir(exist_ok=True)
        
        main_jsx = '''import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
'''
        main_jsx_path = src_dir / 'main.jsx'
        with open(main_jsx_path, 'w', encoding='utf-8') as f:
            f.write(main_jsx)
        
        print("✅ Generated: src/main.jsx")
        return main_jsx_path
    
    def generate_index_css(self, project_dir):
        """Generate src/index.css"""
        src_dir = project_dir / 'src'
        src_dir.mkdir(exist_ok=True)
        
        if self.project_data['css_framework'] == 'tailwindcss':
            index_css = '''@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  font-family: Inter, system-ui, Avenir, Helvetica, Arial, sans-serif;
  line-height: 1.5;
  font-weight: 400;
}

body {
  margin: 0;
  display: flex;
  place-items: center;
  min-width: 320px;
  min-height: 100vh;
}

#root {
  width: 100%;
  margin: 0 auto;
}
'''
        else:
            index_css = '''body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}

#root {
  width: 100%;
  margin: 0 auto;
}
'''
        
        index_css_path = src_dir / 'index.css'
        with open(index_css_path, 'w', encoding='utf-8') as f:
            f.write(index_css)
        
        print("✅ Generated: src/index.css")
        return index_css_path
    
    def generate_env_file(self, project_dir):
        """Generate .env.example with detected API keys"""
        if not self.project_data['api_keys']:
            return None
        
        env_content = "# Environment Variables\n"
        env_content += "# Copy this file to .env and fill in your actual values\n\n"
        
        for key in self.project_data['api_keys']:
            env_content += f"{key}=your_{key.lower()}_here\n"
        
        env_path = project_dir / '.env.example'
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print(f"✅ Generated: .env.example with {len(self.project_data['api_keys'])} API keys")
        return env_path
    
    def create_component_files(self, project_dir):
        """Create all component files in their proper directories"""
        created_files = []
        
        for component in self.project_data['components']:
            file_path = project_dir / component['file_path'].lstrip('/')
            
            # Create parent directories
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write the component code
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(component['code'])
            
            created_files.append(file_path)
            print(f"✅ Created: {component['file_path']}")
        
        return created_files
    
    def generate_readme(self, project_dir):
        """Generate README.md with setup instructions"""
        readme_content = f'''# LLM Generated Project

This project was automatically generated from an LLM response on {datetime.now().strftime('%Y-%m-%d')}.

## Setup Instructions

1. **Install dependencies:**
npm install

2. **Set up environment variables (if needed):**
cp .env.example .env  

3. **Run the development server:**
npm run dev

4. **Open your browser:**
Visit [http://localhost:3000](http://localhost:3000)

## Project Structure

- `src/components/` - React components
- `src/pages/` - Page components
- `src/` - Main application files
- `public/` - Static assets

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
'''

        if self.project_data['has_backend']:
            readme_content += '''
## Backend

- `npm run server` - Start backend server
- `npm start` - Start both frontend and backend
'''

        readme_content += f'''
## Generated Components

{len(self.project_data['components'])} components were automatically created:

'''
        for component in self.project_data['components']:
            readme_content += f"- `{component['file_path']}` - {component['name']}\n"

        readme_path = project_dir / 'README.md'
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print("✅ Generated: README.md")
        return readme_path
    
    def build_complete_project(self):
        """Main method to build the complete project"""
        try:
            print("🚀 Starting Complete Project Builder...")
            print("="*60)
            
            # Step 1: Find latest Perplexity file
            latest_file = self.find_latest_perplexity_file()
            
            # Step 2: Read content
            with open(latest_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Step 3: Parse dependencies and API keys
            print("\n📋 Parsing dependencies and configuration...")
            self.parse_dependencies_section(content)
            
            # Step 4: Extract code components
            print("\n🔧 Extracting code components...")
            self.extract_code_components(content)
            
            if not self.project_data['components']:
                raise RuntimeError("No code components found! Check your text file format.")
            
            # Step 5: Create project directory
            project_dir = Path.home() / 'Desktop' / 'LLM_Generated_Project'
            if project_dir.exists():
                print(f"\n🗑️  Removing existing project directory...")
                import shutil
                shutil.rmtree(project_dir)
            
            project_dir.mkdir(parents=True, exist_ok=True)
            print(f"\n📁 Created project directory: {project_dir}")
            
            # Step 6: Generate all configuration files
            print("\n⚙️  Generating configuration files...")
            self.generate_package_json(project_dir)
            self.generate_vite_config(project_dir)
            self.generate_tailwind_config(project_dir)
            self.generate_postcss_config(project_dir)
            self.generate_index_html(project_dir)
            self.generate_main_jsx(project_dir)
            self.generate_index_css(project_dir)
            self.generate_env_file(project_dir)
            
            # Step 7: Create all component files
            print("\n📝 Creating component files...")
            created_files = self.create_component_files(project_dir)
            
            # Step 8: Generate README
            self.generate_readme(project_dir)
            
            # Success summary
            print("\n" + "="*60)
            print("🎉 PROJECT BUILD COMPLETE!")
            print("="*60)
            print(f"📂 Project Location: {project_dir}")
            print(f"📦 Dependencies: {len(self.project_data['dependencies'])} + {len(self.project_data['dev_dependencies'])} dev")
            print(f"🔧 Components: {len(self.project_data['components'])}")
            print(f"🔑 API Keys: {len(self.project_data['api_keys'])}")
            
            print(f"\n⚡ Next Steps:")
            print(f"1. cd {project_dir}")
            print(f"2. npm install")
            print(f"3. npm run dev")
            print(f"4. Open http://localhost:3000")
            
            if self.project_data['api_keys']:
                print(f"5. Copy .env.example to .env and add your API keys")
            
            print("\n🚀 Your project is ready to run!")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            raise

# Main execution
if __name__ == "__main__":
    builder = CompleteProjectBuilder()
    builder.build_complete_project()
