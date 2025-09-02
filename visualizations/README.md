# Protein Best Hits Visualizations

This directory contains comprehensive visualizations of the protein best hits analysis across all genomes.

## Visualization Types

### 1. Bubble Plots (`*_bubble_plot.png`)

**Purpose**: Show the significance and quality of best hits for each query protein across all genomes.

**Layout**:
- **X-axis**: Different genomes (8 total)
- **Y-axis**: Different query proteins from each family
- **Bubble size**: Represents significance level
- **Bubble color**: Represents significance category
- **Text labels**: Percent identity values

**Significance Categories**:
- **VERY HIGH** (Red, large): E-value ≤ 1e-50 AND identity ≥ 70% - Likely orthologs
- **HIGH** (Orange, medium-large): E-value ≤ 1e-20 AND identity ≥ 50% - Likely orthologs
- **MEDIUM** (Yellow, medium): E-value ≤ 1e-5 AND identity ≥ 30% - Likely homologs
- **LOW** (Green, small): Other significant hits - Possible homologs
- **NOT FOUND** (Gray, very small): No significant hits found

### 2. Heatmaps (`*_heatmap.png`)

**Purpose**: Provide a color-coded overview of percent identity values across all query-genome combinations.

**Layout**:
- **X-axis**: Different genomes
- **Y-axis**: Different query proteins
- **Color intensity**: Percent identity (0-100%)
- **Text annotations**: Exact percent identity values

**Color Scheme**: Red-Yellow-Blue (RdYlBu_r)
- **Red**: High identity (80-100%)
- **Yellow**: Medium identity (40-80%)
- **Blue**: Low identity (0-40%)
- **White/Black text**: Optimized for readability

## Protein Families Analyzed

### 1. **Elongases** (2 queries)
- **File**: `elongases_bubble_plot.png`, `elongases_heatmap.png`
- **Pattern**: High conservation, 100% hit rate across all genomes
- **Key insights**: Essential function, highly conserved

### 2. **Desaturases** (5 queries)
- **File**: `desaturases_bubble_plot.png`, `desaturases_heatmap.png`
- **Pattern**: Variable conservation, 80% hit rate
- **Key insights**: Some highly conserved, others more variable

### 3. **Hydroxylases** (6 queries)
- **File**: `hydroxylases_bubble_plot.png`, `hydroxylases_heatmap.png`
- **Pattern**: Good conservation, 70.8% hit rate
- **Key insights**: Many high-quality matches, some gaps

### 4. **Polyketide Synthases** (2 queries)
- **File**: `polyketide_synthases_bubble_plot.png`, `polyketide_synthases_heatmap.png`
- **Pattern**: Moderate conservation, 81.2% hit rate
- **Key insights**: Variable conservation, some high-quality matches

### 5. **Long Polyketide Synthases** (11 queries)
- **File**: `pks_long_bubble_plot.png`, `pks_long_heatmap.png`
- **Pattern**: Excellent conservation, 100% hit rate
- **Key insights**: Most widespread distribution, many orthologs

### 6. **Decarboxylases** (1 query)
- **File**: `decarboxylases_bubble_plot.png`, `decarboxylases_heatmap.png`
- **Pattern**: Lower conservation, 62.5% hit rate
- **Key insights**: Limited distribution, some high-quality matches

## Genome Performance Summary

### **Top Performers**:
- **Ochro3194_1**: Highest average identity (89.2%), most orthologs
- **Gepoce1**: Excellent performance (84.7% average identity)
- **Isogal1**: Good performance (56.6% average identity)

### **Moderate Performers**:
- **IsochDm2_1**: Moderate performance (55.4% average identity)
- **Phaglo1**: Variable performance (38.0% average identity)

### **Lower Performers**:
- **Chrsp_1**: Lower conservation (40.1% average identity)
- **Chrpa1_1**: Lower conservation (34.8% average identity)
- **Pparv12B1_1_1**: Lower conservation (35.6% average identity)

## How to Interpret the Visualizations

### **Bubble Plots**:
1. **Large red bubbles**: Strong evidence for orthologs
2. **Medium orange bubbles**: Good evidence for orthologs
3. **Small yellow bubbles**: Evidence for homologs
4. **Small green bubbles**: Weak evidence for homologs
5. **Tiny gray bubbles**: No significant hits

### **Heatmaps**:
1. **Red regions**: High sequence identity (80-100%)
2. **Yellow regions**: Medium sequence identity (40-80%)
3. **Blue regions**: Low sequence identity (0-40%)
4. **Text values**: Exact percent identity for each combination

## Key Evolutionary Insights

1. **Essential Functions**: Elongases and long PKS show highest conservation
2. **Functional Diversity**: Desaturases and hydroxylases show variable conservation
3. **Genome Relationships**: Ochro3194_1 and Gepoce1 are most closely related
4. **Functional Conservation**: Some protein families are more conserved than others
5. **Evolutionary Distance**: Chrsp_1 and Chrpa1_1 show more distant relationships

## Usage

These visualizations can be used for:
- **Comparative genomics** studies
- **Functional annotation** of unknown proteins
- **Evolutionary relationship** analysis
- **Publication figures** and presentations
- **Quality assessment** of genome assemblies and annotations

## File Formats

All visualizations are saved as high-resolution PNG files (300 DPI) suitable for:
- Publications and presentations
- Web display
- Further analysis and manipulation

