# Advanced AI Architecture for Wildfire Prediction

This document explores moving beyond structural baseline models (like Random Forest) to Deep Learning (LSTM + CNN architectures) for wildfire prediction, and evaluates the tradeoffs and feasibility.

## 1. When Advanced Deep Learning is Beneficial

Deep learning shines when the relationship between features and the target is highly non-linear, spatial, and temporal.

- **Spatio-Temporal Dynamics**: Fire spread is inherently temporal (weather changes over days) and spatial (fire moves across terrain). LSTMs capture the temporal sequences, while CNNs capture the spatial context from satellite imagery.
- **Complex Feature Interactions**: CNNs can automatically extract visual features (like dryness patterns or burn scars) directly from raw satellite pixels, without requiring manual feature engineering like NDVI extraction.
- **High Data Volume**: Deep learning requires massive datasets to outperform tree-based models. If you have petabytes of historical satellite imagery and weather data, DL can leverage it.

## 2. Architecture Diagrams

### Spatio-Temporal Hybrid Architecture (CNN-LSTM)

This architecture combines raw pixel data with temporal weather data.

```text
[Satellite Imagery (t-3 ... t)] ---> [CNN Layers (ResNet/VGG)] ---> [Spatial Embeddings]
                                                                                |
                                                                                v
[Weather Data Sequence (t-3 ... t)] -------------------------------> [Concatenation]
                                                                                |
                                                                                v
                                                                          [LSTM Layers]
                                                                                |
                                                                                v
                                                                     [Dense/Output Layers]
                                                                                |
                                                                                v
                                                       [Prediction: Burn Probability / Size Class]
```

## 3. Required Datasets

To train this architecture, you need:

1.  **Multi-spectral Satellite Imagery**: NASA MODIS (moderate resolution) or Landsat (daily passes). You need sequences of images leading up to fire events.
2.  **Weather Time-Series**: Hourly or daily ERA5 or NOAA data (Temp, Humidity, Wind), aligned chronologically with the satellite data.
3.  **Topography**: USGS DEM (Elevation, Slope, Aspect) represented as image channels.
4.  **Fire Mask Labels**: Historical fire perimeters (e.g., from MTBS) mapped onto the same coordinate system as your satellite imagery to act as the target `y` mask.

## 4. GPU Requirements

- **Training**: Training a CNN-LSTM on high-resolution satellite imagery covering large regions requires significant VRAM. Min: 1x NVIDIA RTX 3090/4090 (24GB). Ideal: Cloud instances (AWS p3.2xlarge or GCP p4d.24xlarge with A100s).
- **Inference**: Less intensive but still requires a GPU for low-latency batch predictions over large geographical grids.

## 5. Tradeoffs vs Random Forest / XGBoost

| Feature | Random Forest / XGBoost | CNN-LSTM (Deep Learning) |
| :--- | :--- | :--- |
| **Data Requirements** | Moderate (Tabular data) | Massive (Images + Sequences) |
| **Compute Cost** | Low to Moderate (CPU/Basic GPU) | Extremely High (Multi-GPU clusters) |
| **Interpretability** | High (Feature Importance) | Low ("Black Box") |
| **Feature Engineering**| High (Requires domain expertise) | Low (Automatic extraction) |
| **Time to Develop** | Fast (Days/Weeks) | Slow (Months) |

## 6. Realistic Implementation Scope for an Internship

**Attempting a full spatial-temporal CNN-LSTM over satellite imagery is too ambitious for a standard 10-12 week internship** unless you are given a pre-processed, clean, ready-to-train tensor dataset on day one.

The bottlenecks will be:
1. Downloading terabytes of HDF/GeoTIFF files.
2. Aligning grids, projections, and timestamps.
3. Managing cloud compute infrastructure.

## 7. Simplified Implementation Strategy (Internship Friendly DL)

If the goal is to demonstrate Deep Learning capabilities, scale down the problem:

**The "Tabular LSTM" Approach**

Instead of using raw imagery, use the extracted tabular features (NDVI, Temp, Humidity) but treat them as a **time-series**.

1.  **Objective**: Predict fire risk for *tomorrow* based on the sequence of the *past 7 days*.
2.  **Data Format**: Group your tabular dataframe by location. Create rolling windows of length `n_days=7`.
3.  **Input Shape**: `(batch_size, time_steps, num_features)` -> `(N, 7, 10)`
4.  **Architecture**:
    - Input Layer
    - LSTM (e.g., 64 units) -> captures how the weather has been trending leading up to the day.
    - Dropout (0.2)
    - Dense Output (Sigmoid for binary occurrence).
5.  **Tech Stack**: PyTorch or TensorFlow, trained on a local consumer GPU or Google Colab.

This achieves the goal of demonstrating advanced time-series forecasting (LSTM) while avoiding the immense data engineering overhead of processing raw satellite imagery.