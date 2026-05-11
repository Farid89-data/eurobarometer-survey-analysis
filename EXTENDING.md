# Extending the Eurobarometer Analysis Framework

This guide shows how to add new capabilities to the analysis framework.

## 1. Adding Custom Analysis Methods

The architecture is designed for extensibility. Here's how to add new analysis.

### Example 1: Analyzing Trust in Institutions (D70)

```python
def analyze_institutional_trust(self) -> Dict[str, Dict[str, float]]:
    """
    Analyze trust levels in EU institutions across member states.
    
    This method demonstrates how to extend the analyzer with new
    custom analysis while maintaining code quality standards.
    
    Returns:
        Dict[str, Dict[str, float]]: Structure:
            {
                'institution_name': {
                    'high_trust_%': float,
                    'neutral_%': float,
                    'low_trust_%': float,
                    'dontknow_%': float
                },
                ...
            }
    
    Raises:
        Exception: If D70 sheet cannot be parsed
    
    Example:
        >>> analyzer = EurobarometerAnalyzer('data.xlsx')
        >>> trust = analyzer.analyze_institutional_trust()
        >>> print(trust['European Commission'])
        {'high_trust_%': 32.5, 'neutral_%': 38.2, 'low_trust_%': 29.3}
    """
    logger.info("Analyzing institutional trust...")
    
    try:
        df_d70 = self.load_data_sheet('D70')
        trust_data = {}
        
        # D70 typically contains questions about trust in:
        # - European Parliament
        # - European Commission
        # - Council of the European Union
        # - European Central Bank
        
        institutions = [
            'European Parliament',
            'European Commission',
            'Council',
            'European Central Bank'
        ]
        
        # Extract trust levels for each institution
        for idx, row in df_d70.iloc[5:15].iterrows():
            institution = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else None
            
            if institution and any(inst in institution for inst in institutions):
                trust_data[institution] = {
                    'high_trust_%': float(pd.to_numeric(row.iloc[2], errors='coerce') or 0),
                    'neutral_%': float(pd.to_numeric(row.iloc[3], errors='coerce') or 0),
                    'low_trust_%': float(pd.to_numeric(row.iloc[4], errors='coerce') or 0),
                    'dontknow_%': float(pd.to_numeric(row.iloc[5], errors='coerce') or 0)
                }
        
        self.analysis_results['institutional_trust'] = trust_data
        logger.info(f"Analyzed trust for {len(trust_data)} institutions")
        return trust_data
        
    except Exception as e:
        logger.warning(f"Institutional trust analysis failed: {e}")
        return {}
```

**Then add to the main analysis pipeline:**

```python
def run_full_analysis(self) -> Dict:
    """Existing method - add one line."""
    
    # ... existing code ...
    
    # Phase 3: Analysis (add this line)
    self.analyze_institutional_trust()  # ← NEW LINE
    
    # ... rest of existing code ...
```

### Example 2: European Integration Sentiment Analysis (D71_1)

```python
def analyze_european_integration(self) -> Dict[str, float]:
    """
    Analyze citizen sentiment toward European integration.
    
    Extracts responses to the core integration question:
    "In general, is the pace of European integration too slow, 
    about right, or too fast?"
    
    Returns:
        Dict[str, float]: Distribution of responses
            {
                'too_slow_%': float,
                'about_right_%': float,
                'too_fast_%': float,
                'no_opinion_%': float
            }
    
    Example:
        >>> analyzer = EurobarometerAnalyzer('data.xlsx')
        >>> sentiment = analyzer.analyze_european_integration()
        >>> if sentiment['too_fast_%'] > 40:
        ...     print("Integration skepticism high")
    """
    logger.info("Analyzing European integration sentiment...")
    
    try:
        df_d71_1 = self.load_data_sheet('D71_1')
        
        sentiment = {}
        
        # Extract integration sentiment percentages
        for idx, row in df_d71_1.iloc[5:10].iterrows():
            response = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else None
            percentage = pd.to_numeric(row.iloc[2], errors='coerce')
            
            if response and pd.notna(percentage):
                # Normalize key names
                if 'slow' in response.lower():
                    sentiment['too_slow_%'] = float(percentage)
                elif 'right' in response.lower() or 'appropriate' in response.lower():
                    sentiment['about_right_%'] = float(percentage)
                elif 'fast' in response.lower():
                    sentiment['too_fast_%'] = float(percentage)
                elif 'opinion' in response.lower() or 'know' in response.lower():
                    sentiment['no_opinion_%'] = float(percentage)
        
        # Validate sum to 100%
        total = sum(sentiment.values())
        if not (99 < total < 101):
            logger.warning(f"Integration sentiment sums to {total}%, expected ~100%")
        
        self.analysis_results['integration_sentiment'] = sentiment
        logger.info(f"Integration sentiment: {sentiment}")
        return sentiment
        
    except Exception as e:
        logger.warning(f"European integration analysis failed: {e}")
        return {}
```

## 2. Adding Custom Visualizations

### Example: Trust Comparison Chart

```python
def visualize_institutional_trust(self, output_dir: str = './outputs') -> str:
    """
    Create bar chart comparing trust levels across institutions.
    
    Args:
        output_dir: Directory to save the visualization
        
    Returns:
        str: Path to saved visualization
    """
    logger.info("Creating institutional trust visualization...")
    
    try:
        trust_data = self.analysis_results.get('institutional_trust', {})
        
        if not trust_data:
            logger.warning("No institutional trust data to visualize")
            return ""
        
        # Prepare data
        institutions = list(trust_data.keys())
        high_trust = [trust_data[i]['high_trust_%'] for i in institutions]
        
        # Create visualization
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x = np.arange(len(institutions))
        width = 0.6
        
        bars = ax.bar(x, high_trust, width, label='High Trust', color='steelblue', alpha=0.8)
        
        # Customization
        ax.set_ylabel('Percentage (%)', fontsize=11, fontweight='bold')
        ax.set_title('Trust in EU Institutions - Spring 2023', fontsize=13, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(institutions, rotation=45, ha='right')
        ax.set_ylim(0, 100)
        
        # Value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%', ha='center', va='bottom', fontsize=9)
        
        ax.legend()
        plt.tight_layout()
        
        # Save
        Path(output_dir).mkdir(exist_ok=True)
        path = f"{output_dir}/institutional_trust.png"
        plt.savefig(path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved institutional trust visualization: {path}")
        return path
        
    except Exception as e:
        logger.warning(f"Could not create trust visualization: {e}")
        return ""
```

**Add to `create_visualizations()` method:**

```python
def create_visualizations(self, output_dir: str = './outputs') -> List[str]:
    """Existing method - add visualization call."""
    
    created_files = []
    Path(output_dir).mkdir(exist_ok=True)
    
    # ... existing visualizations ...
    
    # Add new visualization
    trust_viz = self.visualize_institutional_trust(output_dir)
    if trust_viz:
        created_files.append(trust_viz)
    
    return created_files
```

## 3. Adding Data Export Formats

### Example: Export to CSV

```python
def export_to_csv(self, output_dir: str = './outputs') -> List[str]:
    """
    Export analysis results to CSV format for Excel/spreadsheet compatibility.
    
    Args:
        output_dir: Directory to save CSV files
        
    Returns:
        List[str]: Paths to created CSV files
    """
    logger.info("Exporting data to CSV format...")
    
    created_files = []
    Path(output_dir).mkdir(exist_ok=True)
    
    try:
        # Export age distribution
        age_dist = self.analysis_results.get('age_distribution', {})
        if age_dist:
            df_age = pd.DataFrame(
                list(age_dist.items()),
                columns=['Age Group', 'Percentage']
            )
            path = f"{output_dir}/age_distribution.csv"
            df_age.to_csv(path, index=False, encoding='utf-8')
            created_files.append(path)
            logger.info(f"Exported age distribution: {path}")
        
        # Export metadata
        if self.metadata:
            metadata_dict = {
                'Attribute': [
                    'Survey Name', 'Wave', 'Fieldwork Dates',
                    'Sample Size', 'Countries', 'Weighting Method'
                ],
                'Value': [
                    self.metadata.survey_name,
                    self.metadata.wave,
                    self.metadata.fieldwork_dates,
                    str(self.metadata.sample_size),
                    str(self.metadata.countries),
                    self.metadata.weighting_method
                ]
            }
            df_metadata = pd.DataFrame(metadata_dict)
            path = f"{output_dir}/survey_metadata.csv"
            df_metadata.to_csv(path, index=False, encoding='utf-8')
            created_files.append(path)
            logger.info(f"Exported metadata: {path}")
        
        return created_files
        
    except Exception as e:
        logger.warning(f"CSV export failed: {e}")
        return []
```

## 4. Filtering & Subsetting Data

### Example: Country-Specific Analysis

```python
def analyze_country_data(self, country_code: str) -> Dict[str, float]:
    """
    Perform detailed analysis for a specific country.
    
    Args:
        country_code: ISO 2-letter country code (e.g., 'DE', 'FR')
        
    Returns:
        Dict[str, float]: Analysis metrics for the country
    """
    logger.info(f"Analyzing data for {country_code}...")
    
    if country_code not in self.EU27_COUNTRIES:
        logger.warning(f"Invalid country code: {country_code}")
        return {}
    
    country_data = self.processed_data.get('country_demographics', {})
    
    if country_code not in country_data:
        logger.warning(f"No data available for {country_code}")
        return {}
    
    data = country_data[country_code]
    
    analysis = {
        'country': country_code,
        'sample_size': len(data),
        'mean': float(data.mean()) if len(data) > 0 else 0,
        'median': float(data.median()) if len(data) > 0 else 0,
        'std_dev': float(data.std()) if len(data) > 0 else 0,
        'min': float(data.min()) if len(data) > 0 else 0,
        'max': float(data.max()) if len(data) > 0 else 0
    }
    
    logger.info(f"Analysis complete for {country_code}")
    return analysis
```

**Usage:**

```python
analyzer = EurobarometerAnalyzer('data.xlsx')
analyzer.run_full_analysis()

# Analyze specific country
germany_stats = analyzer.analyze_country_data('DE')
france_stats = analyzer.analyze_country_data('FR')

# Compare countries
if germany_stats['mean'] > france_stats['mean']:
    print("Germany higher than France")
```

## 5. Integration with External Tools

### Example: Pandas Workflow Integration

```python
# Extract data for downstream processing
analyzer = EurobarometerAnalyzer('data.xlsx')
analyzer.run_full_analysis()

# Get structured data
country_demographics = analyzer.processed_data['country_demographics']

# Convert to DataFrame for further analysis
df = pd.DataFrame(country_demographics).T

# Typical Pandas operations
df['above_median'] = df.mean(axis=1) > df.mean(axis=1).median()
df['growth_rate'] = df.iloc[:, -1] / df.iloc[:, 0] - 1

# Export for downstream
df.to_csv('country_demographics.csv')
df.to_parquet('country_demographics.parquet')  # Efficient format
```

### Example: Database Integration

```python
import sqlite3

analyzer = EurobarometerAnalyzer('data.xlsx')
results = analyzer.run_full_analysis()

# Create database
conn = sqlite3.connect('eurobarometer.db')

# Create tables
sql_create_metadata = """
    CREATE TABLE survey_metadata (
        id INTEGER PRIMARY KEY,
        survey_name TEXT,
        wave TEXT,
        fieldwork_dates TEXT,
        sample_size INTEGER,
        countries INTEGER
    )
"""

conn.execute(sql_create_metadata)

# Insert data
metadata = results['metadata']
conn.execute(
    "INSERT INTO survey_metadata VALUES (?, ?, ?, ?, ?, ?)",
    (1, metadata['survey'], metadata['wave'], 
     metadata['fieldwork'], metadata['sample_size'], metadata['countries'])
)

conn.commit()
conn.close()

logger.info("Data successfully loaded into SQLite database")
```

## 6. Testing Your Extensions

### Example: Unit Tests

```python
import unittest
from pathlib import Path

class TestExtensions(unittest.TestCase):
    """Test suite for custom analysis extensions."""
    
    @classmethod
    def setUpClass(cls):
        """Initialize analyzer once for all tests."""
        cls.analyzer = EurobarometerAnalyzer('test_data.xlsx')
        cls.analyzer.load_survey_metadata()
    
    def test_institutional_trust_returns_dict(self):
        """Verify trust analysis returns proper structure."""
        trust = self.analyzer.analyze_institutional_trust()
        
        self.assertIsInstance(trust, dict)
        self.assertGreater(len(trust), 0)
    
    def test_trust_values_in_valid_range(self):
        """Verify trust percentages are within valid bounds."""
        trust = self.analyzer.analyze_institutional_trust()
        
        for institution, values in trust.items():
            for metric, value in values.items():
                self.assertGreaterEqual(value, 0)
                self.assertLessEqual(value, 100)
    
    def test_integration_sentiment_sum(self):
        """Verify integration sentiment percentages sum to ~100."""
        sentiment = self.analyzer.analyze_european_integration()
        
        total = sum(sentiment.values())
        self.assertGreater(total, 99)
        self.assertLess(total, 101)
    
    def test_country_analysis_valid_code(self):
        """Verify country analysis works with valid codes."""
        analyzer.run_full_analysis()
        
        stats = self.analyzer.analyze_country_data('DE')
        self.assertIsInstance(stats, dict)
        self.assertEqual(stats['country'], 'DE')
        self.assertGreater(stats['sample_size'], 0)

if __name__ == '__main__':
    unittest.main()
```

**Run tests:**

```bash
python -m pytest test_extensions.py -v
python -m pytest test_extensions.py --cov=eurobarometer_analysis  # With coverage
```

## 7. Creating Specialized Pipelines

### Example: Demographic Profile Pipeline

```python
def create_demographic_profile_pipeline(self, output_file: str = 'demographic_profile.json'):
    """
    Execute specialized pipeline for demographic profiling.
    
    Returns complete demographic breakdown with cross-tabulations.
    """
    logger.info("Creating demographic profile pipeline...")
    
    # Extract all demographic dimensions
    age_dist = self.analyze_age_distribution()
    country_data = self.extract_country_data()
    quality = self.calculate_data_quality_metrics()
    
    # Combine into structured profile
    profile = {
        'timestamp': datetime.now().isoformat(),
        'demographics': {
            'age': age_dist,
            'geography': country_data,
        },
        'quality_assurance': quality,
        'statistics': {
            'total_respondents': self.metadata.sample_size,
            'countries_covered': self.metadata.countries,
            'completeness': quality.get('completeness_percentage', 0)
        }
    }
    
    # Export
    with open(output_file, 'w') as f:
        json.dump(profile, f, indent=2, default=str)
    
    logger.info(f"Demographic profile saved to {output_file}")
    return profile
```

## 8. Handling Edge Cases

### Example: Robust Error Handling

```python
def analyze_with_fallback(self, primary_sheet: str, fallback_sheet: str) -> Dict:
    """
    Attempt analysis on primary sheet, fall back to alternative if needed.
    
    This pattern shows resilience in production pipelines.
    """
    try:
        logger.info(f"Attempting analysis on {primary_sheet}...")
        df = self.load_data_sheet(primary_sheet)
        
        # Attempt analysis
        if df.shape[0] < 5:
            raise ValueError(f"Sheet {primary_sheet} has insufficient data")
        
        return self._process_sheet(df, primary_sheet)
        
    except (FileNotFoundError, KeyError) as e:
        logger.warning(f"{primary_sheet} not available, falling back to {fallback_sheet}")
        
        try:
            df = self.load_data_sheet(fallback_sheet)
            return self._process_sheet(df, fallback_sheet)
            
        except Exception as fallback_error:
            logger.error(f"Both sheets failed: {e}, {fallback_error}")
            return {}

def _process_sheet(self, df: pd.DataFrame, sheet_name: str) -> Dict:
    """Common processing logic."""
    # Implementation
    pass
```

---

**Summary:** The framework is designed for extensibility while maintaining code quality. Each new feature:

1. ✅ Follows the established architecture
2. ✅ Includes comprehensive docstrings
3. ✅ Has appropriate error handling
4. ✅ Logs operations at suitable levels
5. ✅ Integrates seamlessly into the pipeline

Use these examples as templates for your own extensions!
