import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import cv2
import pytesseract
import numpy as np
from PIL import Image, ImageTk
from deep_translator import GoogleTranslator
from gtts import gTTS
import os
import threading

# ========================================
# CONFIGURATION
# ========================================
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class SignboardTranslator:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Signboard Translator for Tourists")
        self.root.geometry("1000x750")
        self.root.configure(bg='#f5f5f5')
        
        self.current_image_path = None
        self.extracted_text = ""
        self.translated_text = ""
        
        self.create_gui()
        self.test_tesseract_on_startup()
    
    def test_tesseract_on_startup(self):
        """Test Tesseract when app starts"""
        try:
            version = pytesseract.get_tesseract_version()
            self.update_status(f"✅ Tesseract {version} ready", 'success')
        except Exception as e:
            self.update_status(f"❌ Tesseract Error: {str(e)}", 'error')
            messagebox.showerror(
                "Tesseract Not Found",
                f"Error: {str(e)}\n\n"
                "Please check:\n"
                "1. Tesseract is installed\n"
                "2. Path in code is correct"
            )
    
    def create_gui(self):
        # ========================================
        # HEADER
        # ========================================
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title = tk.Label(
            header_frame,
            text="🌍 AI Signboard Translator",
            font=("Arial", 24, "bold"),
            bg='#2c3e50',
            fg='white'
        )
        title.pack(pady=20)
        
        # ========================================
        # MAIN CONTENT FRAME
        # ========================================
        content_frame = tk.Frame(self.root, bg='#f5f5f5')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Upload Button
        self.upload_btn = tk.Button(
            content_frame,
            text="📁 Upload Signboard Image",
            command=self.upload_image,
            font=("Arial", 14, "bold"),
            bg='#27ae60',
            fg='white',
            padx=30,
            pady=15,
            cursor='hand2',
            relief=tk.RAISED,
            borderwidth=3
        )
        self.upload_btn.pack(pady=15)
        
        # Language Selection Frame
        lang_frame = tk.Frame(content_frame, bg='#f5f5f5')
        lang_frame.pack(pady=10)
        
        tk.Label(
            lang_frame,
            text="🌐 Translate to:",
            font=("Arial", 12, "bold"),
            bg='#f5f5f5'
        ).pack(side=tk.LEFT, padx=10)
        
        self.target_lang = ttk.Combobox(
            lang_frame,
            values=[
                'English', 'Hindi', 'Tamil', 'Telugu', 
                'Marathi', 'Bengali', 'Kannada', 'Malayalam',
                'Spanish', 'French', 'German', 'Chinese'
            ],
            state='readonly',
            width=20,
            font=("Arial", 11)
        )
        self.target_lang.set('English')
        self.target_lang.pack(side=tk.LEFT)
        
        # Progress Bar
        self.progress = ttk.Progressbar(
            content_frame,
            length=500,
            mode='indeterminate'
        )
        self.progress.pack(pady=15)
        
        # ========================================
        # TEXT DISPLAY AREA
        # ========================================
        text_container = tk.Frame(content_frame, bg='#f5f5f5')
        text_container.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Left Column - Original Text
        left_frame = tk.Frame(text_container, bg='#f5f5f5')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(
            left_frame,
            text="📝 Extracted Text (Original)",
            font=("Arial", 13, "bold"),
            bg='#f5f5f5',
            fg='#2c3e50'
        ).pack(anchor='w', pady=(0, 5))
        
        original_scroll_frame = tk.Frame(left_frame)
        original_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        original_scrollbar = tk.Scrollbar(original_scroll_frame)
        original_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.original_text = tk.Text(
            original_scroll_frame,
            height=12,
            font=("Arial", 11),
            wrap=tk.WORD,
            relief=tk.SOLID,
            borderwidth=2,
            yscrollcommand=original_scrollbar.set,
            bg='#ffffff'
        )
        self.original_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        original_scrollbar.config(command=self.original_text.yview)
        
        # Right Column - Translated Text
        right_frame = tk.Frame(text_container, bg='#f5f5f5')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        tk.Label(
            right_frame,
            text="🌐 Translated Text",
            font=("Arial", 13, "bold"),
            bg='#f5f5f5',
            fg='#2c3e50'
        ).pack(anchor='w', pady=(0, 5))
        
        translation_scroll_frame = tk.Frame(right_frame)
        translation_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        translation_scrollbar = tk.Scrollbar(translation_scroll_frame)
        translation_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.translation_text = tk.Text(
            translation_scroll_frame,
            height=12,
            font=("Arial", 11),
            wrap=tk.WORD,
            relief=tk.SOLID,
            borderwidth=2,
            yscrollcommand=translation_scrollbar.set,
            bg='#ffffff'
        )
        self.translation_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        translation_scrollbar.config(command=self.translation_text.yview)
        
        # ========================================
        # AUDIO BUTTON
        # ========================================
        self.audio_btn = tk.Button(
            content_frame,
            text="🔊 Play Audio Translation",
            command=self.play_audio,
            font=("Arial", 12, "bold"),
            bg='#3498db',
            fg='white',
            padx=25,
            pady=12,
            state=tk.DISABLED,
            cursor='hand2',
            relief=tk.RAISED,
            borderwidth=2
        )
        self.audio_btn.pack(pady=15)
        
        # ========================================
        # STATUS BAR
        # ========================================
        status_frame = tk.Frame(self.root, bg='#34495e', height=40)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            status_frame,
            text="Checking Tesseract installation...",
            font=("Arial", 10),
            bg='#34495e',
            fg='white',
            anchor='w'
        )
        self.status_label.pack(side=tk.LEFT, padx=20, pady=10)
    
    def update_status(self, message, status_type='info'):
        """Update status bar with color coding"""
        colors = {
            'info': '#3498db',
            'success': '#27ae60',
            'warning': '#f39c12',
            'error': '#e74c3c'
        }
        self.status_label.config(text=message, fg=colors.get(status_type, 'white'))
    
    def preprocess_image(self, image_path):
        """Enhanced image preprocessing for better OCR"""
        img = cv2.imread(image_path)
        
        if img is None:
            raise ValueError("Cannot read image file")
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Resize image (3x larger for better recognition)
        gray = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        
        # Noise removal
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        
        # Adaptive thresholding
        binary = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Morphological operations to clean up
        kernel = np.ones((2, 2), np.uint8)
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)
        
        # Save debug image
        cv2.imwrite('debug_preprocessed.png', cleaned)
        
        return cleaned
    
    def extract_text(self, processed_image):
        """Extract text with multiple OCR configurations"""
        configs = [
            '--oem 3 --psm 3',   # Fully automatic
            '--oem 3 --psm 6',   # Single uniform block
            '--oem 3 --psm 11',  # Sparse text
            '--oem 3 --psm 12',  # Sparse text with OSD
        ]
        
        best_text = ""
        
        for config in configs:
            try:
                text = pytesseract.image_to_string(processed_image, config=config)
                if len(text.strip()) > len(best_text):
                    best_text = text.strip()
            except:
                continue
        
        return best_text
    
    def translate(self, text, target_lang):
        """Translate text to target language using deep-translator"""
        lang_codes = {
            'English': 'en', 'Hindi': 'hi', 'Tamil': 'ta',
            'Telugu': 'te', 'Marathi': 'mr', 'Bengali': 'bn',
            'Kannada': 'kn', 'Malayalam': 'ml',
            'Spanish': 'es', 'French': 'fr', 'German': 'de', 'Chinese': 'zh-CN'
        }
        
        code = lang_codes.get(target_lang, 'en')
        
        try:
            translator = GoogleTranslator(source='auto', target=code)
            result = translator.translate(text)
            return result
        except Exception as e:
            error_msg = f"⚠️ Translation Error\n\n"
            error_msg += f"Error: {str(e)}\n\n"
            error_msg += "Possible causes:\n"
            error_msg += "• No internet connection\n"
            error_msg += "• Translation service unavailable\n"
            error_msg += "• Text too long\n\n"
            error_msg += f"Original text:\n{text}"
            return error_msg
    
    def upload_image(self):
        """Handle image upload and processing"""
        file_path = filedialog.askopenfilename(
            title="Select Signboard Image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.gif"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        self.current_image_path = file_path
        self.progress.start()
        self.update_status("⏳ Processing image...", 'info')
        self.root.update()
        
        try:
            # Clear previous results
            self.original_text.delete(1.0, tk.END)
            self.translation_text.delete(1.0, tk.END)
            self.audio_btn.config(state=tk.DISABLED)
            
            # Preprocess image
            self.update_status("→ Preprocessing image...", 'info')
            self.root.update()
            processed = self.preprocess_image(file_path)
            
            # Extract text
            self.update_status("→ Extracting text with OCR...", 'info')
            self.root.update()
            extracted = self.extract_text(processed)
            
            if not extracted or len(extracted) < 2:
                self.original_text.insert(tk.END, "⚠️ NO TEXT DETECTED\n\n")
                self.original_text.insert(tk.END, "Possible reasons:\n")
                self.original_text.insert(tk.END, "• Image quality too low\n")
                self.original_text.insert(tk.END, "• Text too small or blurry\n")
                self.original_text.insert(tk.END, "• Poor lighting or contrast\n")
                self.original_text.insert(tk.END, "• Handwritten or unusual font\n\n")
                self.original_text.insert(tk.END, "💡 Check 'debug_preprocessed.png' file\n")
                
                self.update_status("⚠️ No text detected in image", 'warning')
                messagebox.showwarning(
                    "No Text Found",
                    "Could not detect text in the image.\n\n"
                    "Tips:\n"
                    "• Use clearer image\n"
                    "• Ensure good lighting\n"
                    "• Check if text is large enough"
                )
                return
            
            self.extracted_text = extracted
            self.original_text.insert(tk.END, extracted)
            
            # Translate text
            self.update_status("→ Translating text...", 'info')
            self.root.update()
            
            translated = self.translate(extracted, self.target_lang.get())
            self.translated_text = translated
            self.translation_text.insert(tk.END, translated)
            
            # Enable audio button
            self.audio_btn.config(state=tk.NORMAL)
            
            # Success
            self.update_status(
                f"✅ Success! Extracted {len(extracted)} chars, translated to {self.target_lang.get()}",
                'success'
            )
            
            messagebox.showinfo(
                "Success!",
                f"✅ Text extracted and translated successfully!\n\n"
                f"Original: {len(extracted)} characters\n"
                f"Words: {len(extracted.split())} words"
            )
            
        except Exception as e:
            self.original_text.delete(1.0, tk.END)
            self.original_text.insert(tk.END, f"❌ ERROR:\n{str(e)}\n\n")
            self.original_text.insert(tk.END, "Troubleshooting:\n")
            self.original_text.insert(tk.END, "1. Check Tesseract installation\n")
            self.original_text.insert(tk.END, "2. Verify image file is valid\n")
            self.original_text.insert(tk.END, "3. Check internet connection for translation\n")
            
            self.update_status(f"❌ Error: {str(e)}", 'error')
            messagebox.showerror("Error", f"An error occurred:\n\n{str(e)}")
        
        finally:
            self.progress.stop()
    
    def play_audio(self):
        """Convert translated text to speech"""
        if not self.translated_text:
            return
        
        def generate_audio():
            try:
                self.update_status("🔊 Generating audio...", 'info')
                
                lang_codes = {
                    'English': 'en', 'Hindi': 'hi', 'Tamil': 'ta',
                    'Telugu': 'te', 'Marathi': 'mr', 'Bengali': 'bn',
                    'Kannada': 'kn', 'Malayalam': 'ml',
                    'Spanish': 'es', 'French': 'fr', 'German': 'de',
                    'Chinese': 'zh-cn'
                }
                
                code = lang_codes.get(self.target_lang.get(), 'en')
                tts = gTTS(text=self.translated_text, lang=code, slow=False)
                
                audio_file = "translation_audio.mp3"
                tts.save(audio_file)
                
                # Play audio
                os.system(f"start {audio_file}")
                
                self.update_status("✅ Audio playing...", 'success')
                
            except Exception as e:
                self.update_status(f"❌ Audio error: {str(e)}", 'error')
                messagebox.showerror(
                    "Audio Error",
                    f"Could not generate audio:\n\n{str(e)}\n\n"
                    "Check internet connection."
                )
        
        # Run in separate thread
        thread = threading.Thread(target=generate_audio)
        thread.daemon = True
        thread.start()

# ========================================
# RUN APPLICATION
# ========================================
if __name__ == "__main__":
    root = tk.Tk()
    app = SignboardTranslator(root)
    root.mainloop()
