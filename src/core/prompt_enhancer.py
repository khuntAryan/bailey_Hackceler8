"""
Prompt Enhancer using FlexOS Prompt Enhancer AI
FIXED VERSION - No fallback to pre-built prompts
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

class PromptEnhancer:
    def __init__(self, brave_controller, config, logger):
        self.brave = brave_controller
        self.config = config
        self.logger = logger
        self.flexos_url = config.get('urls', {}).get('flexos', 'https://www.flexos.work/design/prompt')

    def enhance_prompt(self, original_prompt):
        """Enhanced prompt processing - NO fallback to pre-built prompts"""
        try:
            print("  🌐 Opening FlexOS Prompt Enhancer...")
            
            # Open FlexOS in new tab
            if not self.brave.open_new_tab(self.flexos_url):
                print("  ❌ FlexOS failed - using original prompt directly")
                return original_prompt  # Return original, NOT fallback
            
            # Wait for page to load
            time.sleep(6)
            
            # Process enhancement
            enhanced_prompt = self._enhanced_extraction_flow(original_prompt)
            
            if enhanced_prompt and len(enhanced_prompt) > len(original_prompt):
                print("  ✨ Prompt enhanced successfully with FlexOS!")
                return enhanced_prompt
            else:
                print("  ⚠️ FlexOS enhancement failed, using original prompt")
                return original_prompt  # Return original, NOT fallback
                
        except Exception as e:
            print(f"  ❌ Enhancement error: {e}")
            return original_prompt  # Return original, NOT fallback

    def _enhanced_extraction_flow(self, original_prompt):
        """Process FlexOS enhancement"""
        try:
            # Find and fill input
            input_element = self._find_flexos_input()
            if not input_element:
                print("  ❌ Could not find FlexOS input field")
                return None
            
            # Enter the prompt
            if not self._enter_prompt_into_flexos(input_element, original_prompt):
                print("  ❌ Could not enter prompt into FlexOS")
                return None
            
            # Wait for processing and extract result
            enhanced_result = self._wait_and_extract_with_copy_button()
            if enhanced_result:
                print(f"  ✅ Successfully got enhanced prompt from FlexOS!")
                return enhanced_result
            
            return None
            
        except Exception as e:
            self.logger.error(f"FlexOS processing error: {e}")
            return None

    def _find_flexos_input(self):
        """Find FlexOS input textarea"""
        try:
            print("  🔍 Looking for FlexOS input field...")
            
            WebDriverWait(self.brave.driver, 25).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            time.sleep(5)
            
            flexos_input_selectors = [
                "textarea[placeholder='Type your prompt here...']",
                "textarea[placeholder*='Type your prompt here']",
                "textarea[placeholder*='prompt here']",
                "textarea[placeholder*='Type']",
                "textarea[placeholder*='prompt']",
                "textarea:not([style*='display: none']):not([disabled])",
                "textarea",
                "div[contenteditable='true']",
                "[contenteditable='true']"
            ]
            
            for i, selector in enumerate(flexos_input_selectors, 1):
                try:
                    print(f"    📋 Trying FlexOS selector {i}/{len(flexos_input_selectors)}: {selector}")
                    
                    elements = self.brave.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        if self._is_flexos_input_valid(element):
                            print(f"    ✅ Found FlexOS input field!")
                            return element
                            
                except Exception as e:
                    print(f"    ⚠️ Selector failed: {e}")
                    continue
            
            print("  ❌ Could not find FlexOS input field")
            return None
            
        except Exception as e:
            print(f"  ❌ FlexOS input detection failed: {e}")
            return None

    def _is_flexos_input_valid(self, element):
        """Validate FlexOS input element"""
        try:
            if not (element.is_displayed() and element.is_enabled()):
                return False
            
            size = element.size
            if size['height'] < 30 or size['width'] < 200:
                return False
            
            try:
                self.brave.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                time.sleep(1)
                element.click()
                time.sleep(1)
                return True
            except Exception:
                return False
                
        except Exception:
            return False

    def _enter_prompt_into_flexos(self, element, prompt):
        """Enter prompt into FlexOS safely"""
        try:
            print("  📝 Entering prompt into FlexOS...")
            
            try:
                element.clear()
                time.sleep(1)
            except:
                try:
                    element.send_keys(Keys.CONTROL + "a")
                    element.send_keys(Keys.DELETE)
                    time.sleep(1)
                except:
                    pass
            
            # Enter prompt in chunks
            chunk_size = 80
            for i in range(0, len(prompt), chunk_size):
                chunk = prompt[i:i+chunk_size]
                try:
                    element.send_keys(chunk)
                    time.sleep(0.15)
                except StaleElementReferenceException:
                    element = self.brave.driver.switch_to.active_element
                    element.send_keys(chunk)
                    time.sleep(0.15)
            
            time.sleep(3)
            print("  ✅ Prompt entered into FlexOS successfully")
            return True
            
        except Exception as e:
            print(f"  ❌ Error entering prompt into FlexOS: {e}")
            return False

    def _wait_and_extract_with_copy_button(self):
        """Wait for processing and extract via copy button"""
        try:
            print("  ⏳ Waiting for FlexOS to process prompt...")
            
            max_wait = 90
            check_interval = 3
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                try:
                    # Look for enhanced text directly on page
                    direct_result = self._extract_enhanced_text_from_page()
                    if direct_result:
                        print(f"  ✅ Found enhanced text directly on page!")
                        return direct_result
                    
                    # Check if still processing
                    if self._is_flexos_processing():
                        print("  🔄 FlexOS still processing...")
                    else:
                        # Check for any substantial content changes
                        page_content = self._check_for_content_changes()
                        if page_content:
                            print(f"  ✅ Found content changes on page!")
                            return page_content
                    
                    time.sleep(check_interval)
                    
                except Exception as e:
                    print(f"  ⚠️ FlexOS extraction attempt failed: {e}")
                    time.sleep(check_interval)
            
            print(f"  ⏰ FlexOS timeout after {max_wait} seconds")
            return None
            
        except Exception as e:
            print(f"  ❌ FlexOS result extraction error: {e}")
            return None

    def _extract_enhanced_text_from_page(self):
        """Extract enhanced text directly from page"""
        try:
            content_selectors = [
                "div.enhanced-prompt",
                "div.result-text",
                "div.output-text", 
                "div.generated-content",
                "pre",
                "code",
                "textarea[readonly]",
                "div[class*='enhanced']",
                "div[class*='result']"
            ]
            
            for selector in content_selectors:
                try:
                    elements = self.brave.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text_content = element.text.strip()
                        
                        if (text_content and 
                            len(text_content) > 250 and
                            self._looks_like_enhanced_content(text_content) and
                            not self._is_flexos_navigation(text_content)):
                            
                            return text_content
                            
                except Exception:
                    continue
            
            return None
            
        except Exception as e:
            return None

    def _check_for_content_changes(self):
        """Check for any substantial content changes on the page"""
        try:
            page_text = self.brave.driver.find_element(By.TAG_NAME, "body").text
            
            if len(page_text) > 3000:
                lines = [line.strip() for line in page_text.split('\n') if len(line.strip()) > 100]
                
                for line in lines:
                    if (self._looks_like_enhanced_content(line) and 
                        not self._is_flexos_navigation(line)):
                        
                        line_index = lines.index(line)
                        start_index = max(0, line_index - 1)
                        end_index = min(len(lines), line_index + 3)
                        
                        context_lines = lines[start_index:end_index]
                        combined_content = '\n'.join(context_lines)
                        
                        if len(combined_content) > 400:
                            return combined_content
                            
        except Exception as e:
            pass
        
        return None

    def _is_flexos_processing(self):
        """Check if FlexOS is still processing"""
        processing_indicators = [
            ".loading", ".processing", ".spinner",
            "[data-testid*='loading']", "[aria-label*='loading' i]",
            ".progress", ".generating"
        ]
        
        for selector in processing_indicators:
            try:
                if self.brave.driver.find_elements(By.CSS_SELECTOR, selector):
                    return True
            except:
                continue
        
        return False

    def _is_flexos_navigation(self, text):
        """Check if text is FlexOS navigation content"""
        nav_keywords = [
            'flexos', 'productivity', 'craft perfect ai art prompts',
            'prompt enhancer ai', 'chatgpt for designers', 'courses',
            'newsletter', 'subscribe', 'copy link', 'share on linkedin',
            'share on twitter', 'share on facebook', 'midjourney',
            'ideogram', 'dall-e', 'your guides to a better future',
            'type your prompt here'
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in nav_keywords)

    def _looks_like_enhanced_content(self, text):
        """Check if text looks like enhanced prompt content"""
        enhancement_indicators = [
            'create', 'develop', 'build', 'design', 'implement',
            'website', 'application', 'frontend', 'backend', 'system',
            'features', 'functionality', 'requirements', 'specifications',
            'components', 'structure', 'architecture', 'framework',
            'modern', 'professional', 'responsive', 'interactive',
            'detailed', 'comprehensive', 'technical', 'advanced'
        ]
        
        text_lower = text.lower()
        matches = sum(1 for indicator in enhancement_indicators if indicator in text_lower)
        
        return matches >= 4 and len(text) > 200
