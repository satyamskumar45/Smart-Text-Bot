"""
Advanced OCR Image Preprocessing
Improves OCR accuracy through image enhancement techniques.
"""

from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import numpy as np
import cv2
import io
from typing import Tuple, Optional


class OCRPreprocessor:
    """Advanced image preprocessing for better OCR results"""
    
    def __init__(self):
        self.default_config = {
            'resize_factor': 2.0,      # Upscale for better OCR
            'denoise_strength': 10,     # Noise reduction
            'sharpen_factor': 1.5,      # Sharpening
            'contrast_factor': 1.3,     # Contrast enhancement
            'brightness_factor': 1.1,   # Brightness adjustment
        }
    
    def preprocess(
        self,
        image: Image.Image,
        method: str = "auto"
    ) -> Image.Image:
        """
        Preprocess image for OCR.
        
        Args:
            image: PIL Image
            method: "auto", "standard", "aggressive", "light"
        
        Returns:
            Preprocessed PIL Image
        """
        if method == "auto":
            # Analyze image and choose best method
            method = self._detect_best_method(image)
        
        if method == "aggressive":
            return self._aggressive_preprocessing(image)
        elif method == "light":
            return self._light_preprocessing(image)
        else:  # standard
            return self._standard_preprocessing(image)
    
    def _detect_best_method(self, image: Image.Image) -> str:
        """Detect best preprocessing method based on image characteristics"""
        # Convert to numpy array
        img_array = np.array(image.convert('L'))
        
        # Calculate image statistics
        mean_brightness = np.mean(img_array)
        std_brightness = np.std(img_array)
        
        # Low contrast or very dark/bright images need aggressive processing
        if std_brightness < 40 or mean_brightness < 80 or mean_brightness > 200:
            return "aggressive"
        # Good quality images need light processing
        elif std_brightness > 60 and 100 < mean_brightness < 180:
            return "light"
        else:
            return "standard"
    
    def _standard_preprocessing(self, image: Image.Image) -> Image.Image:
        """Standard preprocessing pipeline"""
        # 1. Convert to grayscale
        image = image.convert('L')
        
        # 2. Resize (upscale for better OCR)
        width, height = image.size
        new_size = (int(width * 2), int(height * 2))
        image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # 3. Denoise
        image = image.filter(ImageFilter.MedianFilter(size=3))
        
        # 4. Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.3)
        
        # 5. Sharpen
        image = image.filter(ImageFilter.SHARPEN)
        
        # 6. Binarization (Otsu's method)
        image = self._adaptive_threshold(image)
        
        return image
    
    def _light_preprocessing(self, image: Image.Image) -> Image.Image:
        """Light preprocessing for good quality images"""
        # 1. Convert to grayscale
        image = image.convert('L')
        
        # 2. Slight upscale
        width, height = image.size
        new_size = (int(width * 1.5), int(height * 1.5))
        image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # 3. Light sharpening
        image = image.filter(ImageFilter.SHARPEN)
        
        # 4. Light contrast enhancement
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.1)
        
        return image
    
    def _aggressive_preprocessing(self, image: Image.Image) -> Image.Image:
        """Aggressive preprocessing for poor quality images"""
        # Convert to OpenCV format for advanced processing
        img_array = np.array(image.convert('L'))
        
        # 1. Upscale significantly
        img_array = cv2.resize(
            img_array,
            None,
            fx=2.5,
            fy=2.5,
            interpolation=cv2.INTER_CUBIC
        )
        
        # 2. Denoise aggressively
        img_array = cv2.fastNlMeansDenoising(img_array, None, 10, 7, 21)
        
        # 3. Enhance contrast with CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        img_array = clahe.apply(img_array)
        
        # 4. Morphological operations to clean up
        kernel = np.ones((2, 2), np.uint8)
        img_array = cv2.morphologyEx(img_array, cv2.MORPH_CLOSE, kernel)
        
        # 5. Adaptive thresholding
        img_array = cv2.adaptiveThreshold(
            img_array,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )
        
        # 6. Deskew if needed
        img_array = self._deskew(img_array)
        
        # Convert back to PIL
        return Image.fromarray(img_array)
    
    def _adaptive_threshold(self, image: Image.Image) -> Image.Image:
        """Apply adaptive thresholding for binarization"""
        img_array = np.array(image)
        
        # Adaptive threshold
        binary = cv2.adaptiveThreshold(
            img_array,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )
        
        return Image.fromarray(binary)
    
    def _deskew(self, img_array: np.ndarray) -> np.ndarray:
        """Deskew image to correct rotation"""
        # Calculate skew angle
        coords = np.column_stack(np.where(img_array > 0))
        if len(coords) == 0:
            return img_array
        
        angle = cv2.minAreaRect(coords)[-1]
        
        # Correct angle
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        
        # Only deskew if angle is significant
        if abs(angle) < 0.5:
            return img_array
        
        # Rotate image
        (h, w) = img_array.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            img_array,
            M,
            (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )
        
        return rotated
    
    def remove_borders(self, image: Image.Image) -> Image.Image:
        """Remove black borders from scanned documents"""
        img_array = np.array(image.convert('L'))
        
        # Find non-white regions
        _, binary = cv2.threshold(img_array, 200, 255, cv2.THRESH_BINARY_INV)
        
        # Find contours
        contours, _ = cv2.findContours(
            binary,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        if not contours:
            return image
        
        # Get bounding box of largest contour
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        
        # Crop image
        cropped = img_array[y:y+h, x:x+w]
        
        return Image.fromarray(cropped)
    
    def enhance_for_ocr(
        self,
        image_bytes: bytes,
        method: str = "auto"
    ) -> Tuple[Image.Image, Image.Image]:
        """
        Complete preprocessing pipeline.
        
        Args:
            image_bytes: Raw image bytes
            method: Preprocessing method
        
        Returns:
            Tuple of (original_image, preprocessed_image)
        """
        # Load image
        original = Image.open(io.BytesIO(image_bytes))
        
        # Remove borders
        image = self.remove_borders(original)
        
        # Preprocess
        preprocessed = self.preprocess(image, method=method)
        
        return original, preprocessed


# =========================
# CONVENIENCE FUNCTIONS
# =========================

def preprocess_for_ocr(
    image_bytes: bytes,
    method: str = "auto"
) -> Image.Image:
    """
    Quick preprocessing function.
    
    Args:
        image_bytes: Raw image bytes
        method: "auto", "standard", "aggressive", "light"
    
    Returns:
        Preprocessed PIL Image
    """
    preprocessor = OCRPreprocessor()
    _, preprocessed = preprocessor.enhance_for_ocr(image_bytes, method)
    return preprocessed


def preprocess_pil_image(
    image: Image.Image,
    method: str = "auto"
) -> Image.Image:
    """
    Preprocess PIL Image directly.
    
    Args:
        image: PIL Image
        method: Preprocessing method
    
    Returns:
        Preprocessed PIL Image
    """
    preprocessor = OCRPreprocessor()
    return preprocessor.preprocess(image, method)
