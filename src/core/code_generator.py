"""
Code Generator using Perplexity Pro
FINAL VERSION - Handles contenteditable inputs properly and saves complete response
"""

import time
import os
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, WebDriverException
import re

class CodeGenerator:
    def __init__(self, brave_controller, config, logger):
        self.brave = brave_controller
        self.config = config
        self.logger = logger
        self.perplexity_url = config['urls']['perplexity']

    def generate_code(self, user_prompt):
        """Generate code and save complete response to file - BULLETPROOF VERSION"""
        try:
            print("  🌐 Opening Perplexity Pro...")
            
            if not self.brave.open_new_tab(self.perplexity_url):
                return None
            
            print("  ⏳ Waiting for page to fully load...")
            time.sleep(8)
            
            # Check login status
            is_logged_in, is_pro = self._comprehensive_login_check()
            if is_logged_in and is_pro:
                print("  🎉 Perplexity Pro confirmed and ready!")
            elif is_logged_in:
                print("  ✅ Logged in to Perplexity")
            else:
                print("  ⚠️ Login status unclear - proceeding anyway")
            
            # Create the COMPLETE combined prompt - NO SEPARATION
            final_prompt = self._create_complete_unified_prompt(user_prompt)
            
            # Send the UNIFIED prompt and get response
            generated_response = self._send_unified_prompt_and_capture(final_prompt)
            
            if generated_response:
                print("  🎉 Response collected and saved successfully!")
                print(f"  📏 Collected {len(generated_response)} characters")
                return generated_response
            else:
                print("  ❌ Failed to collect response")
                return None
                
        except Exception as e:
            self.logger.error(f"Code generation failed: {e}")
            print(f"  ❌ Generation error: {e}")
            return None

    def _create_complete_unified_prompt(self, user_prompt):
        """Create ONE unified prompt - user request + instructions seamlessly combined"""
        
        # Make the instructions flow NATURALLY from the user prompt
        unified_prompt = f"{user_prompt.strip()} with different components use tailwind css + react to do. Provide the code for the following details above. Directly give the code. Give advanced code, no simple code. Give the code of components with special formatting. If you are providing the code of components, then make sure before the start of the code in the comments on the very top, write the name of the component and the folder and the file path. Example format: // Component: Header // File: src/components/Header/Header.jsx [component code here] // Component: Hero // File: src/components/Hero/Hero.jsx [component code here] , Kindly Mention the packages in the for of npm i and all the dependency required and also mention the api keys which are required on the top of the response in case of backend only. "
        
        print(f"  🔧 Created unified prompt: {len(unified_prompt)} characters")
        print(f"  📝 Preview: {unified_prompt[:100]}...")
        return unified_prompt

    def _send_unified_prompt_and_capture(self, unified_prompt):
        """Send the unified prompt and capture complete response"""
        max_attempts = 3
        
        for attempt in range(max_attempts):
            try:
                print(f"  🔄 Attempt {attempt + 1}/{max_attempts}")
                
                # Find input
                input_element = self._find_input_bulletproof()
                if not input_element:
                    print(f"  ❌ Could not find input field on attempt {attempt + 1}")
                    if attempt < max_attempts - 1:
                        time.sleep(5)
                        continue
                    return None
                
                # Send the UNIFIED prompt
                success = self._send_prompt_bulletproof(input_element, unified_prompt)
                if not success:
                    print(f"  ❌ Failed to send unified prompt on attempt {attempt + 1}")
                    if attempt < max_attempts - 1:
                        time.sleep(5)
                        continue
                    return None
                
                # Capture complete response
                response = self._capture_complete_response()
                if response:
                    return response
                
                if attempt < max_attempts - 1:
                    print(f"  🔄 No response received, retrying...")
                    time.sleep(10)
                    
            except Exception as e:
                print(f"  ⚠️ Attempt {attempt + 1} failed: {e}")
                if attempt < max_attempts - 1:
                    time.sleep(5)
                    continue
        
        return None

    def _find_input_bulletproof(self):
        """Bulletproof input finding"""
        for retry in range(5):
            try:
                print(f"    🔍 Looking for input field (attempt {retry + 1}/5)")
                
                WebDriverWait(self.brave.driver, 15).until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
                time.sleep(3)
                
                selectors = [
                    "div[contenteditable='true'][role='textbox']",  # Perplexity's main input
                    "textarea[placeholder*='Ask anything']",
                    "textarea[placeholder*='Ask']",
                    "div[contenteditable='true']",
                    "[contenteditable='true']",
                    "textarea",
                    "[role='textbox']"
                ]
                
                for selector in selectors:
                    try:
                        elements = self.brave.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            if (element.is_displayed() and element.is_enabled() and
                                element.size['height'] > 10 and element.size['width'] > 50):
                                
                                # Test if we can interact with it
                                try:
                                    self.brave.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                    time.sleep(1)
                                    element.click()
                                    time.sleep(0.5)
                                    print(f"    ✅ Found working input: {selector}")
                                    return element
                                except:
                                    continue
                    except:
                        continue
                
                if retry < 4:
                    print(f"    ⏳ No input found, waiting...")
                    time.sleep(4)
                
            except Exception as e:
                print(f"    ⚠️ Search error: {e}")
                time.sleep(3)
        
        print("    ❌ Could not find input field")
        return None

    def _send_prompt_bulletproof(self, element, prompt):
        """Bulletproof prompt sending - tries multiple methods"""
        
        methods = [
            ("ContentEditable JavaScript", self._send_contenteditable_js),
            ("Send Keys", self._send_with_keys),
            ("Actions Chain", self._send_with_actions)
        ]
        
        for method_name, method_func in methods:
            try:
                print(f"    🚀 Trying {method_name}...")
                
                # Ensure element is ready
                try:
                    element.click()
                    time.sleep(0.5)
                except:
                    pass
                
                if method_func(element, prompt):
                    print(f"    ✅ {method_name} SUCCESS!")
                    return True
                    
            except Exception as e:
                print(f"    ⚠️ {method_name} failed: {e}")
                continue
        
        return False

    def _send_contenteditable_js(self, element, prompt):
        """Method 1: Contenteditable JavaScript - FIXED FOR PERPLEXITY"""
        try:
            # Clear and focus first
            self.brave.driver.execute_script("arguments[0].focus();", element)
            time.sleep(0.2)
            
            # Handle contenteditable properly with innerText
            contenteditable_script = """
            var element = arguments[0];
            var text = arguments[1];
            
            // Clear first
            if (element.tagName === "TEXTAREA" || element.tagName === "INPUT") {
                element.value = '';
                element.value = text;
            } else {
                // For contenteditable (Perplexity uses this)
                element.innerText = '';
                element.innerHTML = '';
                element.innerText = text;
            }
            
            // Trigger all React events
            element.dispatchEvent(new Event('focus', {bubbles: true}));
            element.dispatchEvent(new Event('input', {bubbles: true}));
            element.dispatchEvent(new Event('change', {bubbles: true}));
            
            // Return what was actually set
            return element.tagName === "TEXTAREA" || element.tagName === "INPUT" ? element.value : element.innerText;
            """
            
            result_content = self.brave.driver.execute_script(contenteditable_script, element, prompt)
            
            if result_content and len(result_content) >= len(prompt) * 0.8:
                print(f"    🎯 ContentEditable JS set {len(result_content)} chars!")
                
                # Wait a moment for React to process
                time.sleep(0.5)
                
                # Submit
                element.send_keys(Keys.RETURN)
                time.sleep(2)
                return True
            else:
                print(f"    ❌ ContentEditable JS failed - got {len(result_content or '')} chars")
                return False
                
        except Exception as e:
            print(f"    ❌ ContentEditable JS failed: {e}")
            return False

    def _send_with_keys(self, element, prompt):
        """Method 2: Send Keys - reliable for multiline"""
        try:
            element.click()
            time.sleep(0.5)
            
            # Clear the field (works for both textarea and contenteditable)
            try:
                element.clear()
            except:
                # For contenteditable, clear manually
                self.brave.driver.execute_script("arguments[0].innerText = '';", element)
            
            time.sleep(0.5)
            
            # Send the complete prompt using send_keys (handles newlines perfectly)
            element.send_keys(prompt)
            time.sleep(1)
            
            element.send_keys(Keys.RETURN)
            time.sleep(2)
            return True
            
        except Exception as e:
            print(f"    ❌ Send keys method failed: {e}")
            return False

    def _send_with_actions(self, element, prompt):
        """Method 3: Action chains"""
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            
            actions = ActionChains(self.brave.driver)
            actions.click(element)
            actions.pause(0.5)
            actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL)
            actions.send_keys(Keys.DELETE)
            actions.pause(0.5)
            actions.send_keys(prompt)
            actions.send_keys(Keys.RETURN)
            actions.perform()
            
            time.sleep(2)
            return True
            
        except Exception as e:
            print(f"    ❌ Actions method failed: {e}")
            return False

    def _capture_complete_response(self):
        """ENHANCED: Wait until Perplexity completely finishes responding before saving"""
        try:
            print("  ⏳ Waiting for Perplexity to completely finish responding...")
            
            # Enhanced parameters for better stability detection
            max_wait = 600  # 10 minutes total wait time
            check_interval = 3  # Check every 3 seconds
            start_time = time.time()
            
            last_content = ""
            last_length = 0
            stable_count = 0
            required_stable_checks = 12  # Must be stable for 12 consecutive checks (36 seconds)
            min_content_length = 5000  # Minimum content length to consider complete
            
            print(f"  📊 Stability requirements: {required_stable_checks} consecutive stable checks")
            
            while time.time() - start_time < max_wait:
                try:
                    # Get ALL page content with enhanced extraction
                    current_content = self._get_all_page_content()
                    current_length = len(current_content) if current_content else 0
                    
                    if current_content and current_length > min_content_length:
                        # Check if content has stabilized (no changes)
                        if current_content == last_content and current_length == last_length:
                            stable_count += 1
                            print(f"  📊 Content stable: {stable_count}/{required_stable_checks} ({current_length:,} chars)")
                            
                            # Additional check: make sure we're not still generating
                            if stable_count >= 6:  # After some stability, double-check
                                if self._is_still_generating():
                                    print("  🔄 Still actively generating, resetting stability counter")
                                    stable_count = 0
                                    
                            # If we've been stable long enough, we're done!
                            if stable_count >= required_stable_checks:
                                print(f"  ✅ Content fully stabilized at {current_length:,} characters")
                                print(f"  ⏰ Total wait time: {time.time() - start_time:.1f} seconds")
                                
                                # Save the complete response
                                saved_path = self._save_complete_response(current_content)
                                if saved_path:
                                    print(f"  💾 Complete response saved to: {saved_path}")
                                
                                return current_content
                        else:
                            # Content changed, reset counter
                            if current_length > last_length:
                                growth = current_length - last_length
                                print(f"  📈 Content growing: {current_length:,} chars (+{growth:,})")
                            elif current_length < last_length:
                                print(f"  📉 Content changed: {current_length:,} chars")
                                
                            stable_count = 0
                            last_content = current_content
                            last_length = current_length
                    else:
                        print(f"  ⏳ Waiting for substantial content... ({current_length:,} chars)")
                        stable_count = 0
                    
                    # Check if still loading/generating
                    if self._is_still_generating():
                        print("  🔄 Still generating content...")
                    
                    time.sleep(check_interval)
                    
                except Exception as e:
                    print(f"  ⚠️ Content monitoring error: {e}")
                    time.sleep(check_interval)
            
            print(f"  ⏰ Maximum wait time reached ({max_wait} seconds)")
            
            # Save whatever we have as final attempt
            if current_content and len(current_content) > 1000:
                saved_path = self._save_complete_response(current_content)
                print(f"  💾 Final response saved: {saved_path}")
                return current_content
            
            print("  ❌ No substantial content captured")
            return None
            
        except Exception as e:
            self.logger.error(f"Response capture error: {e}")
            print(f"  ❌ Response capture failed: {e}")
            return None

    def _get_all_page_content(self):
        """Enhanced: Get ALL content from the page with multiple extraction methods"""
        try:
            # Method 1: Get all visible text from body
            body_text = self.brave.driver.find_element(By.TAG_NAME, "body").text
            
            # Method 2: Get specific Perplexity response areas
            response_areas = []
            perplexity_selectors = [
                # Perplexity-specific selectors
                "[data-testid*='copilot-answer']",
                "[data-testid*='answer']",
                "[data-testid*='response']",
                "[data-testid*='result']",
                ".copilot-answer",
                ".answer-content", 
                ".response-content",
                "[role='article']",
                ".prose",
                "main [class*='answer']",
                "main [class*='response']",
                # Generic content areas
                "main",
                ".answer-container"
            ]
            
            for selector in perplexity_selectors:
                try:
                    elements = self.brave.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        text = elem.text.strip()
                        if text and len(text) > 100:
                            response_areas.append(f"=== {selector} ===\n{text}")
                except:
                    continue
            
            # Method 3: Try to get innerHTML for better content extraction
            try:
                body_html = self.brave.driver.find_element(By.TAG_NAME, "body").get_attribute("innerHTML")
                # Simple HTML tag removal for additional content
                import re
                clean_html_text = re.sub('<[^<]+?>', '', body_html)
                if len(clean_html_text) > len(body_text):
                    body_text += f"\n\n=== HTML EXTRACTED CONTENT ===\n{clean_html_text[:5000]}"
            except:
                pass
            
            # Combine all content sources
            all_content = body_text
            if response_areas:
                all_content += f"\n\n{'='*60}\nEXTRACTED PERPLEXITY RESPONSES\n{'='*60}\n"
                all_content += "\n\n".join(response_areas)
            
            return all_content
            
        except Exception as e:
            print(f"  ⚠️ Error getting enhanced page content: {e}")
            return None

    def _save_complete_response(self, content):
        """Save complete response to timestamped file with enhanced metadata"""
        try:
            # Create directory
            responses_dir = os.path.expanduser("~/Desktop/Perplexity_Responses")
            os.makedirs(responses_dir, exist_ok=True)
            
            # Create filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"perplexity_response_{timestamp}.txt"
            filepath = os.path.join(responses_dir, filename)
            
            # Save with enhanced metadata
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("="*70 + "\n")
                f.write("PERPLEXITY COMPLETE RESPONSE CAPTURE - ENHANCED\n")
                f.write("="*70 + "\n")
                f.write(f"Capture Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Content Length: {len(content):,} characters\n")
                f.write(f"Content Lines: {len(content.splitlines()):,} lines\n")
                f.write(f"Word Count (approx): {len(content.split()):,} words\n")
                f.write("="*70 + "\n\n")
                f.write(content)
            
            return filepath
            
        except Exception as e:
            print(f"  ❌ Save error: {e}")
            return None

    def _is_still_generating(self):
        """Enhanced: Check if Perplexity is still actively generating content"""
        try:
            # Check for loading/generating UI indicators
            loading_indicators = [
                "[data-testid*='loading']",
                "[data-testid*='generating']",
                "[data-testid*='thinking']",
                ".loading",
                ".spinner", 
                ".generating",
                ".thinking",
                "[aria-label*='loading' i]",
                "[aria-label*='generating' i]",
                "[class*='loading']",
                "[class*='spinner']",
                "[class*='generating']"
            ]
            
            for selector in loading_indicators:
                try:
                    elements = self.brave.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        # Check if any are actually visible
                        for elem in elements:
                            if elem.is_displayed():
                                return True
                except:
                    continue
            
            # Check page text for generation indicators
            try:
                page_text = self.brave.driver.find_element(By.TAG_NAME, "body").text.lower()
                generation_phrases = [
                    "generating",
                    "thinking", 
                    "processing",
                    "searching",
                    "analyzing",
                    "loading",
                    "please wait"
                ]
                
                for phrase in generation_phrases:
                    if phrase in page_text:
                        return True
            except:
                pass
            
            return False
            
        except Exception:
            return False

    def _comprehensive_login_check(self):
        """Check login status"""
        try:
            is_logged_in = False
            is_pro = False
            
            # Check UI indicators
            user_selectors = [
                "[data-testid*='user']",
                "[data-testid*='profile']", 
                ".user-menu",
                ".profile-menu",
                ".user-avatar",
                "button[aria-label*='user' i]",
                ".logged-in",
                ".authenticated"
            ]
            
            for selector in user_selectors:
                try:
                    element = self.brave.find_element_safe(selector, timeout=2)
                    if element:
                        is_logged_in = True
                        print("  ✅ User interface indicates logged in")
                        break
                except:
                    continue
            
            # Check page text
            try:
                page_text = self.brave.driver.find_element(By.TAG_NAME, "body").text.lower()
                
                if any(phrase in page_text for phrase in ["sign out", "logout", "my account"]):
                    is_logged_in = True
                    print("  ✅ Page text indicates logged in")
                
                if any(phrase in page_text for phrase in ["pro search", "unlimited", "pro plan", "premium"]):
                    is_pro = True
                    print("  🎯 Pro features detected")
                
                if not any(phrase in page_text for phrase in ["searches remaining", "search limit"]):
                    is_pro = True
                    print("  🎯 No search limits - likely Pro")
                    
            except Exception as e:
                print(f"  ⚠️ Page check failed: {e}")
            
            return is_logged_in, is_pro
            
        except Exception as e:
            print(f"  ⚠️ Login check failed: {e}")
            return False, False