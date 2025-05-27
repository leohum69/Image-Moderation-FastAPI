# # app/image_analyzer.py
# import hashlib
# from PIL import Image
# import numpy as np
# from datetime import datetime
# from typing import List
# import random

# from database.models import ModerationResult, SafetyCategory

# class ImageAnalyzer:
#     """
#     Image analysis service for content moderation.
#     This is a mock implementation - in production you'd integrate with
#     services like Google Vision API, AWS Rekognition, or custom ML models.
#     """
    
#     def __init__(self):
#         # Mock categories we check for
#         self.categories = [
#             "explicit_nudity",
#             "graphic_violence", 
#             "hate_symbols",
#             "self_harm",
#             "extremist_content",
#             "drugs",
#             "weapons"
#         ]
    
#     async def analyze_image(self, image: Image.Image) -> ModerationResult:
#         """
#         Analyze image for harmful content.
#         This is a mock implementation that randomly generates results
#         based on some image properties for demonstration purposes.
#         """
        
#         # Generate image hash for tracking
#         image_hash = self._generate_image_hash(image)
        
#         # Mock analysis based on image properties
#         width, height = image.size
#         pixel_count = width * height
        
#         # Convert to numpy array for basic analysis
#         img_array = np.array(image.convert('RGB'))
#         avg_brightness = np.mean(img_array)
        
#         # Mock safety analysis
#         categories = self._mock_safety_analysis(pixel_count, avg_brightness)
        
#         # Determine overall safety
#         high_risk_categories = [cat for cat in categories if cat.severity == "high"]
#         is_safe = len(high_risk_categories) == 0
        
#         # Calculate overall confidence
#         overall_confidence = np.mean([cat.confidence for cat in categories])
        
#         return ModerationResult(
#             is_safe=is_safe,
#             overall_confidence=float(overall_confidence),
#             categories=categories,
#             analysis_timestamp=datetime.utcnow(),
#             image_hash=image_hash
#         )
    
#     def _generate_image_hash(self, image: Image.Image) -> str:
#         """Generate a hash for the image"""
#         # Convert image to bytes and hash
#         img_bytes = image.tobytes()
#         return hashlib.md5(img_bytes).hexdigest()
    
#     def _mock_safety_analysis(self, pixel_count: int, avg_brightness: float) -> List[SafetyCategory]:
#         """
#         Mock safety analysis that generates realistic-looking results.
#         In production, this would be replaced with actual ML models or API calls.
#         """
#         categories = []
        
#         # Set random seed based on image properties for consistency
#         random.seed(int(pixel_count + avg_brightness))
        
#         for category in self.categories:
#             # Generate mock confidence score
#             confidence = random.uniform(0.1, 0.95)
            
#             # Determine severity based on confidence
#             if confidence > 0.8:
#                 severity = "high"
#             elif confidence > 0.5:
#                 severity = "medium"
#             else:
#                 severity = "low"
            
#             # Only include categories with meaningful confidence
#             if confidence > 0.2:
#                 categories.append(SafetyCategory(
#                     category=category,
#                     confidence=round(confidence, 3),
#                     severity=severity
#                 ))
        
#         # Ensure at least one safe category if no high-risk found
#         if not any(cat.severity == "high" for cat in categories):
#             categories.append(SafetyCategory(
#                 category="safe_content",
#                 confidence=0.95,
#                 severity="low"
#             ))
        
#         return categories[:3]  # Return top 3 categories

from PIL import Image
from transformers import AutoFeatureExtractor, AutoModelForImageClassification
import torch
from typing import List
from datetime import datetime
import numpy as np
import hashlib

from database.models import ModerationResult, SafetyCategory


class ImageAnalyzer:
    def __init__(self):
        # Load prebuilt model from Hugging Face
        self.extractor = AutoFeatureExtractor.from_pretrained("Falconsai/nsfw_image_detection")
        self.model = AutoModelForImageClassification.from_pretrained("Falconsai/nsfw_image_detection")
        self.labels = self.model.config.id2label

    async def analyze_image(self, image: Image.Image) -> ModerationResult:
        image_hash = self._generate_image_hash(image)
        
        inputs = self.extractor(images=image, return_tensors="pt")
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        probs = torch.nn.functional.softmax(outputs.logits, dim=1)[0]
        categories = []

        for idx, prob in enumerate(probs):
            label = self.labels[idx]
            confidence = prob.item()
            severity = self._label_to_severity(label, confidence)
            if confidence > 0.1:
                categories.append(SafetyCategory(
                    category=label,
                    confidence=round(confidence, 3),
                    severity=severity
                ))

        is_safe = not any(cat.severity == "high" for cat in categories)
        overall_confidence = float(np.mean([cat.confidence for cat in categories]))

        return ModerationResult(
            is_safe=is_safe,
            overall_confidence=overall_confidence,
            categories=categories,
            analysis_timestamp=datetime.utcnow(),
            image_hash=image_hash
        )

    def _label_to_severity(self, label: str, confidence: float) -> str:
        if label in ["porn", "hentai", "sexy"] and confidence > 0.7:
            return "high"
        elif confidence > 0.5:
            return "medium"
        return "low"

    def _generate_image_hash(self, image: Image.Image) -> str:
        img_bytes = image.tobytes()
        return hashlib.md5(img_bytes).hexdigest()
