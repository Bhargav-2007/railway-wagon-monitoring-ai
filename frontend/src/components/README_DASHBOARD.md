# Model Analytics Dashboard Components

## Overview
These components create a Roboflow-inspired analytics dashboard for the Railway Wagon Monitoring AI System. They provide real-time visualization of model training progress, performance metrics, and deployment status.

## Components

### 1. **ModelStats.tsx**
Displays key metrics in card format:
- **mAP@50**: Mean Average Precision at 50% IoU threshold
- **Precision**: Classification precision percentage
- **Recall**: Detection recall percentage  
- **Total Images**: Number of training images

**Features**:
- Responsive grid layout (1 column mobile, 4 columns desktop)
- Color-coded metric cards with gradient overlays
- Hover effects and smooth transitions

**Props**:
```typescript
interface ModelStatsProps {
  mapScore?: number;        // Default: 80.5
  precision?: number;       // Default: 87.2
  recall?: number;          // Default: 60.0
  totalImages?: number;     // Default: 113
}
```

---

### 2. **TrainingProgress.tsx**
Shows real-time training progress with epoch tracking:
- Current epoch / total epochs progress bar
- Time remaining estimation
- Completion percentage
- Training status indicator

**Features**:
- Animated progress bar with gradient
- Live training spinner animation
- Responsive two-column stats layout
- Real-time epoch updates

**Props**:
```typescript
interface TrainingProgressProps {
  currentEpoch?: number;     // Default: 35
  totalEpochs?: number;      // Default: 40
  timeRemaining?: string;    // Default: '40 minutes'
  isTraining?: boolean;      // Default: true
}
```

---

### 3. **ModelPerformance.tsx**
Displays model loss metrics across training:
- **Box Location Loss**: Bounding box positioning accuracy
- **Class Loss**: Classification loss value
- **Box Overlap Loss**: IoU-based overlap loss

**Features**:
- Three-column metric layout
- Loss trend indicators (increasing/decreasing)
- Gradient-colored visual indicators
- Convergence status and percentage

**Props**:
```typescript
interface ModelPerformanceProps {
  epoch?: number;            // Default: 35
  data?: PerformanceData;    // Default loss values
}
```

---

### 4. **ModelAnalyticsDashboard.tsx** (Main Component)
Integrates all sub-components into a complete dashboard:
- Header with model info and version badge
- Quick stats bar (images, model type, epoch, status)
- Model metrics section
- Training progress and performance side-by-side
- Deployment readiness info

**Features**:
- Dark gradient background matching Roboflow style
- Sticky header for navigation
- Color-coded section indicators
- Responsive grid layout
- Deployment status display

**Props**:
```typescript
interface ModelAnalyticsDashboardProps {
  data?: ModelData;  // Complete model information object
}
```

---

## Integration Example

```tsx
import ModelAnalyticsDashboard from './components/ModelAnalyticsDashboard';

function App() {
  const modelData = {
    modelName: 'Wagons defect',
    version: 'v1',
    modelType: 'RF-DETR (Medium)',
    datasetVersion: '2026-01-08 11:39pm',
    mapScore: 80.5,
    precision: 87.2,
    recall: 60.0,
    totalImages: 113,
    currentEpoch: 35,
    totalEpochs: 40,
    timeRemaining: '40 minutes',
    isTraining: true,
    boxLocationLoss: 0.18,
    classLoss: 0.65,
    boxOverlapLoss: 0.47,
  };

  return <ModelAnalyticsDashboard data={modelData} />;
}
```

---

## Styling

All components use **Tailwind CSS** utility classes:
- Dark theme: Gray-900 background with gray-700 borders
- Color accents: Purple, blue, pink, and green gradients
- Typography: Bold white text on dark backgrounds
- Spacing: Consistent padding and margins for visual hierarchy

---

## Responsive Behavior

- **Mobile**: Single column layout, stacked components
- **Tablet**: 2-column grid for metrics and progress
- **Desktop**: Full 4-column stats, side-by-side sections

---

## Future Enhancements

1. **Real-time Data Integration**: Connect to WebSocket for live updates
2. **Interactive Charts**: Add Recharts for loss curves visualization
3. **Export Functionality**: Download metrics as PDF/CSV
4. **Threshold Alerts**: Notify when metrics exceed thresholds
5. **Model Comparison**: Side-by-side comparison of multiple versions
6. **Deployment Wizard**: Step-by-step model export and deployment

---

## Files

- `ModelStats.tsx` - Metric cards component
- `TrainingProgress.tsx` - Progress tracking component
- `ModelPerformance.tsx` - Loss metrics component
- `ModelAnalyticsDashboard.tsx` - Main dashboard integration

