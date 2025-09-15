"""
AI Website Generator v2.0
Standalone version with embedded configuration
"""

import os
import sys
import time
from datetime import datetime
import logging


current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)


DEFAULT_CONFIG = {
    'browser': {'debug_port': 9222},
    'urls': {
        'flexos': 'https://www.flexos.work/design/prompt',
        'perplexity': 'https://www.perplexity.ai'
    },
    'timeouts': {
        'page_load': 20,
        'element_wait': 15,
        'response_wait': 60
    },
    'project': {
        'output_directory': '~/Desktop',
        'project_prefix': 'AI_Generated_'
    }
}

class AIWebsiteGenerator:
    def __init__(self):
        self.config = DEFAULT_CONFIG
        self.logger = self._setup_logging()
        self.brave_controller = None
        self.prompt_enhancer = None
        self.code_generator = None
        self.project_creator = None
        self.start_time = None
        self.projects_created = 0

    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)

    def print_banner(self):
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║              🤖 AI WEBSITE GENERATOR v2.0                   ║
║                                                              ║
║    FlexOS Enhancement + Perplexity Pro + Brave Browser      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝"""
        print(banner)

    def get_user_input(self):
        print("🎯 AI WEBSITE GENERATOR")
        print("=" * 60)
        print("I'll create a complete, modern website for you!")
        print("The process: Your idea → Optional AI Enhancement → Pro Generation → Ready Project")
        print()

        while True:
            user_prompt = input("📝 Describe the website you want to create: ").strip()
            if not user_prompt:
                print("❌ Please provide a description for your website.")
                continue
            elif len(user_prompt) < 10:
                print("❌ Please provide a more detailed description (at least 10 characters).")
                continue
            else:
                break
        print(f"📋 You want to create: {user_prompt}")

        while True:
            proceed = input("✅ Proceed with this project? (y/n): ").strip().lower()
            if proceed in ['y', 'yes']:
                break
            elif proceed in ['n', 'no']:
                print("❌ Project cancelled.")
                return None, None
            else:
                print("❌ Please enter 'y' for yes or 'n' for no")
        print()
        enhance_choice = self._get_enhancement_choice()
        return user_prompt, enhance_choice

    def _get_enhancement_choice(self):
        print("🔧 PROMPT ENHANCEMENT OPTION")
        print("=" * 60)
        print("Would you like to enhance your prompt using AI before sending to Perplexity?")
        print()
        print("✅ YES: Your prompt will be enhanced with detailed technical specifications")
        print("⚡ NO:  Skip enhancement and use your original prompt directly")
        print()
        while True:
            choice = input("🤖 Enhance prompt with AI? (y/n): ").strip().lower()
            if choice in ['y', 'yes']:
                print("✅ Prompt will be enhanced using FlexOS AI")
                return True
            elif choice in ['n', 'no']:
                print("⚡ Skipping enhancement - using original prompt directly")
                return False
            else:
                print("❌ Please enter 'y' for yes or 'n' for no")

    def initialize_components(self):
        try:
            print("🔧 Initializing components...")
            from core.brave_controller import BraveController
            self.brave_controller = BraveController(self.config, self.logger)
            if not self.brave_controller.connect_to_browser():
                print("❌ Failed to connect to Brave browser")
                print("💡 Make sure Brave is closed before running this script")
                return False
            print("✅ Successfully connected to Brave browser!")
            from core.prompt_enhancer import PromptEnhancer
            from core.code_generator import CodeGenerator
            from tools.phase2_complete_project_builder import CompleteProjectBuilder
            self.prompt_enhancer = PromptEnhancer(self.brave_controller, self.config, self.logger)
            self.code_generator = CodeGenerator(self.brave_controller, self.config, self.logger)
            self.project_creator = CompleteProjectBuilder()
            return True
        except ImportError as e:
            print(f"❌ Missing component: {e}")
            print("❌ Please ensure all required modules are in place.")
            return False
        except Exception as e:
            self.logger.error(f"Component initialization failed: {e}")
            print(f"❌ Initialization error: {e}")
            return False

    def create_fallback_enhancement(self, original_prompt):

        return f"...[same as before]..."

    def generate_website(self, user_prompt, enhance_prompt=True):
        try:
            print()
            print("=" * 60)
            print("🚀 Starting generation workflow...")
            print(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")
            self.start_time = time.time()

            if enhance_prompt and self.prompt_enhancer:
                print("📈 Step 1: Enhancing your prompt with AI...")
                try:
                    enhanced_prompt = self.prompt_enhancer.enhance_prompt(user_prompt)
                    final_prompt = enhanced_prompt
                except Exception as e:
                    print(f"⚠️ Enhancement error: {e}")
                    print("🔄 Using original prompt")
                    final_prompt = user_prompt
            else:
                print("📈 Step 1: Using original prompt directly")
                final_prompt = user_prompt
                print("✅ Original prompt ready!")

            print("🤖 Step 2: Getting response from Perplexity Pro...")
            try:
                response = self.code_generator.generate_code(final_prompt)
                if not response:
                    print("❌ Failed to collect response")
                    return False

                print("🏗️ Step 3: Creating project folders/files from LLM response (no intermediate file)...")
                project_path = self.project_creator.build_project_from_llm_response(response)
                if not project_path:
                    print("❌ Project creation from LLM response failed.")
                    return False
                self._show_success_message(project_path)
                self.projects_created += 1
                return True
            except Exception as e:
                print(f"❌ Response collection or project build error: {e}")
                return False
        except Exception as e:
            if self.logger:
                self.logger.error(f"Website generation failed: {e}")
            print(f"❌ Generation error: {e}")
            return False

    def _show_success_message(self, project_path):
        print()
        print("=" * 60)
        print("🎉 WEBSITE GENERATION COMPLETED!")
        print("=" * 60)
        print(f"✅ Your website has been created successfully")
        print(f"📁 Location: {project_path}")
        print()
        print("🚀 Next Steps:")
        print(f"   1. cd \"{project_path}\"")
        print("   2. npm install")
        print("   3. npm run dev")
        print()
        print("🌐 Your website will open at http://localhost:3000")

    def _show_failure_message(self):
        print()
        print("=" * 60)
        print("😞 WEBSITE GENERATION FAILED")
        print("=" * 60)
        print("❌ Something went wrong during the process")
        print("📋 Please check that all required files are in place")

    def _show_statistics(self):
        if self.start_time:
            duration = time.time() - self.start_time
            minutes, seconds = divmod(duration, 60)
            duration_str = f"{int(minutes):02d}:{seconds:06.3f}"
            print("📊 Session Statistics:")
            print(f"   • Duration: {duration_str}")
            print(f"   • Projects Created: {self.projects_created}")

    def cleanup(self):
        try:
            if self.brave_controller:
                self.brave_controller.cleanup()
                print("🧹 Cleaned up browser resources")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Cleanup error: {e}")

    def run(self):
        try:
            self.print_banner()
            user_prompt, enhance_choice = self.get_user_input()
            if not user_prompt:
                return
            if not self.initialize_components():
                print("❌ Failed to initialize components")
                print("💡 Please ensure all files in src/core/ directory exist")
                return
            success = self.generate_website(user_prompt, enhance_choice)
            if not success:
                self._show_failure_message()
            self._show_statistics()
        except KeyboardInterrupt:
            print("\n🛑 Process interrupted by user")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Application error: {e}")
            print(f"💥 Unexpected error: {e}")
        finally:
            self.cleanup()
            print("👋 Thanks for using AI Website Generator!")

def main():
    try:
        generator = AIWebsiteGenerator()
        generator.run()
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        print("❌ Please check your setup and try again")
        sys.exit(1)

if __name__ == "__main__":
    main()
