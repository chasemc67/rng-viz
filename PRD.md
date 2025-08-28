# Product Requirements Document (PRD)

## RNG Visualizer - TrueRNG Pro V2 Bitstream Analyzer

**Version**: 1.0  
**Date**: 2024  
**Status**: Development

---

## 1. Executive Summary

The RNG Visualizer is a Python command-line application designed to capture, analyze, and visualize bitstreams from the TrueRNG Pro V2 hardware random number generator. Inspired by the Global Consciousness Project, the application detects statistical anomalies in random data that may correlate with consciousness-related phenomena.

### 1.1 Vision Statement

Create a professional-grade tool for real-time analysis of hardware random number generators, enabling researchers to study potential consciousness-matter interactions through statistical deviation detection.

### 1.2 Success Metrics

- Reliable connection to TrueRNG Pro V2 devices
- Real-time statistical analysis with <100ms latency
- Accurate anomaly detection with configurable significance levels
- Intuitive visualization accessible to both technical and non-technical users
- Robust data capture and storage for long-term studies

---

## 2. Product Overview

### 2.1 Target Users

**Primary Users:**

- Consciousness researchers and parapsychologists
- Statistics and randomness enthusiasts
- Citizen scientists interested in GCP-style experiments
- Academic researchers studying random number generators

**Secondary Users:**

- Hardware security researchers
- Cryptographic applications requiring entropy analysis
- Educational institutions teaching statistics and probability

### 2.2 Use Cases

**UC-1: Live Consciousness Experiment**

- Researcher sets up device during meditation sessions
- Application detects and visualizes statistical deviations
- Data is automatically recorded for later analysis
- Real-time feedback shows potential consciousness correlations

**UC-2: Historical Data Analysis**

- Researcher opens previously captured data files
- Application replays the bitstream with statistical analysis
- Comparison of different time periods or experimental conditions
- Export of anomaly reports for statistical software

**UC-3: Device Validation**

- Verify TrueRNG Pro V2 is operating correctly
- Continuous monitoring of randomness quality
- Detection of hardware issues or environmental interference
- Baseline establishment for experimental validity

---

## 3. Functional Requirements

### 3.1 Core Functionality

#### 3.1.1 Device Connection

- **REQ-001**: Auto-detect TrueRNG Pro V2 devices on common USB ports
- **REQ-002**: Support manual device path specification
- **REQ-003**: Handle device connection/disconnection gracefully
- **REQ-004**: Display device status and connection information
- **REQ-005**: Support multiple TrueRNG operating modes (Normal, Raw, Debug)

#### 3.1.2 Data Acquisition

- **REQ-006**: Stream data at device's maximum rate (>3.2 Mbits/s)
- **REQ-007**: Buffer data to prevent loss during processing
- **REQ-008**: Timestamp all incoming data with millisecond precision
- **REQ-009**: Handle USB communication errors and reconnection

#### 3.1.3 Statistical Analysis

- **REQ-010**: Implement sliding window analysis (configurable size)
- **REQ-011**: Perform frequency analysis (bit bias detection)
- **REQ-012**: Execute runs tests (pattern detection)
- **REQ-013**: Calculate chi-square tests for byte uniformity
- **REQ-014**: Generate z-scores and p-values for all tests
- **REQ-015**: Support configurable significance thresholds
- **REQ-016**: Detect multiple anomaly types simultaneously

#### 3.1.4 Visualization

- **REQ-017**: Display real-time horizontal scrolling bitstream
- **REQ-018**: Show statistical deviations as visual peaks/valleys
- **REQ-019**: Color-code anomalies by significance level
- **REQ-020**: Display current statistics (bit counts, ratios, etc.)
- **REQ-021**: Show device status and connection info
- **REQ-022**: Maintain 60+ FPS update rate for smooth visualization

#### 3.1.5 Data Storage

- **REQ-023**: Save raw bitstream data to CSV format
- **REQ-024**: Include metadata (timestamp, device info, settings)
- **REQ-025**: Store anomaly detection results
- **REQ-026**: Support incremental file saving during capture
- **REQ-027**: Compress large data files automatically

#### 3.1.6 File Playback

- **REQ-028**: Load and parse saved capture files
- **REQ-029**: Replay data with original timing or at custom speeds
- **REQ-030**: Navigate through large datasets efficiently
- **REQ-031**: Display same visualization as live mode
- **REQ-032**: Export anomaly reports and statistics

### 3.2 User Interface Requirements

#### 3.2.1 Command Line Interface

- **REQ-033**: Support `--live` mode with optional save path
- **REQ-034**: Support `--open` mode for file playback
- **REQ-035**: Interactive mode selection when no arguments provided
- **REQ-036**: `--device` parameter for manual device specification
- **REQ-037**: `--verbose` flag for detailed logging
- **REQ-038**: Help documentation accessible via `--help`

#### 3.2.2 Terminal User Interface

- **REQ-039**: Modern, responsive terminal UI using Textual framework
- **REQ-040**: Clear visual hierarchy with organized panels
- **REQ-041**: Real-time updating without screen flicker
- **REQ-042**: Keyboard shortcuts for common actions
- **REQ-043**: Status indicators for all major components
- **REQ-044**: Error messages and notifications system

#### 3.2.3 Visualization Design

- **REQ-045**: Horizontal wave visualization of bitstream
- **REQ-046**: Baseline indicator for normal randomness
- **REQ-047**: Anomaly markers with different symbols/colors:
  - `***` Red for 99.9% confidence (p < 0.001)
  - `**` Yellow for 99% confidence (p < 0.01)
  - `*` Light yellow for 95% confidence (p < 0.05)
- **REQ-048**: Smooth scrolling animation
- **REQ-049**: Configurable visualization parameters

### 3.3 Configuration and Settings

#### 3.3.1 Analysis Parameters

- **REQ-050**: Configurable window size (default: 1000 bytes)
- **REQ-051**: Adjustable significance threshold (default: p < 0.01)
- **REQ-052**: Selectable statistical tests to perform
- **REQ-053**: Update rate configuration
- **REQ-054**: Settings persistence between sessions

#### 3.3.2 Device Settings

- **REQ-055**: TrueRNG mode selection (Normal, Raw Binary, Raw ASCII)
- **REQ-056**: Baud rate configuration
- **REQ-057**: USB timeout settings
- **REQ-058**: Connection retry parameters

---

## 4. Non-Functional Requirements

### 4.1 Performance

- **REQ-059**: Process data in real-time without lag
- **REQ-060**: Memory usage < 500MB for 24-hour captures
- **REQ-061**: CPU usage < 25% on modern hardware
- **REQ-062**: Startup time < 3 seconds
- **REQ-063**: File loading time < 10 seconds for 1GB files

### 4.2 Reliability

- **REQ-064**: 99.9% uptime during continuous operation
- **REQ-065**: Graceful handling of all error conditions
- **REQ-066**: Data integrity verification and validation
- **REQ-067**: Automatic recovery from device disconnections
- **REQ-068**: No data loss during normal operation

### 4.3 Usability

- **REQ-069**: Intuitive interface requiring minimal training
- **REQ-070**: Comprehensive error messages with solutions
- **REQ-071**: Progressive disclosure of advanced features
- **REQ-072**: Consistent behavior across platforms
- **REQ-073**: Accessible to users with disabilities

### 4.4 Compatibility

- **REQ-074**: Python 3.13+ support
- **REQ-075**: Linux, macOS, and Windows compatibility
- **REQ-076**: USB 2.0/3.0 support
- **REQ-077**: TrueRNG Pro V2 and V3 compatibility
- **REQ-078**: Terminal emulator compatibility

### 4.5 Security

- **REQ-079**: No network communication (air-gapped operation)
- **REQ-080**: Secure file permissions for saved data
- **REQ-081**: No logging of sensitive information
- **REQ-082**: Input validation for all user data

---

## 5. Technical Architecture

### 5.1 System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   TrueRNG Pro   │────│  Device Driver   │────│  Application    │
│      V2         │    │   (USB Serial)   │    │   Interface     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                       ┌─────────────────────────────────┼─────────────────┐
                       │                                 │                 │
                ┌──────▼──────┐    ┌──────────────┐    ┌▼────────────┐    │
                │   Data      │    │  Statistical │    │    User     │    │
                │ Acquisition │    │   Analysis   │    │ Interface   │    │
                └─────────────┘    └──────────────┘    └─────────────┘    │
                       │                   │                   │          │
                ┌──────▼──────────────────▼───────────────────▼──────────┐
                │              Data Storage & Management               │
                └─────────────────────────────────────────────────────┘
```

### 5.2 Module Design

#### 5.2.1 Device Interface (`rng_viz.device`)

- **TrueRNGDevice**: Main device connection class
- **DeviceInfo**: Device detection and information
- **TrueRNGMode**: Operating mode enumeration
- Handles USB communication, buffering, and error recovery

#### 5.2.2 Statistical Analysis (`rng_viz.analysis`)

- **RandomnessAnalyzer**: Main analysis engine
- **StatisticalWindow**: Sliding window implementation
- **AnomalyResult**: Statistical test results
- Implements frequency, runs, and chi-square tests

#### 5.2.3 User Interface (`rng_viz.ui`)

- **RNGVisualizerApp**: Main Textual application
- **BitstreamVisualizer**: Real-time wave visualization
- **StatsDisplay**: Statistics panel
- **DeviceStatus**: Device information panel

#### 5.2.4 Data Management (`rng_viz.data`)

- **BitstreamWriter**: CSV file output
- **BitstreamReader**: File loading and parsing
- **CaptureMetadata**: Session information
- **BitstreamRecord**: Individual data points

### 5.3 Data Flow

1. **Device Connection**: USB enumeration and TrueRNG detection
2. **Data Acquisition**: Continuous byte stream reading
3. **Buffering**: Queue management for real-time processing
4. **Analysis**: Statistical tests on sliding windows
5. **Visualization**: Real-time UI updates with anomaly highlighting
6. **Storage**: Continuous writing to CSV files
7. **Playback**: File reading and visualization replay

---

## 6. Implementation Plan

### 6.1 Development Phases

#### Phase 1: Core Infrastructure (Completed)

- ✅ Project setup with uv and pyproject.toml
- ✅ Basic module structure
- ✅ TrueRNG device interface
- ✅ Statistical analysis framework
- ✅ Data storage system
- ✅ Basic Textual UI

#### Phase 2: Integration and Testing

- Device connection testing on multiple platforms
- Statistical analysis validation
- UI responsiveness optimization
- Error handling implementation
- Performance testing and optimization

#### Phase 3: Advanced Features

- Configuration system
- Multiple device support
- Advanced statistical tests
- Export functionality
- Documentation completion

#### Phase 4: Polish and Release

- User testing and feedback
- Bug fixes and optimizations
- Installation packages
- User documentation
- Release preparation

### 6.2 Testing Strategy

#### 6.2.1 Unit Testing

- Device interface mocking
- Statistical algorithm validation
- Data storage integrity
- UI component testing

#### 6.2.2 Integration Testing

- End-to-end data flow
- Real device testing
- Performance under load
- Error condition handling

#### 6.2.3 User Testing

- Usability studies with target users
- Documentation clarity
- Installation process validation
- Cross-platform compatibility

---

## 7. Future Enhancements

### 7.1 Advanced Analytics

- Machine learning anomaly detection
- Frequency domain analysis
- Multiple time scale analysis
- Correlation with external events

### 7.2 Collaboration Features

- Network data sharing
- Multi-site experiments
- Real-time collaboration
- Data synchronization

### 7.3 Visualization Improvements

- 3D visualization options
- Historical trend analysis
- Comparative visualizations
- Custom chart types

### 7.4 Platform Extensions

- Web interface
- Mobile applications
- Cloud integration
- API development

---

## 8. Success Criteria

### 8.1 Technical Success

- ✅ Successful device connection and data acquisition
- ✅ Real-time statistical analysis implementation
- ✅ Responsive and intuitive user interface
- Reliable data storage and retrieval
- Cross-platform compatibility

### 8.2 User Success

- Positive feedback from consciousness researchers
- Adoption by GCP-style research groups
- Documentation rated as clear and comprehensive
- Successful replication of known statistical patterns
- Community contributions and extensions

### 8.3 Business Success

- Open source community engagement
- Educational institution adoption
- Research publication citations
- Professional recommendation and endorsement
- Sustainable maintenance and development model

---

## 9. Appendices

### 9.1 Glossary

- **Anomaly**: Statistical deviation from expected random behavior
- **Bitstream**: Continuous sequence of binary data
- **GCP**: Global Consciousness Project
- **RNG**: Random Number Generator
- **Significance Level**: Statistical confidence threshold
- **TrueRNG Pro V2**: Hardware random number generator device
- **Z-score**: Number of standard deviations from the mean

### 9.2 References

- [TrueRNG Pro V2 Technical Documentation](https://ubld.it/products/truerngprov2)
- [Global Consciousness Project Methodology](https://noosphere.princeton.edu/)
- [NIST Statistical Test Suite](https://csrc.nist.gov/projects/random-bit-generation)
- [Textual Framework Documentation](https://textual.textualize.io/)

### 9.3 Change Log

- **v1.0**: Initial PRD creation with complete specification
- **v0.1**: Basic project structure and requirements definition
