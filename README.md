# RouteForceRouting

A route optimization engine for field execution teams. This application helps optimize routes for visiting multiple locations efficiently.

## 🚨 **IMPORTANT SECURITY NOTICE**

**CRITICAL**: API keys were previously exposed in the source code. If you're using this codebase:

1. **IMMEDIATELY rotate your Google Maps API keys**
2. **Never commit API keys to version control**
3. **Use environment variables for all sensitive data**

## ✅ **RECENT IMPROVEMENTS**

- ✅ **Geocoding Cache**: Implemented persistent caching to prevent API rate limiting
- ✅ **Security Fixes**: Added proper `.gitignore` protection for environment files
- ✅ **Performance**: Dramatic speedup for repeated geocoding operations
- ✅ **Error Handling**: Improved error handling and user experience
- ✅ **User Interface**: Better CLI with progress indicators and cache statistics

## 📋 **Current Status**

This is a **pre-alpha** version with the following capabilities:

- ✅ **Data Loading**: Loads from Excel/CSV files with validation
- ✅ **Geocoding**: Converts addresses to coordinates with intelligent caching
- ✅ **Route Optimization**: Basic nearest-neighbor algorithm
- ✅ **Google Maps Integration**: Generates clickable route links
- ✅ **Performance**: Cached geocoding for 100x+ speedup on repeated operations
- ⚠️ **Route Algorithm**: Still uses simple greedy algorithm (needs improvement)
- ⚠️ **Business Rules**: No time windows, priorities, or constraints yet

## 🚀 **Quick Start**

### Prerequisites

```bash
# Install Python 3.8+
python3 --version

# Install dependencies
pip install -r requirements.txt
```

### Environment Setup

1. Create a `.env` file in the project root:
```bash
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
GOOGLE_MAPS_API_SECRET=your_google_maps_api_secret_here
```

2. **Never commit your `.env` file to version control**

### Running the Application

```bash
# Basic route generation (limited to 10 stores for testing)
python main.py

# Preview data without generating routes
python -m routing.loader --preview

# Load specific file
python -m routing.loader path/to/your/stores.xlsx
```

## 📊 **Data Format**

Your store data file should have these columns:
- `Store Name` - Name of the store/location
- `Address` - Full address (used for geocoding)

Example:
```csv
Store Name,Address
Store A,123 Main St, New York, NY 10001
Store B,456 Oak Ave, Brooklyn, NY 11201
```

## 🏗️ **Architecture**

```
routing/
├── core.py          # Route optimization logic
├── loader.py        # Data loading and validation
├── utils.py         # Distance calculations and geocoding cache
├── config.py        # Configuration constants
└── __init__.py      # Package initialization
```

## 🔧 **Performance Features**

### Geocoding Cache
- **Persistent Storage**: Caches coordinates in `geocoding_cache.json`
- **Rate Limiting**: Respectful 1-second delays between API calls
- **Performance**: 100x+ speedup for repeated addresses
- **Automatic**: No manual intervention required

### Memory Management
- **Testing Mode**: Limits to 10 stores by default (configurable)
- **Validation**: Checks data integrity during loading
- **Error Recovery**: Graceful handling of geocoding failures

## 🔧 **Known Issues & Limitations**

### Current Limitations
- [ ] **Route Algorithm**: Uses simple greedy algorithm (suboptimal)
- [ ] **Business Rules**: No time windows, priorities, or constraints
- [ ] **Large Datasets**: Limited to 10 stores in testing mode
- [ ] **Return Route**: No return-to-start optimization

### Performance Considerations
- [x] **Geocoding**: Cached for performance (FIXED)
- [ ] **Route Optimization**: Still O(n²) complexity
- [ ] **Memory Usage**: Could be optimized for large datasets
- [ ] **Parallel Processing**: No concurrent geocoding

## 🛠️ **Development Roadmap**

### Phase 1: Core Functionality (Current) ✅
- [x] Basic data loading
- [x] Geocoding with caching
- [x] Simple route generation
- [x] Google Maps integration

### Phase 2: Optimization (Next)
- [ ] Implement proper TSP solver
- [ ] Add business rule constraints
- [ ] Add route validation
- [ ] Remove testing limits

### Phase 3: Production Features
- [ ] Add comprehensive error handling
- [ ] Add logging and monitoring
- [ ] Add unit tests
- [ ] Add configuration management
- [ ] Add performance optimizations

## 🐛 **Troubleshooting**

### Common Issues

1. **"File not found" error**
   - Ensure your data file exists and path is correct
   - Check file permissions

2. **"Invalid data format" error**
   - Verify your file has required columns: `Store Name` and `Address`
   - Check for empty rows or missing data

3. **Geocoding failures**
   - Ensure addresses are complete and valid
   - Check internet connection (geocoding requires API calls)
   - Check cache file permissions

4. **API key errors**
   - Verify your Google Maps API key is valid
   - Check that the key has the necessary permissions
   - Ensure the key is set in your `.env` file

### Performance Tips

1. **First Run**: Initial geocoding will be slow (1 second per address)
2. **Subsequent Runs**: Much faster due to caching
3. **Cache Management**: Cache file grows with unique addresses
4. **Testing**: Use small datasets for development

## 📝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 **License**

[Add your license information here]

## 🆘 **Support**

For issues and questions:
1. Check the troubleshooting section above
2. Review the known issues
3. Create an issue in the repository

---

**⚠️ Remember**: This is pre-alpha software. Use at your own risk and test thoroughly before production use.

**🎯 Performance Note**: The geocoding cache provides significant performance improvements for repeated operations. First-time geocoding of new addresses will still require API calls with appropriate rate limiting.