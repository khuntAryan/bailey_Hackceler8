from src.tools.phase2_complete_project_builder import CompleteProjectBuilder


def main():
    # STEP 1: Paste your entire LLM response here
    llm_response = """
## Required Dependencies
npm i react react-dom react-router-dom framer-motion lucide-react
npm i -D vite @vitejs/plugin-react tailwindcss postcss autoprefixer

## Environment Variables (.env)
MONGODB_URI=your_mongodb_uri_here
JWT_SECRET=your_jwt_secret_here

// Component: Header
// File: src/components/Header/Header.jsx
import React from 'react';
import { Menu, X } from 'lucide-react';

const Header = () => {
  return (
    <header className="bg-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-6">
          <span className="text-2xl font-bold text-gray-900">My App</span>
          <nav className="hidden md:flex space-x-10">
            <a href="#" className="text-base font-medium text-gray-500 hover:text-gray-900">Home</a>
            <a href="#" className="text-base font-medium text-gray-500 hover:text-gray-900">About</a>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;

// Component: Hero
// File: src/components/Hero/Hero.jsx
import React from 'react';

const Hero = () => {
  return (
    <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white py-20">
      <div className="max-w-7xl mx-auto px-4 text-center">
        <h1 className="text-4xl font-bold mb-4">Welcome to My App</h1>
        <p className="text-xl mb-8">Build amazing things with React and Tailwind</p>
        <button className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100">
          Get Started
        </button>
      </div>
    </div>
  );
};

export default Hero;

// Component: Footer
// File: src/components/Footer/Footer.jsx
import React from 'react';

const Footer = () => {
  return (
    <footer className="bg-gray-800 text-white py-8">
      <div className="max-w-7xl mx-auto px-4 text-center">
        <p>&copy; 2025 My App. All rights reserved.</p>
      </div>
    </footer>
  );
};

export default Footer;
    """
    
    # STEP 2: Create builder and build project
    print("🚀 Building project from LLM response...")
    builder = CompleteProjectBuilder()
    project_path = builder.build_project_from_llm_response(llm_response)
    
    # STEP 3: Show next steps
    print(f"\n✅ Project successfully created!")
    print(f"📂 Location: {project_path}")
    print(f"\n🎯 Next steps:")
    print(f"cd {project_path}")
    print("npm install")
    print("npm run dev")

if __name__ == "__main__":
    main()
