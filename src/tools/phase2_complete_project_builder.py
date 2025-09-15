import os
import re
import json
from datetime import datetime
from typing import Dict, List, Optional

class CompleteProjectBuilder:
    def __init__(self, base_path: str = "generated_projects"):
        self.base_path = base_path
        self.current_project_path = None
        
    def _extract_code_blocks_from_response(self, response: str) -> Dict[str, Dict]:
        """FIXED: Extract code blocks from LLM response with correct regex patterns"""
        components = {}
        print(f"🔍 Parsing response length: {len(response)} characters")
     ##jjdjjd djdjd




        patterns = [
            r'//\s*Component:\s*([^/\n]+)\s*//\s*File:\s*([^\n]+)\s*\n(.*?)(?=//\s*Component:|$)',
            r'//\s*([^/\n]+)\s*\|\s*([^\n]+)\s*\n(.*?)(?=//\s*[^/\n]+\s*\||$)',
            r'``````',

        ]
        
        for i, pattern in enumerate(patterns):
            matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
            print(f"📊 Pattern {i+1} found {len(matches)} matches")
            
            if matches:
                for match in matches:
                    if len(match) == 3:  
                        component_name = match[0].strip()
                        file_path = match[1].strip()
                        code = match[2].strip()
                        
                        if len(code) > 100:  
                            components[component_name] = {
                                'name': component_name,
                                'path': file_path,
                                'code': code
                            }
                            print(f"✅ Extracted {component_name}: {len(code)} chars")
                    elif len(match) == 1:  
                        code = match.strip()
                        if len(code) > 100:

                            name_match = re.search(r'function\s+(\w+)|const\s+(\w+)\s*=', code)
                            if name_match:
                                comp_name = name_match.group(1) or name_match.group(2)
                                components[comp_name] = {
                                    'name': comp_name,
                                    'path': f'src/components/{comp_name}/{comp_name}.jsx',
                                    'code': code
                                }
                                print(f"✅ Extracted {comp_name}: {len(code)} chars")
        

        if not components:
            print("🔄 Using fallback line-by-line parsing...")
            lines = response.split('\n')
            current_component = None
            current_code = []
            
            for line in lines:
                if '// Component:' in line and '// File:' in line:

                    if current_component and current_code:
                        code_str = '\n'.join(current_code).strip()
                        if len(code_str) > 100:
                            components[current_component['name']] = {
                                'name': current_component['name'],
                                'path': current_component['path'], 
                                'code': code_str
                            }
                            print(f"✅ Fallback extracted {current_component['name']}: {len(code_str)} chars")
                    

                    parts = line.split('//')
                    if len(parts) >= 3:
                        comp_name = parts[1].replace('Component:', '').strip()
                        file_path = parts[2].replace('File:', '').strip()
                        current_component = {'name': comp_name, 'path': file_path}
                        current_code = []
                elif current_component:
                    current_code.append(line)
            

            if current_component and current_code:
                code_str = '\n'.join(current_code).strip()
                if len(code_str) > 100:
                    components[current_component['name']] = {
                        'name': current_component['name'],
                        'path': current_component['path'],
                        'code': code_str
                    }
                    print(f"✅ Final fallback extracted {current_component['name']}: {len(code_str)} chars")
        
        print(f"🎯 Total extracted components: {len(components)}")
        return components
    
    def create_component_file(self, project_path: str, component_info: Dict) -> Optional[str]:
        """FIXED: Create component file with proper error handling"""
        try:
            component_name = component_info['name']
            file_path = component_info['path'] 
            code = component_info['code']
            

            if file_path.startswith('./'):
                file_path = file_path[2:]
            if file_path.startswith('src/'):
                file_path = file_path[4:]
                

            full_path = os.path.join(project_path, 'src', file_path)
            

            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            

            clean_code = code
            if clean_code.startswith('```'):
                clean_code = '\n'.join(clean_code.split('\n')[1:-1])
            

            if 'import React' not in clean_code and ('function ' in clean_code or 'const ' in clean_code):
                clean_code = "import React from 'react';\n" + clean_code
            

            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(clean_code)
                
            print(f"✅ Created: {full_path} ({len(clean_code)} characters)")
            return full_path
            
        except Exception as e:
            print(f"❌ Error creating {component_info.get('name', 'unknown')}: {e}")
            return None
    
    def create_project_structure(self, project_name: str) -> str:
        """Create basic project structure"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_path = os.path.join(self.base_path, f"{project_name}_{timestamp}")
        

        directories = [
            'src/components',
            'src/pages',
            'src/hooks',
            'src/utils',
            'src/styles',
            'public'
        ]
        
        for directory in directories:
            os.makedirs(os.path.join(project_path, directory), exist_ok=True)
        

        package_json = {
            "name": project_name.lower().replace(' ', '-'),
            "version": "1.0.0",
            "main": "server.js",
            "scripts": {
                "test": "echo \"Error: no test specified\" && exit 1",
                "start": "node server.js"
            },
            "keywords": [],
            "author": "",
            "license": "ISC",
            "dependencies": {},
            "devDependencies": {}
        }
        
        with open(os.path.join(project_path, 'package.json'), 'w') as f:
            json.dump(package_json, f, indent=2)
        
        self.current_project_path = project_path
        return project_path
    
    def build_complete_project(self, llm_response: str, project_name: str = "LLM_Generated_Project") -> str:
        """MAIN METHOD: Build complete project from LLM response"""
        try:
            print(f"🚀 Starting project build: {project_name}")
            

            project_path = self.create_project_structure(project_name)
            print(f"📁 Created project structure at: {project_path}")
            

            components = self._extract_code_blocks_from_response(llm_response)
            
            if not components:
                print("❌ No components found in response!")
                return project_path
            

            created_files = []
            for component_name, component_info in components.items():
                file_path = self.create_component_file(project_path, component_info)
                if file_path:
                    created_files.append(file_path)
            
            print(f"✅ Successfully created {len(created_files)} component files!")
            print("📝 Created files:")
            for file_path in created_files:
                print(f"   → {file_path}")
            

            self._create_project_summary(project_path, components, created_files)
            
            return project_path
            
        except Exception as e:
            print(f"❌ Error building project: {e}")
            return None
    
    def _create_project_summary(self, project_path: str, components: Dict, created_files: List[str]):
        """Create a summary file for the project"""
        summary = {
            "project_name": os.path.basename(project_path),
            "created_at": datetime.now().isoformat(),
            "total_components": len(components),
            "created_files": created_files,
            "components": {
                name: {
                    "path": info["path"],
                    "size": len(info["code"])
                } for name, info in components.items()
            }
        }
        
        with open(os.path.join(project_path, 'project_summary.json'), 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"📊 Created project summary at: {os.path.join(project_path, 'project_summary.json')}")


if __name__ == "__main__":

    builder = CompleteProjectBuilder()
    

    sample_response = """
// Component: Header
// File: src/components/Header/Header.jsx
import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';

export default function Header() {
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    return (
        <header className="bg-gradient-to-r from-indigo-900 via-purple-900 to-pink-900 text-white shadow-md sticky top-0 z-50">
            <div className="container mx-auto flex justify-between items-center p-5">
                <div className="text-3xl font-extrabold tracking-tight cursor-pointer select-none">
                    <NavLink to="/" className="hover:text-pink-400">PowerGym</NavLink>
                </div>
                {/* Navigation and mobile menu code */}
            </div>
        </header>
    );
}

// Component: Hero
// File: src/components/Hero/Hero.jsx
import React from 'react';

export default function Hero() {
    return (
        <section className="relative bg-gradient-to-br from-pink-700 to-indigo-900 text-white py-28 px-6">
            <div className="max-w-lg space-y-6">
                <h1 className="text-5xl font-extrabold drop-shadow-lg tracking-tight leading-tight">
                    Elevate Your <span className="text-pink-400">Fitness</span> Journey
                </h1>
                <p className="text-lg font-light tracking-wide max-w-md drop-shadow-md">
                    Join PowerGym and get access to elite trainers, world-class equipment, and personalized plans.
                </p>
            </div>
        </section>
    );
}
    """
    

    project_path = builder.build_complete_project(sample_response, "PowerGym_Website")
    print(f"🎉 Project built successfully at: {project_path}")
