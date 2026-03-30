# Tomato Leaf Disease Detection & Segmentation System

## Project Title

**Development of a Deep Learning Model for Accurate Detection and Pixel-Level Segmentation of Tomato Leaf Diseases**

---

## 1. Introduction / Background of the Study

Agriculture plays a vital role in food security and economic development. Tomato is one of the most widely cultivated vegetable crops worldwide. However, tomato production is significantly affected by diseases such as:

- Early blight
- Late blight
- Septoria leaf spot

Traditional disease detection methods rely on manual visual inspection, which is:

- Time-consuming
- Subjective
- Prone to misdiagnosis

There is therefore a need for an automated and intelligent system that can detect diseases accurately and efficiently.

---

## 2. Problem Statement

Tomato leaf diseases significantly reduce yield and quality.

Current detection methods:

- Rely heavily on human observation
- Lack precision
- Cannot measure infection severity

Most existing AI systems:

- Perform only classification
- Do not identify exact infected regions

There is no integrated system that:

- Detects disease type
- Segments infected areas at pixel level

---

## 3. Aim and Objectives

### Main Objective

To develop and evaluate a deep learning model for accurate detection and pixel-level segmentation of tomato leaf diseases.

### Specific Objectives

- Collect and preprocess tomato leaf images
- Design a CNN-based detection model
- Implement a U-Net segmentation model
- Train and evaluate the model
- Develop a functional prototype system

---

## 4. Significance of the Study

This project will:

- Assist farmers in early disease detection
- Improve crop management decisions
- Reduce unnecessary pesticide usage
- Support precision agriculture
- Contribute to AI applications in agriculture

### Beneficiaries

- Farmers
- Agricultural extension officers
- Researchers
- Policy makers

---

## 5. Scope and Limitations

### Scope

- Focus on tomato leaf diseases only
- Use image-based deep learning
- Perform classification and segmentation
- Evaluate using:
  - Accuracy
  - IoU (Intersection over Union)
  - Dice Coefficient

### Limitations

- Limited annotated segmentation datasets
- Variations in lighting and background
- Computational resource constraints
- Not extended to other crops

---

## 6. Literature Review

Previous studies show:

- CNN models achieve high classification accuracy
- Mohanty et al. demonstrated deep learning effectiveness using the PlantVillage dataset
- Too et al. compared fine-tuned deep learning models
- Ronneberger et al. introduced U-Net for semantic segmentation

### Research Gap

- Most systems focus only on classification
- Few integrate detection and pixel-level segmentation

---

## 7. Methodology

This study adopts an **Agile development approach**.

### Research Design

Experimental deep learning system development approach.

### Data Collection

- PlantVillage dataset
- Labeled segmentation masks (where available)

### Tools and Technologies

- Python
- PyTorch / TensorFlow
- OpenCV
- FastAPI
- React Native
- Next.js
- Google Colab (for training)

### System Architecture

`Image Input → Preprocessing → CNN Detection → U-Net Segmentation → Output Visualization`

---

## 8. Expected Output / Results

The system will:

- Classify tomato leaves as healthy or diseased
- Identify disease type
- Highlight infected regions using segmentation masks

### Disease Severity Formula

`Disease Severity (%) = (Infected Pixels / Total Leaf Pixels) × 100`

### Expected Performance Metrics

- High Accuracy (>90%)
- High IoU
- High Dice Coefficient

---

## 9. Conclusion

This project proposes an intelligent system for:

- Accurate disease detection
- Precise pixel-level segmentation
- Disease severity estimation

The study demonstrates the practical application of deep learning in smart agriculture and contributes toward:

- Improved crop management
- Reduced crop losses
- Sustainable agricultural development

---

## References

- Mahlein, A. K. (2016). _Plant disease detection by imaging sensors_
- Mohanty, S. P., Hughes, D. P., & Salathé, M. (2016). _Using deep learning for plant disease detection_
- Ronneberger, O., Fischer, P., & Brox, T. (2015). _U-Net: Convolutional networks for biomedical image segmentation_
- Savary, S., et al. (2019). _The global burden of pathogens on major food crops_
- Too, E. C., et al. (2019). _Comparative study of fine-tuned deep learning models_
