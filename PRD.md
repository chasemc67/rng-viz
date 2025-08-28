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

**UC-3: Interactive Consciousness Game**

- User engages in real-time consciousness interaction experiment
- System provides randomized instructions ("Generate more 1's" or "Generate more 0's")
- Turn-based scoring tracks anomaly distribution across 6 categories
- Session replay capability for analysis of consciousness correlation patterns
- Statistical analysis of intention vs. actual RNG bias

**UC-4: Device Validation**

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

#### 3.1.7 Game Mode Functionality

- **REQ-033A**: Generate random instructions ("Generate more 1's" or "Generate more 0's")
- **REQ-033B**: Implement random turn duration between 10-30 seconds
- **REQ-033C**: Categorize anomalies into 6 buckets (Red/Orange/Yellow × Up/Down)
- **REQ-033D**: Track scoring per turn in real-time
- **REQ-033E**: Maintain history of all completed turns
- **REQ-033F**: Calculate overall statistics across all turns
- **REQ-033G**: Support manual game completion via keyboard shortcut
- **REQ-033H**: Enable game session replay with full game interface

### 3.2 User Interface Requirements

#### 3.2.1 Command Line Interface

- **REQ-040**: Support `--live` mode with optional save path
- **REQ-041**: Support `--open` mode for file playback
- **REQ-042**: Interactive mode selection when no arguments provided
- **REQ-043**: `--device` parameter for manual device specification
- **REQ-044**: `--verbose` flag for detailed logging
- **REQ-045**: Help documentation accessible via `--help`
- **REQ-046**: Support `--game` mode for consciousness interaction experiments
- **REQ-047**: Support `--open-game` mode for game session replay

#### 3.2.2 Terminal User Interface

- **REQ-048**: Modern, responsive terminal UI using Textual framework
- **REQ-049**: Clear visual hierarchy with organized panels
- **REQ-050**: Real-time updating without screen flicker
- **REQ-051**: Keyboard shortcuts for common actions
- **REQ-052**: Status indicators for all major components
- **REQ-053**: Error messages and notifications system

#### 3.2.3 Visualization Design

- **REQ-054**: Horizontal wave visualization of bitstream
- **REQ-055**: Baseline indicator for normal randomness
- **REQ-056**: Anomaly markers with different symbols/colors:
  - `***` Red for 99.9% confidence (p < 0.001)
  - `**` Yellow for 99% confidence (p < 0.01)
  - `*` Light yellow for 95% confidence (p < 0.05)
- **REQ-057**: Smooth scrolling animation
- **REQ-058**: Configurable visualization parameters

#### 3.2.4 Game Mode User Interface

- **REQ-059**: Display current instruction ("Generate more 1's" / "Generate more 0's") prominently
- **REQ-060**: Show countdown timer for current turn
- **REQ-061**: Display current turn bucket scores with visual emphasis
- **REQ-062**: Maintain scrollable history of completed turns
- **REQ-063**: Show overall game statistics when finished
- **REQ-064**: Support finish game keyboard shortcut (F key)

### 3.3 Configuration and Settings

#### 3.3.1 Analysis Parameters

- **REQ-065**: Configurable window size (default: 1000 bytes)
- **REQ-066**: Adjustable significance threshold (default: p < 0.01)
- **REQ-067**: Selectable statistical tests to perform
- **REQ-068**: Update rate configuration
- **REQ-069**: Settings persistence between sessions

#### 3.3.2 Device Settings

- **REQ-070**: TrueRNG mode selection (Normal, Raw Binary, Raw ASCII)
- **REQ-071**: Baud rate configuration
- **REQ-072**: USB timeout settings
- **REQ-073**: Connection retry parameters

#### 3.3.3 Game Mode Settings

- **REQ-074**: Configurable turn duration range (default: 10-30 seconds)
- **REQ-075**: Customizable instruction set for consciousness experiments
- **REQ-076**: Adjustable significance levels for bucket categorization

---

## 4. Non-Functional Requirements

### 4.1 Performance

- **REQ-077**: Process data in real-time without lag
- **REQ-078**: Memory usage < 500MB for 24-hour captures
- **REQ-079**: CPU usage < 25% on modern hardware
- **REQ-080**: Startup time < 3 seconds
- **REQ-081**: File loading time < 10 seconds for 1GB files

### 4.2 Reliability

- **REQ-082**: 99.9% uptime during continuous operation
- **REQ-083**: Graceful handling of all error conditions
- **REQ-084**: Data integrity verification and validation
- **REQ-085**: Automatic recovery from device disconnections
- **REQ-086**: No data loss during normal operation

### 4.3 Usability

- **REQ-087**: Intuitive interface requiring minimal training
- **REQ-088**: Comprehensive error messages with solutions
- **REQ-089**: Progressive disclosure of advanced features
- **REQ-090**: Consistent behavior across platforms
- **REQ-091**: Accessible to users with disabilities

### 4.4 Compatibility

- **REQ-092**: Python 3.13+ support
- **REQ-093**: Linux, macOS, and Windows compatibility
- **REQ-094**: USB 2.0/3.0 support
- **REQ-095**: TrueRNG Pro V2 and V3 compatibility
- **REQ-096**: Terminal emulator compatibility

### 4.5 Security

- **REQ-097**: No network communication (air-gapped operation)
- **REQ-098**: Secure file permissions for saved data
- **REQ-099**: No logging of sensitive information
- **REQ-100**: Input validation for all user data

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
- ✅ Game mode implementation with turn-based anomaly tracking
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

- **v1.1**: Added game mode functionality for consciousness interaction experiments
- **v1.0**: Initial PRD creation with complete specification
- **v0.1**: Basic project structure and requirements definition
