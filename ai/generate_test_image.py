import cv2
import numpy as np

# Create a blank image
image = np.zeros((640, 640, 3), dtype=np.uint8)
cv2.putText(image, "Test Image", (200, 320), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

# Save the test image
cv2.imwrite("test.jpg", image)
print("✅ Test image created successfully! Check 'backend/ai/test.jpg'.")
